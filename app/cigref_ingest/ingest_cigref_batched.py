"""
CIGREF Knowledge Base Batch Ingestion Script

Part of lightrag-cv application workflows.
Module: app.cigref_ingest.ingest_cigref_batched

This script implements batch processing to avoid LLM timeout issues during entity extraction.
It splits the CIGREF data into smaller batches and processes each independently.

Strategy:
- Split 681 source chunks into batches of configurable size
- Each batch processes independently to avoid timeouts
- Progress tracked across all batches
- Resume capability from specific batch or chunk ID

Usage:
    # Process all chunks in batches of 5
    python -m app.cigref_ingest.ingest_cigref_batched --batch-size 5

    # Resume from batch 10
    python -m app.cigref_ingest.ingest_cigref_batched --start-batch 10

    # Start from specific chunk ID (e.g., chunk_37)
    python -m app.cigref_ingest.ingest_cigref_batched --chunk-start chunk_37

    # Combine chunk start with custom batch size
    python -m app.cigref_ingest.ingest_cigref_batched --chunk-start chunk_37 --batch-size 10
"""

import asyncio
import json
import logging
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import psycopg
from psycopg.rows import dict_row

# Import centralized configuration (RULE 2: All Environment Variables via config.py)
from app.shared.config import settings

# Configuration constants
CIGREF_DATA_PATH = settings.CIGREF_PARSED_FILE
LIGHTRAG_URL = settings.lightrag_url
POSTGRES_DSN = settings.postgres_dsn
INGESTION_TIMEOUT = int(settings.INGESTION_TIMEOUT)
BATCH_SIZE = settings.DEFAULT_BATCH_SIZE
MAX_RETRIES = settings.MAX_RETRIES

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(".ai/cigref-batch-ingestion.log")
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class BatchMetrics:
    """Metrics for a single batch."""
    batch_number: int
    source_chunks: int
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    processing_time: float = 0.0
    lightrag_chunks: int = 0
    entities: int = 0
    relations: int = 0
    status: str = "pending"  # pending, processing, completed, failed
    error: Optional[str] = None

    def mark_completed(self, lightrag_chunks: int, entities: int, relations: int):
        """Mark batch as completed with results."""
        self.end_time = time.time()
        self.processing_time = self.end_time - self.start_time
        self.lightrag_chunks = lightrag_chunks
        self.entities = entities
        self.relations = relations
        self.status = "completed"

    def mark_failed(self, error: str):
        """Mark batch as failed with error."""
        self.end_time = time.time()
        self.processing_time = self.end_time - self.start_time
        self.status = "failed"
        self.error = error


@dataclass
class OverallMetrics:
    """Overall metrics across all batches."""
    total_batches: int
    total_source_chunks: int
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    batches: List[BatchMetrics] = field(default_factory=list)

    @property
    def completed_batches(self) -> int:
        return sum(1 for b in self.batches if b.status == "completed")

    @property
    def failed_batches(self) -> int:
        return sum(1 for b in self.batches if b.status == "failed")

    @property
    def total_lightrag_chunks(self) -> int:
        return sum(b.lightrag_chunks for b in self.batches if b.status == "completed")

    @property
    def total_entities(self) -> int:
        return sum(b.entities for b in self.batches if b.status == "completed")

    @property
    def total_relations(self) -> int:
        return sum(b.relations for b in self.batches if b.status == "completed")

    @property
    def total_processing_time(self) -> float:
        return sum(b.processing_time for b in self.batches)


def split_into_batches(chunks: List[Dict[str, Any]], batch_size: int) -> List[List[Dict[str, Any]]]:
    """Split chunks into batches of specified size."""
    batches = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        batches.append(batch)
    return batches


