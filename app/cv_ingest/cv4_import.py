#!/usr/bin/env python3
"""
CV Import Script - Submit CVs to LightRAG with metadata tracking.

Part of lightrag-cv application workflows.
Module: app.cv_ingest.cv4_import

Imports CVs from parsed data into LightRAG with metadata headers and
tracks import status in PostgreSQL document_metadata table.

Story: Story 2.5.3c - Refactor CV Ingest Workflow for Simplicity
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

import asyncpg
import httpx

# Import centralized configuration (RULE 2)
from app.shared.config import settings

# Configure logging (RULE 7)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def create_document_metadata_table(conn: asyncpg.Connection):
    """
    Create document_metadata table if not exists.

    This table tracks all documents imported to LightRAG with their metadata.
    """
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS document_metadata (
            document_id TEXT PRIMARY KEY,
            document_type TEXT NOT NULL,
            source_filename TEXT,
            candidate_label TEXT,
            job_title TEXT,
            role_domain TEXT,
            experience_level TEXT,
            is_latin_text BOOLEAN,
            file_format TEXT,
            file_size_kb FLOAT,
            page_count INTEGER,
            chunks_count INTEGER,
            import_timestamp TIMESTAMPTZ DEFAULT NOW(),
            metadata JSONB
        );
    """)
    logger.info("document_metadata table ready")


async def insert_document_metadata(
    conn: asyncpg.Connection,
    cv_meta: Dict,
    parsed_data: Dict
):
    """
    Insert or update CV metadata in document_metadata table.

    Args:
        conn: Database connection
        cv_meta: CV metadata from manifest
        parsed_data: Parsed CV data with chunks
    """
    await conn.execute("""
        INSERT INTO document_metadata (
            document_id, document_type, source_filename, candidate_label,
            job_title, role_domain, experience_level, is_latin_text,
            file_format, file_size_kb, page_count, chunks_count, metadata
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
        ON CONFLICT (document_id) DO UPDATE SET
            job_title = EXCLUDED.job_title,
            role_domain = EXCLUDED.role_domain,
            experience_level = EXCLUDED.experience_level,
            is_latin_text = EXCLUDED.is_latin_text,
            chunks_count = EXCLUDED.chunks_count,
            import_timestamp = NOW()
    """,
        cv_meta["candidate_label"],                      # document_id
        "CV",                                             # document_type
        cv_meta.get("filename"),                          # source_filename
        cv_meta["candidate_label"],                       # candidate_label
        cv_meta.get("job_title", "Unknown"),              # job_title
        cv_meta.get("role_domain", "Unknown"),            # role_domain
        cv_meta.get("experience_level", "Unknown"),       # experience_level
        cv_meta.get("is_latin_text", True),               # is_latin_text
        cv_meta.get("file_format"),                       # file_format
        cv_meta.get("file_size_kb"),                      # file_size_kb
        cv_meta.get("page_count"),                        # page_count
        len(parsed_data.get("chunks", [])),               # chunks_count
        json.dumps(cv_meta)                               # metadata (full manifest entry)
    )


async def submit_cv_to_lightrag(
    cv_meta: Dict,
    parsed_data: Dict,
    client: httpx.AsyncClient
) -> bool:
    """
    Submit single CV to LightRAG with metadata headers.

    Args:
        cv_meta: CV metadata from manifest
        parsed_data: Parsed CV data with chunks
        client: HTTP client

    Returns:
        True if successful, False otherwise
    """
    candidate_label = cv_meta["candidate_label"]

    try:
        # Extract chunks from parsed data
        chunks = parsed_data.get("chunks", [])

        if not chunks:
            logger.warning(
                "No chunks found for CV",
                extra={"candidate_label": candidate_label}
            )
            return False

        # Prepare text with metadata headers
        texts = []
        file_sources = []

        for idx, chunk in enumerate(chunks):
            # Metadata header (RULE 7: Structured context)
            metadata_header = (
                f"[CANDIDATE_LABEL: {candidate_label}]\n"
                f"[JOB_TITLE: {cv_meta.get('job_title', 'Unknown')}]\n"
                f"[ROLE_DOMAIN: {cv_meta.get('role_domain', 'Unknown')}]\n"
                f"[EXPERIENCE_LEVEL: {cv_meta.get('experience_level', 'Unknown')}]\n"
                f"[PAGE: {chunk.get('metadata', {}).get('page', 'N/A')}]\n\n"
            )
            texts.append(metadata_header + chunk.get("content", ""))
            file_sources.append(f"cv_{candidate_label}_{idx}")

        # Submit to LightRAG (RULE 9: Async I/O)
        logger.info(
            f"Submitting CV to LightRAG: {candidate_label} ({len(texts)} chunks)"
        )

        response = await client.post(
            f"{settings.lightrag_url}/documents/texts",
            json={"texts": texts, "file_sources": file_sources},
            timeout=settings.INGESTION_TIMEOUT
        )
        response.raise_for_status()

        logger.info(
            f"CV submitted successfully: {candidate_label}"
        )
        return True

    except httpx.HTTPError as e:
        logger.error(
            "HTTP error submitting CV",
            extra={
                "candidate_label": candidate_label,
                "error": str(e)
            }
        )
        return False
    except Exception as e:
        logger.error(
            "Error submitting CV",
            extra={
                "candidate_label": candidate_label,
                "error": str(e)
            }
        )
        return False


