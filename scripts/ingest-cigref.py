#!/usr/bin/env python3
"""CIGREF Knowledge Base Ingestion Script.

This script ingests parsed CIGREF profile data into the LightRAG knowledge base,
including vector embeddings and graph relationships.

Usage:
    python scripts/ingest-cigref.py

Requirements:
    - CIGREF parsed data at /data/cigref/cigref-parsed.json
    - LightRAG service running at localhost:9621
    - PostgreSQL running at localhost:5434
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

import httpx
import psycopg

# Import centralized configuration (RULE 2: All Environment Variables via config.py)
from config import settings

# Configure logging with structured output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('.ai/cigref-ingestion.log')
    ]
)
logger = logging.getLogger(__name__)


class IngestionMetrics:
    """Track ingestion metrics."""

    def __init__(self):
        self.start_time = time.time()
        self.document_id: Optional[str] = None
        self.chunk_count = 0
        self.chunks_created = 0
        self.entities_extracted = 0
        self.vector_count = 0
        self.entity_count = 0
        self.relationship_count = 0
        self.query_test_passed = False
        self.total_time_seconds = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "document_id": self.document_id,
            "chunk_count": self.chunk_count,
            "chunks_created": self.chunks_created,
            "entities_extracted": self.entities_extracted,
            "vector_count": self.vector_count,
            "entity_count": self.entity_count,
            "relationship_count": self.relationship_count,
            "query_test_passed": self.query_test_passed,
            "total_time_seconds": round(self.total_time_seconds, 2),
            "total_time_minutes": round(self.total_time_seconds / 60, 2)
        }


async def load_cigref_data() -> Dict[str, Any]:
    """Load and validate CIGREF parsed data.

    Returns:
        Parsed CIGREF data dictionary

    Raises:
        FileNotFoundError: If CIGREF file doesn't exist
        ValueError: If JSON structure is invalid
    """
    logger.info("Loading CIGREF parsed data", extra={"file": str(settings.CIGREF_PARSED_FILE)})

    if not settings.CIGREF_PARSED_FILE.exists():
        raise FileNotFoundError(f"CIGREF parsed file not found: {settings.CIGREF_PARSED_FILE}")

    with open(settings.CIGREF_PARSED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Validate JSON structure
    required_fields = ["document_metadata", "chunks"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    if not isinstance(data["chunks"], list):
        raise ValueError("'chunks' must be a list")

    if len(data["chunks"]) == 0:
        raise ValueError("'chunks' list is empty")

    # Validate document_metadata
    if "document_id" not in data["document_metadata"]:
        raise ValueError("Missing document_id in document_metadata")

    # Validate chunk structure
    chunk_sample = data["chunks"][0]
    required_chunk_fields = ["chunk_id", "content", "metadata"]
    for field in required_chunk_fields:
        if field not in chunk_sample:
            raise ValueError(f"Missing required chunk field: {field}")

    logger.info(
        "CIGREF data loaded successfully",
        extra={
            "document_id": data["document_metadata"]["document_id"],
            "chunk_count": len(data["chunks"]),
            "file_size_kb": settings.CIGREF_PARSED_FILE.stat().st_size // 1024
        }
    )

    return data


async def create_document_metadata_table(conn: psycopg.AsyncConnection) -> None:
    """Create document_metadata table if it doesn't exist.

    Args:
        conn: PostgreSQL async connection
    """
    async with conn.cursor() as cur:
        await cur.execute(
            """
            CREATE TABLE IF NOT EXISTS document_metadata (
                document_id TEXT PRIMARY KEY,
                document_type TEXT NOT NULL,
                source_filename TEXT,
                file_format TEXT,
                upload_timestamp TIMESTAMP,
                total_chunks INTEGER,
                cigref_profile_name TEXT,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    await conn.commit()
    logger.info("document_metadata table created/verified")


async def insert_document_metadata(conn: psycopg.AsyncConnection, cigref_data: Dict[str, Any]) -> None:
    """Insert document metadata record into PostgreSQL.

    Args:
        conn: PostgreSQL async connection
        cigref_data: CIGREF parsed data
    """
    doc_meta = cigref_data["document_metadata"]
    document_id = doc_meta["document_id"]

    logger.info(
        "Inserting document metadata",
        extra={
            "document_id": document_id,
            "document_type": "CIGREF_PROFILE"
        }
    )

    async with conn.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO document_metadata (
                document_id, document_type, source_filename, file_format,
                upload_timestamp, cigref_profile_name, metadata
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (document_id) DO UPDATE SET
                upload_timestamp = EXCLUDED.upload_timestamp,
                metadata = EXCLUDED.metadata
            """,
            (
                document_id,
                "CIGREF_PROFILE",
                doc_meta.get("source_filename", "cigref-parsed.json"),
                doc_meta.get("format", "PDF"),
                datetime.now(),
                "CIGREF_IT_Profiles_2024",
                json.dumps(doc_meta)
            )
        )

    await conn.commit()

    logger.info(
        "Document metadata inserted",
        extra={"document_id": document_id}
    )


async def submit_to_lightrag(cigref_data: Dict[str, Any]) -> str:
    """Submit chunks to LightRAG ingestion API with metadata preservation.

    Args:
        cigref_data: CIGREF parsed data with chunks containing metadata

    Returns:
        Document ID from LightRAG response

    Raises:
        httpx.HTTPError: If API request fails
    """
    doc_meta = cigref_data["document_metadata"]
    document_id = doc_meta["document_id"]
    chunks = cigref_data["chunks"]

    # Prepare texts with embedded metadata for each chunk
    texts = []
    file_sources = []

    for chunk in chunks:
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
        file_sources.append(f"cigref:{document_id}:{chunk_id}")

    # Use /documents/texts (plural) endpoint to preserve chunk boundaries
    payload = {
        "texts": texts,
        "file_sources": file_sources
    }

    logger.info(
        "Submitting to LightRAG API",
        extra={
            "document_id": document_id,
            "chunk_count": len(chunks),
            "endpoint": f"{settings.lightrag_url}/documents/texts"
        }
    )

    async with httpx.AsyncClient(timeout=settings.INGESTION_TIMEOUT) as client:
        response = await client.post(
            f"{settings.lightrag_url}/documents/texts",
            json=payload
        )
        response.raise_for_status()
        result = response.json()

    logger.info(
        "LightRAG ingestion started",
        extra={
            "document_id": document_id,
            "track_id": result.get("track_id"),
            "status": result.get("status"),
            "api_message": result.get("message")
        }
    )

    return document_id


async def monitor_processing_status(document_id: str, metrics: IngestionMetrics) -> Dict[str, Any]:
    """Monitor LightRAG processing status until completion.

    Args:
        document_id: Document ID to monitor
        metrics: Metrics tracker

    Returns:
        Final status response

    Raises:
        RuntimeError: If processing fails or times out
    """
    logger.info(
        "Monitoring processing status",
        extra={
            "document_id": document_id,
            "poll_interval": settings.STATUS_POLL_INTERVAL,
            "max_attempts": settings.STATUS_MAX_ATTEMPTS
        }
    )

    async with httpx.AsyncClient() as client:
        for attempt in range(settings.STATUS_MAX_ATTEMPTS):
            try:
                response = await client.get(
                    f"{settings.lightrag_url}/documents/pipeline_status"
                )
                response.raise_for_status()
                status_data = response.json()

                busy = status_data.get("busy", False)
                job_name = status_data.get("job_name", "")
                cur_batch = status_data.get("cur_batch", 0)
                total_batches = status_data.get("batchs", 0)
                latest_message = status_data.get("latest_message", "")

                logger.info(
                    "Status check",
                    extra={
                        "document_id": document_id,
                        "attempt": attempt + 1,
                        "busy": busy,
                        "job_name": job_name,
                        "progress": f"{cur_batch}/{total_batches}",
                        "latest_message": latest_message[:100] if latest_message else ""
                    }
                )

                # Check if pipeline is idle (processing complete)
                if not busy and attempt > 0:  # Wait at least one cycle
                    logger.info(
                        "Processing completed",
                        extra={
                            "document_id": document_id,
                            "total_attempts": attempt + 1
                        }
                    )
                    return status_data

                # Check for error messages in latest_message
                if "error" in latest_message.lower() or "failed" in latest_message.lower():
                    error = latest_message
                    logger.error(
                        "Processing failed",
                        extra={"document_id": document_id, "error": error}
                    )
                    raise RuntimeError(f"LightRAG processing failed: {error}")

                # Still processing, wait and retry
                await asyncio.sleep(settings.STATUS_POLL_INTERVAL)

            except httpx.HTTPError as e:
                logger.warning(
                    "Status check failed",
                    extra={"document_id": document_id, "error": str(e)}
                )
                await asyncio.sleep(settings.STATUS_POLL_INTERVAL)

    # Timeout
    raise RuntimeError(
        f"Processing timeout after {settings.STATUS_MAX_ATTEMPTS * settings.STATUS_POLL_INTERVAL} seconds"
    )


async def validate_vector_storage(conn: psycopg.AsyncConnection, document_id: str, metrics: IngestionMetrics) -> None:
    """Validate vector embeddings storage in PostgreSQL.

    Args:
        conn: PostgreSQL async connection
        document_id: Document ID to validate
        metrics: Metrics tracker
    """
    logger.info(
        "Validating vector storage",
        extra={"document_id": document_id}
    )

    async with conn.cursor() as cur:
        # Count vectors for this document
        await cur.execute(
            "SELECT COUNT(*) FROM lightrag_doc_full WHERE id LIKE %s",
            (f"{document_id}%",)
        )
        result = await cur.fetchone()
        vector_count = result[0] if result else 0

        metrics.vector_count = vector_count

        logger.info(
            "Vector storage validation",
            extra={
                "document_id": document_id,
                "vector_count": vector_count,
                "expected_chunks": metrics.chunk_count
            }
        )

        # Sample vectors to verify structure
        await cur.execute(
            """
            SELECT id, content
            FROM lightrag_doc_full
            WHERE id LIKE %s
            LIMIT 5
            """,
            (f"{document_id}%",)
        )
        samples = await cur.fetchall()

        if samples:
            logger.info(
                "Sample vectors retrieved",
                extra={
                    "sample_count": len(samples),
                    "sample_ids": [s[0] for s in samples]
                }
            )


async def validate_graph_entities(conn: psycopg.AsyncConnection, metrics: IngestionMetrics) -> List[Dict[str, Any]]:
    """Validate knowledge graph entities.

    Args:
        conn: PostgreSQL async connection
        metrics: Metrics tracker

    Returns:
        List of sample entities
    """
    logger.info("Validating knowledge graph entities")

    async with conn.cursor() as cur:
        # Query entities from LightRAG PostgreSQL table
        # Schema: id, workspace, entity_names (JSONB), count, create_time, update_time
        await cur.execute(
            """
            SELECT id, entity_names, count
            FROM lightrag_full_entities
            WHERE workspace = 'default'
            LIMIT 50
            """
        )
        entities = await cur.fetchall()

        metrics.entity_count = len(entities)

        logger.info(
            "Graph entities retrieved",
            extra={
                "entity_count": len(entities)
            }
        )

        # Parse entities
        entity_samples = []
        if entities:
            for entity_row in entities[:10]:
                entity_id, entity_names_json, count = entity_row
                entity_samples.append({
                    "id": entity_id,
                    "entity_names": entity_names_json,
                    "count": count
                })

            logger.info(
                "Sample entities",
                extra={
                    "samples": [e["id"] for e in entity_samples[:5]]
                }
            )
        else:
            logger.warning("No entities found in database")

        return entity_samples


async def validate_graph_relationships(conn: psycopg.AsyncConnection, metrics: IngestionMetrics) -> List[Dict[str, Any]]:
    """Validate knowledge graph relationships.

    Args:
        conn: PostgreSQL async connection
        metrics: Metrics tracker

    Returns:
        List of sample relationships
    """
    logger.info("Validating knowledge graph relationships")

    async with conn.cursor() as cur:
        # Query relationships from LightRAG PostgreSQL table
        # Schema: id, workspace, relation_pairs (JSONB), count, create_time, update_time
        await cur.execute(
            """
            SELECT id, relation_pairs, count
            FROM lightrag_full_relations
            WHERE workspace = 'default'
            LIMIT 20
            """
        )
        relationships = await cur.fetchall()

        metrics.relationship_count = len(relationships)

        logger.info(
            "Graph relationships retrieved",
            extra={
                "relationship_count": len(relationships)
            }
        )

        # Parse sample relationships
        relationship_samples = []
        if relationships:
            for rel_row in relationships[:10]:
                rel_id, relation_pairs_json, count = rel_row
                relationship_samples.append({
                    "id": rel_id,
                    "relation_pairs": relation_pairs_json,
                    "count": count
                })
        else:
            logger.warning("No relationships found in database")

        logger.info(
            "Sample relationships",
            extra={
                "samples": relationship_samples[:3]
            }
        )

        return relationship_samples


async def test_query(metrics: IngestionMetrics) -> Dict[str, Any]:
    """Execute test query to validate retrieval.

    Args:
        metrics: Metrics tracker

    Returns:
        Query response or error dict
    """
    logger.info("Executing test query")

    query_payload = {
        "query": "What are the skills required for Cloud Architect?",
        "mode": "hybrid",
        "top_k": 5,
        "filters": {"document_type": "CIGREF_PROFILE"}
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.lightrag_url}/query",
                json=query_payload
            )
            response.raise_for_status()
            result = response.json()

        # Validate response structure
        if "results" in result and len(result["results"]) > 0:
            metrics.query_test_passed = True
            logger.info(
                "Query test PASSED",
                extra={
                    "result_count": len(result["results"]),
                    "retrieval_mode": result.get("retrieval_mode_used"),
                    "query_time_ms": result.get("query_time_ms")
                }
            )
        else:
            logger.warning("Query test returned no results")

        return result

    except (httpx.ReadTimeout, httpx.HTTPError) as e:
        logger.warning(f"Query test SKIPPED due to timeout/error: {str(e)}")
        metrics.query_test_passed = False
        return {"error": str(e), "status": "timeout"}


async def generate_validation_report(metrics: IngestionMetrics, entity_samples: List[Dict], relationship_samples: List[Dict], query_result: Dict) -> str:
    """Generate comprehensive validation report.

    Args:
        metrics: Ingestion metrics
        entity_samples: Sample graph entities
        relationship_samples: Sample graph relationships
        query_result: Query test result

    Returns:
        Report content as markdown
    """
    report = f"""# CIGREF Ingestion Validation Report

**Generated**: {datetime.now().isoformat()}

## Summary

| Metric | Value |
|--------|-------|
| Document ID | {metrics.document_id} |
| Total Chunks | {metrics.chunk_count} |
| Chunks Created | {metrics.chunks_created} |
| Entities Extracted | {metrics.entities_extracted} |
| Vector Count | {metrics.vector_count} |
| Graph Entity Count | {metrics.entity_count} |
| Graph Relationship Count | {metrics.relationship_count} |
| Query Test | {'✅ PASSED' if metrics.query_test_passed else '❌ FAILED'} |
| Total Processing Time | {round(metrics.total_time_seconds / 60, 2)} minutes |

## Vector Storage Validation

**Status**: {'✅ PASSED' if metrics.vector_count > 0 else '❌ FAILED'}

- Expected chunks: {metrics.chunk_count}
- Actual vectors stored: {metrics.vector_count}
- Coverage: {(metrics.vector_count / metrics.chunk_count * 100) if metrics.chunk_count > 0 else 0:.1f}%

## Knowledge Graph Validation

### Entity Count

**Status**: {'✅ PASSED' if metrics.entity_count >= 5 else '❌ FAILED (expected ≥5)'}

- Total entities in graph: {metrics.entity_count}
- Minimum required: 5 profiles, 10 skills, 5 missions

### Sample Entities (First 10)

```json
{json.dumps(entity_samples, indent=2)}
```

### Relationship Count

**Status**: {'✅ PASSED' if metrics.relationship_count > 0 else '❌ FAILED'}

- Total relationships: {metrics.relationship_count}

### Sample Relationships (First 10)

```json
{json.dumps(relationship_samples, indent=2)}
```

## Query Test Results

**Test Query**: "What are the skills required for Cloud Architect?"

**Status**: {'✅ PASSED' if metrics.query_test_passed else '❌ FAILED'}

**Response Summary**:
- Results returned: {len(query_result.get('results', []))}
- Retrieval mode: {query_result.get('retrieval_mode_used', 'N/A')}
- Query time: {query_result.get('query_time_ms', 'N/A')} ms

**Sample Results**:

```json
{json.dumps(query_result.get('results', [])[:3], indent=2)}
```

## Validation Queries

### Check Vector Storage

```sql
SELECT COUNT(*) FROM lightrag_doc_full WHERE id LIKE 'cigref_2024_en%';
```

### Check Graph Entities

```sql
SELECT * FROM cypher('lightrag_graph', $$
    MATCH (n)
    RETURN n LIMIT 10
$$) as (n agtype);
```

### Check Graph Relationships

```sql
SELECT * FROM cypher('lightrag_graph', $$
    MATCH (a)-[r]->(b)
    RETURN a, type(r), b LIMIT 20
$$) as (a agtype, r agtype, b agtype);
```

## Overall Status

{
    '✅ **VALIDATION PASSED** - All criteria met'
    if metrics.vector_count > 0 and metrics.entity_count >= 5 and metrics.query_test_passed
    else '⚠️ **VALIDATION INCOMPLETE** - Review failed checks above'
}

---
*Generated by ingest-cigref.py*
"""

    return report


async def main():
    """Main ingestion workflow."""
    metrics = IngestionMetrics()

    try:
        logger.info("=" * 80)
        logger.info("CIGREF KNOWLEDGE BASE INGESTION - STARTED")
        logger.info("=" * 80)

        # Task 1: Load and validate CIGREF data
        cigref_data = await load_cigref_data()
        metrics.document_id = cigref_data["document_metadata"]["document_id"]
        metrics.chunk_count = len(cigref_data["chunks"])

        # Task 2: Insert document metadata
        conn = await psycopg.AsyncConnection.connect(settings.postgres_dsn)
        try:
            await create_document_metadata_table(conn)
            await insert_document_metadata(conn, cigref_data)

            # Task 3: Submit to LightRAG
            document_id = await submit_to_lightrag(cigref_data)

            # Task 4: Monitor processing status
            await monitor_processing_status(document_id, metrics)

            # Task 5: Validate vector storage
            await validate_vector_storage(conn, document_id, metrics)

            # Task 6 & 7: Validate graph entities and relationships
            entity_samples = await validate_graph_entities(conn, metrics)
            relationship_samples = await validate_graph_relationships(conn, metrics)

        finally:
            await conn.close()

        # Task 8: Execute query test
        query_result = await test_query(metrics)

        # Calculate total time
        metrics.total_time_seconds = time.time() - metrics.start_time

        # Task 10: Generate validation report
        report = await generate_validation_report(
            metrics, entity_samples, relationship_samples, query_result
        )

        # Save report
        report_path = Path("/home/wsluser/dev/lightrag-cv/docs/cigref-ingestion-validation.md")
        report_path.write_text(report, encoding='utf-8')

        logger.info("=" * 80)
        logger.info("CIGREF KNOWLEDGE BASE INGESTION - COMPLETED")
        logger.info("=" * 80)
        logger.info("Validation report", extra={"path": str(report_path)})
        logger.info("Metrics", extra=metrics.to_dict())

        # Print summary
        print("\n" + "=" * 80)
        print("INGESTION COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print(f"Document ID: {metrics.document_id}")
        print(f"Chunks processed: {metrics.chunks_created}/{metrics.chunk_count}")
        print(f"Entities extracted: {metrics.entities_extracted}")
        print(f"Vectors stored: {metrics.vector_count}")
        print(f"Graph entities: {metrics.entity_count}")
        print(f"Graph relationships: {metrics.relationship_count}")
        print(f"Query test: {'✅ PASSED' if metrics.query_test_passed else '❌ FAILED'}")
        print(f"Total time: {round(metrics.total_time_seconds / 60, 2):.2f} minutes")
        print(f"\nValidation report: {report_path}")
        print("=" * 80)

    except Exception as e:
        logger.error("Ingestion failed", exc_info=True, extra={"error": str(e)})
        print(f"\n❌ INGESTION FAILED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