async def insert_document_metadata(document_metadata: Dict[str, Any], batch_number: int) -> None:
    """Insert document metadata into PostgreSQL."""
    async with await psycopg.AsyncConnection.connect(POSTGRES_DSN, row_factory=dict_row) as conn:
        async with conn.cursor() as cur:
            # Create batch-specific document ID
            original_doc_id = document_metadata["document_id"]
            batch_doc_id = f"{original_doc_id}_batch_{batch_number}"

            await cur.execute("""
                INSERT INTO document_metadata (
                    document_id, document_type, source_filename, file_format,
                    cigref_profile_name, batch_number, original_document_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (document_id) DO UPDATE
                SET batch_number = EXCLUDED.batch_number,
                    original_document_id = EXCLUDED.original_document_id
            """, (
                batch_doc_id,
                "CIGREF_PROFILE_BATCH",
                document_metadata["source_filename"],
                document_metadata.get("format", "PDF"),
                f"CIGREF_IT_Profiles_2024_Batch_{batch_number}",
                batch_number,
                original_doc_id
            ))
            await conn.commit()

    logger.info(f"Batch {batch_number}: Document metadata inserted")


async def submit_batch_to_lightrag(batch_chunks: List[Dict[str, Any]], batch_number: int) -> str:
    """Submit a batch of chunks to LightRAG for processing with metadata preservation."""

    # Prepare texts with embedded metadata
    texts = []
    file_sources = []

    for chunk in batch_chunks:
        # Extract metadata
        metadata = chunk.get("metadata", {})
        chunk_id = chunk.get("chunk_id", "unknown")

        # Build metadata header
        metadata_lines = [
            f"[CHUNK_ID: {chunk_id}]",
            f"[PAGE: {metadata.get('page', 'N/A')}]",
        ]

        # Add optional metadata fields if present
        if metadata.get("section"):
            metadata_lines.append(f"[SECTION: {metadata['section']}]")
        if metadata.get("domain"):
            metadata_lines.append(f"[DOMAIN: {metadata['domain']}]")
        if metadata.get("job_profile"):
            metadata_lines.append(f"[JOB_PROFILE: {metadata['job_profile']}]")

        # Combine metadata header with content
        text_with_metadata = "\n".join(metadata_lines) + "\n\n" + chunk["content"]
        texts.append(text_with_metadata)

        # Create descriptive file source for each chunk
        file_sources.append(f"cigref_batch_{batch_number}_{chunk_id}")

    # Use /documents/texts (plural) endpoint to preserve chunk boundaries
    payload = {
        "texts": texts,
        "file_sources": file_sources
    }

    async with httpx.AsyncClient(timeout=INGESTION_TIMEOUT) as client:
        response = await client.post(
            f"{LIGHTRAG_URL}/documents/texts",
            json=payload
        )
        response.raise_for_status()
        result = response.json()

    logger.info(f"Batch {batch_number}: Submitted to LightRAG ({len(batch_chunks)} chunks with metadata)")
    return f"cigref_batch_{batch_number}"


async def monitor_batch_processing(batch_number: int, timeout: int = 600) -> bool:
    """Monitor the processing status of a batch."""
    start_time = time.time()
    check_interval = 10  # seconds

    # Wait 2 seconds before first check to allow LightRAG to start processing
    await asyncio.sleep(2)

    async with httpx.AsyncClient(timeout=30) as client:
        processing_started = False

        while time.time() - start_time < timeout:
            try:
                response = await client.get(f"{LIGHTRAG_URL}/documents/pipeline_status")
                response.raise_for_status()
                status = response.json()

                is_busy = status.get("busy", False)

                # Track if processing has started
                if is_busy:
                    processing_started = True

                # Only consider complete if we saw it start processing
                if not is_busy and processing_started:
                    logger.info(f"Batch {batch_number}: Processing completed")
                    # Additional wait to ensure data is committed
                    await asyncio.sleep(2)
                    return True

                # Log progress when busy
                if is_busy:
                    message = status.get("latest_message", "")
                    if message:
                        logger.debug(f"Batch {batch_number}: {message[:100]}")

            except Exception as e:
                logger.warning(f"Batch {batch_number}: Status check failed: {e}")

            await asyncio.sleep(check_interval)

    raise TimeoutError(f"Batch {batch_number}: Processing timeout after {timeout} seconds")