async def import_cvs(candidate_label: Optional[str] = None):
    """
    Main import function - submits CVs to LightRAG and tracks metadata.

    Args:
        candidate_label: If provided, import only this CV. Otherwise import all.
    """
    # Load manifest
    manifest_path = settings.CV_MANIFEST

    if not manifest_path.exists():
        logger.error(
            "CV manifest not found",
            extra={"path": str(manifest_path)}
        )
        sys.exit(1)

    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    cvs = manifest.get("cvs", [])

    # Filter if specific CV requested
    if candidate_label:
        cvs_to_import = [cv for cv in cvs if cv["candidate_label"] == candidate_label]
        if not cvs_to_import:
            logger.error(
                "CV not found in manifest",
                extra={"candidate_label": candidate_label}
            )
            sys.exit(1)
    else:
        cvs_to_import = cvs

    logger.info("=" * 70)
    logger.info("CV IMPORT TO LIGHTRAG")
    logger.info("=" * 70)
    logger.info(f"Total CVs to import: {len(cvs_to_import)}")
    logger.info("")

    # Connect to database
    try:
        conn = await asyncpg.connect(settings.postgres_dsn)
        logger.info("Connected to PostgreSQL")

        # Create table if needed
        await create_document_metadata_table(conn)

    except Exception as e:
        logger.error(
            "Failed to connect to PostgreSQL",
            extra={"error": str(e)}
        )
        sys.exit(1)

    # Import CVs
    successful = 0
    failed = 0
    skipped_non_latin = 0

    async with httpx.AsyncClient(timeout=settings.INGESTION_TIMEOUT) as client:
        for cv_meta in cvs_to_import:
            candidate_label = cv_meta["candidate_label"]

            # Filter: Only import CVs with is_latin_text=True
            if not cv_meta.get("is_latin_text", False):
                logger.info(
                    f"Skipping non-Latin text CV: {candidate_label}"
                )
                skipped_non_latin += 1
                continue

            parsed_file = settings.CV_PARSED_DIR / f"{candidate_label}_parsed.json"

            # Check if parsed file exists
            if not parsed_file.exists():
                logger.warning(
                    "Parsed file not found, skipping",
                    extra={"candidate_label": candidate_label}
                )
                failed += 1
                continue

            # Load parsed data
            with open(parsed_file, 'r') as f:
                parsed_data = json.load(f)

            # Submit to LightRAG
            success = await submit_cv_to_lightrag(cv_meta, parsed_data, client)

            if success:
                # Track metadata in PostgreSQL
                try:
                    await insert_document_metadata(conn, cv_meta, parsed_data)
                    successful += 1
                    logger.info(
                        f"Metadata recorded: {candidate_label}"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to record metadata for {candidate_label}: {str(e)}",
                        extra={
                            "candidate_label": candidate_label,
                            "error": str(e)
                        }
                    )
                    failed += 1
            else:
                failed += 1

            logger.info("")  # Blank line for readability

    # Close database connection
    await conn.close()

    # Summary
    logger.info("=" * 70)
    logger.info("IMPORT SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total CVs processed:      {len(cvs_to_import)}")
    logger.info(f"Skipped (non-Latin text): {skipped_non_latin}")
    logger.info(f"Successful imports:       {successful}")
    logger.info(f"Failed imports:           {failed}")
    logger.info("")

    if successful > 0:
        logger.info("✅ CV import completed successfully!")
    else:
        logger.error("❌ No CVs were imported")
        sys.exit(1)


def main():
    """Main execution with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="Import CVs to LightRAG with metadata tracking"
    )
    parser.add_argument(
        "--candidate-label",
        type=str,
        help="Import specific CV by candidate_label (e.g., cv_001)"
    )
    args = parser.parse_args()

    # Run async import
    asyncio.run(import_cvs(candidate_label=args.candidate_label))


if __name__ == "__main__":
    main()
