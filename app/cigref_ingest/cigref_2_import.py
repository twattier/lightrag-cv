#!/usr/bin/env python3
"""
Import parsed CIGREF data to LightRAG.

Part of lightrag-cv application workflows.
Module: app.cigref_ingest.cigref_2_import

This script:
1. Loads parsed data from settings.CIGREF_PARSED
2. Groups chunks by domain
3. Submits chunks to LightRAG using /documents/texts API (plural endpoint)
4. Accepts optional --domain parameter to import specific domain
5. Default behavior: Import all domains sequentially
6. Uses LightRAG's internal queue (no manual batching/monitoring)

Usage:
    # Import all domains
    python3 app/cigref_ingest/cigref_2_import.py
    python3 app/cigref_ingest/cigref_2_import.py --domain "APPLICATION LIFE CYCLE"
    python -m app.cigref_ingest.cigref_2_import
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add project root to Python path for direct script execution
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import httpx
import psycopg

from app.shared.config import settings


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
    print("   ✓ document_metadata table created/verified")


async def insert_document_metadata(
    conn: psycopg.AsyncConnection, parsed_data: Dict[str, Any]
) -> None:
    """Insert document metadata record into PostgreSQL.

    Args:
        conn: PostgreSQL async connection
        parsed_data: Parsed CIGREF data with document_metadata section
    """
    doc_meta = parsed_data.get("document_metadata", {})

    # Generate document_id from source filename if not present
    source_filename = doc_meta.get("source_filename", "cigref-parsed.json")
    document_id = f"cigref_{source_filename.replace('.', '_')}"
    total_chunks = doc_meta.get("total_chunks", 0)

    async with conn.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO document_metadata (
                document_id, document_type, source_filename, file_format,
                upload_timestamp, total_chunks, cigref_profile_name, metadata
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (document_id) DO UPDATE SET
                upload_timestamp = EXCLUDED.upload_timestamp,
                total_chunks = EXCLUDED.total_chunks,
                metadata = EXCLUDED.metadata
            """,
            (
                document_id,
                "CIGREF_PROFILE",
                source_filename,
                "PDF",
                datetime.now(),
                total_chunks,
                "CIGREF_IT_Profiles_2024",
                json.dumps(doc_meta),
            ),
        )

    await conn.commit()
    print(f"   ✓ Document metadata inserted: {document_id}")


async def submit_domain_to_lightrag(
    domain: str, chunks: List[Dict[str, Any]], retry_count: int = 0
) -> bool:
    """
    Submit a domain's chunks to LightRAG.

    Args:
        domain: Domain name
        chunks: List of chunks for this domain
        retry_count: Current retry attempt number

    Returns:
        True if successful, False otherwise
    """
    texts = []
    file_sources = []

    print(f"INGESTION_TIMEOUT = {settings.INGESTION_TIMEOUT}")

    # Prepare texts with metadata headers
    for chunk in chunks:
        chunk_id = chunk.get("chunk_id", "unknown")
        page = chunk.get("metadata", {}).get("page", 0)
        job_profile = chunk.get("metadata", {}).get("job_profile", "")
        content = chunk.get("content", "")

        # Build metadata header
        metadata_header = (
            f"[CHUNK_ID: {chunk_id}]\n"
            f"[PAGE: {page}]\n"
            f"[DOMAIN: {domain}]\n"
            f"[JOB_PROFILE: {job_profile}]\n\n"
        )

        texts.append(metadata_header + content)
        file_sources.append(f"cigref_{domain}_{chunk_id}")

    # Submit to LightRAG
    payload = {"texts": texts, "file_sources": file_sources}

    try:
        async with httpx.AsyncClient(timeout=settings.INGESTION_TIMEOUT) as client:
            response = await client.post(
                f"{settings.lightrag_url}/documents/texts", json=payload
            )
            response.raise_for_status()

        print(f"   ✓ Submitted {len(chunks)} chunks for domain: {domain}")
        return True

    except httpx.HTTPError as e:
        if retry_count < settings.MAX_RETRIES:
            print(
                f"   ⚠ Retry {retry_count + 1}/{settings.MAX_RETRIES} for domain: {domain} (Error: {e})"
            )
            await asyncio.sleep(2**retry_count)  # Exponential backoff
            return await submit_domain_to_lightrag(domain, chunks, retry_count + 1)
        else:
            print(f"   ❌ Failed to submit domain: {domain} (Error: {e})")
            return False