async def get_batch_results(batch_number: int) -> tuple[int, int, int]:
    """Query database for batch processing results."""
    async with await psycopg.AsyncConnection.connect(POSTGRES_DSN, row_factory=dict_row) as conn:
        async with conn.cursor() as cur:
            # Get chunk count
            await cur.execute("""
                SELECT COUNT(*) as count
                FROM lightrag_vdb_chunks
                WHERE workspace = 'default'
                AND file_path LIKE %s
            """, (f"%batch_{batch_number}%",))
            chunks_result = await cur.fetchone()
            chunks = chunks_result["count"] if chunks_result else 0

            # Get entity count
            await cur.execute("""
                SELECT COUNT(*) as count
                FROM lightrag_full_entities
                WHERE workspace = 'default'
            """)
            entities_result = await cur.fetchone()
            entities = entities_result["count"] if entities_result else 0

            # Get relation count
            await cur.execute("""
                SELECT COUNT(*) as count
                FROM lightrag_full_relations
                WHERE workspace = 'default'
            """)
            relations_result = await cur.fetchone()
            relations = relations_result["count"] if relations_result else 0

    return chunks, entities, relations


async def process_batch(
    batch_chunks: List[Dict[str, Any]],
    batch_number: int,
    document_metadata: Dict[str, Any],
    metrics: BatchMetrics
) -> None:
    """Process a single batch of chunks."""
    logger.info("=" * 80)
    logger.info(f"BATCH {batch_number}/{metrics.total_batches} - STARTED")
    logger.info(f"Source chunks: {len(batch_chunks)}")
    logger.info("=" * 80)

    metrics.status = "processing"

    try:
        # Step 1: Insert metadata
        await insert_document_metadata(document_metadata, batch_number)

        # Step 2: Submit to LightRAG
        file_source = await submit_batch_to_lightrag(batch_chunks, batch_number)

        # Step 3: Monitor processing
        await monitor_batch_processing(batch_number, timeout=INGESTION_TIMEOUT)

        # Step 4: Get results
        chunks, entities, relations = await get_batch_results(batch_number)

        # Warn if no chunks were created (indicates processing issue)
        if chunks == 0:
            logger.warning(f"Batch {batch_number}: WARNING - No chunks created! This may indicate a processing failure.")

        # Mark as completed
        metrics.mark_completed(chunks, entities, relations)

        logger.info("=" * 80)
        logger.info(f"BATCH {batch_number}/{metrics.total_batches} - COMPLETED")
        logger.info(f"Processing time: {metrics.processing_time:.1f}s")
        logger.info(f"LightRAG chunks: {chunks}")
        logger.info(f"Entities: {entities}")
        logger.info(f"Relations: {relations}")
        logger.info("=" * 80)

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        metrics.mark_failed(error_msg)
        logger.error(f"BATCH {batch_number} FAILED: {error_msg}")
        raise


async def main(batch_size: int = BATCH_SIZE, start_batch: int = 1, chunk_start: Optional[str] = None):
    """Main batch ingestion workflow."""
    logger.info("=" * 80)
    logger.info("CIGREF BATCH INGESTION - STARTED")
    logger.info("=" * 80)

    # Load CIGREF data
    with open(CIGREF_DATA_PATH, "r") as f:
        cigref_data = json.load(f)

    document_metadata = cigref_data["document_metadata"]
    all_chunks = cigref_data["chunks"]

    # Filter chunks if chunk_start is specified
    if chunk_start:
        # Find the starting index
        start_index = None
        for idx, chunk in enumerate(all_chunks):
            if chunk.get("chunk_id") == chunk_start:
                start_index = idx
                break

        if start_index is None:
            logger.error(f"Chunk ID '{chunk_start}' not found in source data")
            logger.error(f"Available chunk IDs: {[c.get('chunk_id') for c in all_chunks[:5]]} ... {[c.get('chunk_id') for c in all_chunks[-5:]]}")
            return False

        logger.info(f"Starting from chunk '{chunk_start}' (index {start_index})")
        logger.info(f"Skipping first {start_index} chunks")
        all_chunks = all_chunks[start_index:]

    # Split into batches
    batches = split_into_batches(all_chunks, batch_size)

    # Initialize metrics
    overall_metrics = OverallMetrics(
        total_batches=len(batches),
        total_source_chunks=len(all_chunks)
    )

    logger.info(f"Total source chunks: {len(all_chunks)}")
    logger.info(f"Batch size: {batch_size}")
    logger.info(f"Total batches: {len(batches)}")
    logger.info(f"Starting from batch: {start_batch}")
    logger.info("=" * 80)

    # Process each batch
    for batch_num, batch_chunks in enumerate(batches, start=1):
        if batch_num < start_batch:
            logger.info(f"Skipping batch {batch_num} (already processed)")
            continue

        batch_metrics = BatchMetrics(
            batch_number=batch_num,
            source_chunks=len(batch_chunks)
        )
        batch_metrics.total_batches = len(batches)
        overall_metrics.batches.append(batch_metrics)

        try:
            await process_batch(batch_chunks, batch_num, document_metadata, batch_metrics)
        except Exception as e:
            logger.error(f"Batch {batch_num} failed, continuing with next batch...")
            continue

        # Small delay between batches
        if batch_num < len(batches):
            logger.info(f"Waiting 5 seconds before next batch...")
            await asyncio.sleep(5)

    # Final summary
    overall_metrics.end_time = time.time()
    total_time = overall_metrics.end_time - overall_metrics.start_time

    logger.info("=" * 80)
    logger.info("CIGREF BATCH INGESTION - COMPLETED")
    logger.info("=" * 80)
    logger.info(f"Total batches: {overall_metrics.total_batches}")
    logger.info(f"Completed: {overall_metrics.completed_batches}")
    logger.info(f"Failed: {overall_metrics.failed_batches}")
    logger.info(f"Total source chunks: {overall_metrics.total_source_chunks}")
    logger.info(f"Total LightRAG chunks: {overall_metrics.total_lightrag_chunks}")
    logger.info(f"Total entities: {overall_metrics.total_entities}")
    logger.info(f"Total relations: {overall_metrics.total_relations}")
    logger.info(f"Total time: {total_time / 60:.1f} minutes")
    logger.info(f"Average per batch: {overall_metrics.total_processing_time / len(batches):.1f}s")
    logger.info("=" * 80)

    # Write summary to file
    summary_path = Path(".ai/cigref-batch-ingestion-summary.json")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w") as f:
        json.dump({
            "overall": {
                "total_batches": overall_metrics.total_batches,
                "completed_batches": overall_metrics.completed_batches,
                "failed_batches": overall_metrics.failed_batches,
                "total_source_chunks": overall_metrics.total_source_chunks,
                "total_lightrag_chunks": overall_metrics.total_lightrag_chunks,
                "total_entities": overall_metrics.total_entities,
                "total_relations": overall_metrics.total_relations,
                "total_time_seconds": total_time,
                "average_per_batch_seconds": overall_metrics.total_processing_time / len(batches)
            },
            "batches": [
                {
                    "batch_number": b.batch_number,
                    "source_chunks": b.source_chunks,
                    "lightrag_chunks": b.lightrag_chunks,
                    "entities": b.entities,
                    "relations": b.relations,
                    "processing_time": b.processing_time,
                    "status": b.status,
                    "error": b.error
                }
                for b in overall_metrics.batches
            ]
        }, f, indent=2)

    logger.info(f"Summary written to: {summary_path}")

    return overall_metrics.failed_batches == 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="CIGREF Batch Ingestion",
        epilog="Examples:\n"
               "  # Process all chunks in batches of 5\n"
               "  python3 scripts/ingest-cigref-batched.py --batch-size 5\n\n"
               "  # Resume from batch 10\n"
               "  python3 scripts/ingest-cigref-batched.py --start-batch 10\n\n"
               "  # Start from specific chunk ID\n"
               "  python3 scripts/ingest-cigref-batched.py --chunk-start chunk_37\n\n"
               "  # Start from chunk_37 with batch size 10\n"
               "  python3 scripts/ingest-cigref-batched.py --chunk-start chunk_37 --batch-size 10",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help="Source chunks per batch")
    parser.add_argument("--start-batch", type=int, default=1, help="Starting batch number (for resume)")
    parser.add_argument("--chunk-start", type=str, default=None,
                        help="Start from specific chunk ID (e.g., chunk_37). Overrides start-batch.")
    args = parser.parse_args()

    success = asyncio.run(main(
        batch_size=args.batch_size,
        start_batch=args.start_batch,
        chunk_start=args.chunk_start
    ))
    sys.exit(0 if success else 1)