async def import_all_domains(domains_data: Dict[str, List[Dict[str, Any]]]) -> int:
    """
    Import all domains sequentially.

    Args:
        domains_data: Dictionary mapping domain → chunks

    Returns:
        Number of successfully imported domains
    """
    total_domains = len(domains_data)
    successful = 0
    failed = 0

    print(f"\n📤 Importing {total_domains} domains to LightRAG...")
    print(f"   LightRAG service: {settings.lightrag_url}\n")

    for idx, (domain, chunks) in enumerate(sorted(domains_data.items()), start=1):
        print(f"[{idx}/{total_domains}] Processing domain: {domain}")

        success = await submit_domain_to_lightrag(domain, chunks)

        if success:
            successful += 1
        else:
            failed += 1

    print(f"\n📊 Import Summary:")
    print(f"   ✓ Successful: {successful}/{total_domains} domains")
    if failed > 0:
        print(f"   ❌ Failed: {failed}/{total_domains} domains")

    return successful


async def import_single_domain(
    domain_name: str, domains_data: Dict[str, List[Dict[str, Any]]]
) -> int:
    """
    Import a single domain.

    Args:
        domain_name: Name of domain to import
        domains_data: Dictionary mapping domain → chunks

    Returns:
        1 if successful, 0 otherwise
    """
    if domain_name not in domains_data:
        print(f"❌ ERROR: Domain '{domain_name}' not found in parsed data")
        print(f"\nAvailable domains:")
        for domain in sorted(domains_data.keys()):
            print(f"   • {domain}")
        return 0

    chunks = domains_data[domain_name]
    print(f"\n📤 Importing domain: {domain_name}")
    print(f"   Chunks to import: {len(chunks)}")
    print(f"   LightRAG service: {settings.lightrag_url}\n")

    success = await submit_domain_to_lightrag(domain_name, chunks)

    if success:
        print(f"\n✅ Successfully imported domain: {domain_name}")
        return 1
    else:
        print(f"\n❌ Failed to import domain: {domain_name}")
        return 0


async def main_async(domain_filter: str | None) -> int:
    """
    Main async entry point.

    Args:
        domain_filter: Optional domain name to filter (None = import all)

    Returns:
        Exit code (0 for success)
    """
    print("🔧 CIGREF Import to LightRAG")
    print("=" * 60)

    # Load parsed data
    print(f"\n📂 Loading parsed data: {settings.CIGREF_PARSED.name}")

    if not settings.CIGREF_PARSED.exists():
        print(f"❌ ERROR: Parsed data file not found: {settings.CIGREF_PARSED}")
        print(f"\nPlease run cigref_1_parse.py first:")
        print(f"   python -m app.cigref_ingest.cigref_1_parse")
        return 1

    with open(settings.CIGREF_PARSED, "r", encoding="utf-8") as f:
        parsed_data = json.load(f)

    domains_data = parsed_data.get("domains", {})
    doc_metadata = parsed_data.get("document_metadata", {})

    print(f"   ✓ Loaded {doc_metadata.get('total_domains', 0)} domains")
    print(f"   ✓ Total chunks: {doc_metadata.get('total_chunks', 0)}")

    # Insert document metadata
    print(f"\n📊 Inserting document metadata to PostgreSQL...")
    conn = await psycopg.AsyncConnection.connect(settings.postgres_dsn)
    try:
        await create_document_metadata_table(conn)
        await insert_document_metadata(conn, parsed_data)
    finally:
        await conn.close()

    # Import domains
    if domain_filter:
        successful = await import_single_domain(domain_filter, domains_data)
    else:
        successful = await import_all_domains(domains_data)

    # Summary
    print("\n" + "=" * 60)
    if successful > 0:
        print("✅ IMPORT COMPLETE!")
        return 0
    else:
        print("❌ IMPORT FAILED!")
        return 1


def main() -> int:
    """
    Main entry point with CLI argument parsing.

    Returns:
        Exit code (0 for success)
    """
    parser = argparse.ArgumentParser(description="Import parsed CIGREF data to LightRAG")
    parser.add_argument(
        "--domain",
        type=str,
        default=None,
        help="Import only this specific domain (default: import all domains)",
    )

    args = parser.parse_args()

    try:
        return asyncio.run(main_async(args.domain))
    except Exception as e:
        print(f"\n❌ ERROR: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
