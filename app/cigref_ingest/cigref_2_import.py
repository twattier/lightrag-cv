#!/usr/bin/env python3
"""
Import parsed CIGREF data to LightRAG.

Part of lightrag-cv application workflows.
Module: app.cigref_ingest.cigref_2_import

This script:
1. Loads parsed data from settings.CIGREF_PARSED
2. Groups chunks by domain
3. Creates custom entities and relationships in LightRAG knowledge graph (optional)
4. Submits chunks to LightRAG using /documents/texts API (plural endpoint)
5. Accepts optional --domain parameter to import specific domain
6. Accepts optional --skip-entities flag to skip entity creation
7. Default behavior: Import all domains sequentially with entity creation
8. Uses LightRAG's internal queue (no manual batching/monitoring)

Usage:
    # Import all domains with entity creation (forward relationships only)
    python3 app/cigref_ingest/cigref_2_import.py
    python -m app.cigref_ingest.cigref_2_import

    # Import specific domain
    python3 app/cigref_ingest/cigref_2_import.py --domain "APPLICATION LIFE CYCLE"

    # Create bidirectional relationships
    python3 app/cigref_ingest/cigref_2_import.py --bi-direction

    # Skip entity creation (backward compatibility)
    python3 app/cigref_ingest/cigref_2_import.py --skip-entities
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from typing import Any, Dict, List

import httpx
import psycopg

from app.shared.config import settings


# ============================================================================
# Entity Creation Helper Functions
# ============================================================================


async def check_entity_exists(entity_name: str, client: httpx.AsyncClient) -> bool:
    """Check if entity exists in LightRAG knowledge graph.

    Args:
        entity_name: Name of entity to check
        client: HTTP client for API calls

    Returns:
        True if entity exists, False otherwise
    """
    try:
        response = await client.get(
            f"{settings.lightrag_url}/graph/entity/exists",
            params={"name": entity_name},
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json().get("exists", False)
    except httpx.HTTPError as e:
        print(f"   ⚠ Error checking entity existence: {entity_name} - {e}")
        return False


async def create_entity(
    name: str,
    description: str,
    entity_type: str,
    client: httpx.AsyncClient,
    retry_count: int = 0,
) -> bool:
    """Create entity in LightRAG knowledge graph with retry logic.

    Args:
        name: Entity name
        description: Entity description
        entity_type: Entity type (DOMAIN_PROFILE, PROFILE, etc.)
        client: HTTP client for API calls
        retry_count: Current retry attempt number

    Returns:
        True if created successfully, False otherwise
    """
    try:
        response = await client.post(
            f"{settings.lightrag_url}/graph/entity/create",
            json={
                "entity_name": name,
                "entity_data": {"description": description, "entity_type": entity_type},
            },
            timeout=10.0,
        )
        response.raise_for_status()
        return True
    except httpx.HTTPError as e:
        if retry_count < settings.MAX_RETRIES:
            await asyncio.sleep(2**retry_count)  # Exponential backoff
            return await create_entity(
                name, description, entity_type, client, retry_count + 1
            )
        else:
            print(
                f"   ❌ Failed to create entity after {settings.MAX_RETRIES} retries: {name} (type: {entity_type}) - {e}"
            )
            return False


async def create_relationship(
    src_id: str, tgt_id: str, relation: str, client: httpx.AsyncClient, retry_count: int = 0
) -> bool:
    """Create relationship in LightRAG knowledge graph with retry logic.

    Args:
        src_id: Source entity name
        tgt_id: Target entity name
        relation: Relationship type
        client: HTTP client for API calls
        retry_count: Current retry attempt number

    Returns:
        True if created/exists successfully, False otherwise
    """
    try:
        response = await client.post(
            f"{settings.lightrag_url}/graph/relation/create",
            json={
                "source_entity": src_id,
                "target_entity": tgt_id,
                "relation_data": {
                    "description": f"{src_id} {relation} {tgt_id}",
                    "keywords": relation,
                    "weight": 1.0,
                },
            },
            timeout=10.0,
        )
        response.raise_for_status()
        return True
    except httpx.HTTPError as e:
        if retry_count < settings.MAX_RETRIES:
            await asyncio.sleep(2**retry_count)  # Exponential backoff
            return await create_relationship(src_id, tgt_id, relation, client, retry_count + 1)
        else:
            print(
                f"   ❌ Failed to create relationship after {settings.MAX_RETRIES} retries: {src_id} --[{relation}]--> {tgt_id} - {e}"
            )
            return False


async def create_cigref_entities(
    domain_id: str,
    profiles: List[Dict[str, Any]],
    client: httpx.AsyncClient,
    bi_direction: bool = False,
) -> Dict[str, int]:
    """Create CIGREF entities and relationships in LightRAG knowledge graph.

    Creates:
    1. DOMAIN_PROFILE entity for the domain
    2. PROFILE entities for each unique profile in the domain
    3. Relationships:
       - DOMAIN_PROFILE --[HAS_PROFILE]--> PROFILE (always created)
       - PROFILE --[BELONGS_TO_DOMAIN]--> DOMAIN_PROFILE (only if bi_direction=True)

    Args:
        domain_id: Domain name (e.g., "APPLICATION LIFE CYCLE")
        profiles: List of profile chunks from parsed CIGREF data
        client: HTTP client for API calls
        bi_direction: If True, create bidirectional relationships (default: False)

    Returns:
        Dictionary with statistics:
        {
            "domain_entities_created": int,
            "profile_entities_created": int,
            "relationships_created": int,
            "errors": int
        }
    """
    stats = {
        "domain_entities_created": 0,
        "profile_entities_created": 0,
        "relationships_created": 0,
        "errors": 0,
    }

    # Step 1: Create DOMAIN_PROFILE entity
    domain_exists = await check_entity_exists(domain_id, client)
    if not domain_exists:
        success = await create_entity(domain_id, domain_id, "DOMAIN_PROFILE", client)
        if success:
            print(f"   ✓ Created DOMAIN_PROFILE entity: {domain_id}")
            stats["domain_entities_created"] += 1
        else:
            print(f"   ❌ Failed to create DOMAIN_PROFILE entity: {domain_id}")
            stats["errors"] += 1
    else:
        print(f"   • DOMAIN_PROFILE entity already exists: {domain_id}")

    # Step 2: Extract unique profile names
    unique_profiles = set()
    for chunk in profiles:
        job_profile = chunk.get("metadata", {}).get("job_profile", "")
        if job_profile:
            unique_profiles.add(job_profile)

    print(f"   Found {len(unique_profiles)} unique profiles in domain: {domain_id}")

    # Step 3: Create PROFILE entities
    created_profiles = []
    for profile_name in sorted(unique_profiles):
        profile_exists = await check_entity_exists(profile_name, client)
        if not profile_exists:
            success = await create_entity(profile_name, profile_name, "PROFILE", client)
            if success:
                stats["profile_entities_created"] += 1
                created_profiles.append(profile_name)
            else:
                stats["errors"] += 1
        else:
            created_profiles.append(profile_name)  # Track for relationship creation

    if stats["profile_entities_created"] > 0:
        print(
            f"   ✓ Created {stats['profile_entities_created']} PROFILE entities"
        )

    # Step 4: Create relationships
    for profile_name in created_profiles:
        # Create DOMAIN_PROFILE --[HAS_PROFILE]--> PROFILE
        success1 = await create_relationship(
            domain_id, profile_name, "HAS_PROFILE", client
        )
        if success1:
            stats["relationships_created"] += 1
        else:
            stats["errors"] += 1

        # Create PROFILE --[BELONGS_TO_DOMAIN]--> DOMAIN_PROFILE (only if bi_direction enabled)
        if bi_direction:
            success2 = await create_relationship(
                profile_name, domain_id, "BELONGS_TO_DOMAIN", client
            )
            if success2:
                stats["relationships_created"] += 1
            else:
                stats["errors"] += 1

    if stats["relationships_created"] > 0:
        print(f"   ✓ Created {stats['relationships_created']} relationships")

    return stats


# ============================================================================
# Document Metadata Management
# ============================================================================


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
    domain: str,
    chunks: List[Dict[str, Any]],
    skip_entities: bool = False,
    bi_direction: bool = False,
    retry_count: int = 0,
) -> tuple[bool, Dict[str, int]]:
    """
    Submit a domain's chunks to LightRAG.

    Args:
        domain: Domain name
        chunks: List of chunks for this domain
        skip_entities: If True, skip entity creation
        bi_direction: If True, create bidirectional relationships
        retry_count: Current retry attempt number

    Returns:
        Tuple of (success: bool, entity_stats: Dict[str, int])
    """
    entity_stats = {
        "domain_entities_created": 0,
        "profile_entities_created": 0,
        "relationships_created": 0,
        "errors": 0,
    }

    texts = []
    file_sources = []

    print(f"INGESTION_TIMEOUT = {settings.INGESTION_TIMEOUT}")

    # Prepare texts with metadata headers
    for chunk in chunks:
        chunk_id = chunk.get("chunk_id", "unknown")
        job_profile = chunk.get("metadata", {}).get("job_profile", "")
        section = chunk.get("metadata", {}).get("section", "")
        content = chunk.get("content", "")

        # Build metadata header
        metadata_header = (
            f"[DOMAIN_PROFILE: {domain}]\n"
            f"[PROFILE: {job_profile}]\n"
            f"[SECTION: {section}]\n\n"
        )

        texts.append(metadata_header + content)
        file_sources.append(f"cigref_{domain}_{chunk_id}")

    # Submit to LightRAG
    payload = {"texts": texts, "file_sources": file_sources}

    try:
        async with httpx.AsyncClient(timeout=settings.INGESTION_TIMEOUT) as client:
            # Step 1: Create entities if not skipped
            if not skip_entities:
                print(f"   📊 Creating entities for domain: {domain}")
                entity_stats = await create_cigref_entities(domain, chunks, client, bi_direction)

            # Step 2: Submit text chunks
            response = await client.post(
                f"{settings.lightrag_url}/documents/texts", json=payload
            )
            response.raise_for_status()

        print(f"   ✓ Submitted {len(chunks)} chunks for domain: {domain}")
        return True, entity_stats

    except httpx.HTTPError as e:
        if retry_count < settings.MAX_RETRIES:
            print(
                f"   ⚠ Retry {retry_count + 1}/{settings.MAX_RETRIES} for domain: {domain} (Error: {e})"
            )
            await asyncio.sleep(2**retry_count)  # Exponential backoff
            return await submit_domain_to_lightrag(
                domain, chunks, skip_entities, bi_direction, retry_count + 1
            )
        else:
            print(f"   ❌ Failed to submit domain: {domain} (Error: {e})")
            return False, entity_stats


async def import_all_domains(
    domains_data: Dict[str, List[Dict[str, Any]]],
    skip_entities: bool = False,
    bi_direction: bool = False,
) -> int:
    """
    Import all domains sequentially.

    Args:
        domains_data: Dictionary mapping domain → chunks
        skip_entities: If True, skip entity creation
        bi_direction: If True, create bidirectional relationships

    Returns:
        Number of successfully imported domains
    """
    total_domains = len(domains_data)
    successful = 0
    failed = 0
    total_entity_stats = {
        "domain_entities_created": 0,
        "profile_entities_created": 0,
        "relationships_created": 0,
        "errors": 0,
    }

    print(f"\n📤 Importing {total_domains} domains to LightRAG...")
    print(f"   LightRAG service: {settings.lightrag_url}")
    if skip_entities:
        print("   ⚠ Entity creation SKIPPED (--skip-entities flag)")
    else:
        print("   📊 Entity creation ENABLED")
    print()

    for idx, (domain, chunks) in enumerate(sorted(domains_data.items()), start=1):
        print(f"[{idx}/{total_domains}] Processing domain: {domain}")

        success, entity_stats = await submit_domain_to_lightrag(
            domain, chunks, skip_entities, bi_direction
        )

        if success:
            successful += 1
            # Aggregate entity stats
            total_entity_stats["domain_entities_created"] += entity_stats[
                "domain_entities_created"
            ]
            total_entity_stats["profile_entities_created"] += entity_stats[
                "profile_entities_created"
            ]
            total_entity_stats["relationships_created"] += entity_stats[
                "relationships_created"
            ]
            total_entity_stats["errors"] += entity_stats["errors"]
        else:
            failed += 1

    print("\n📊 Import Summary:")
    print(f"   ✓ Successful: {successful}/{total_domains} domains")
    if failed > 0:
        print(f"   ❌ Failed: {failed}/{total_domains} domains")

    # Print entity creation stats
    if not skip_entities:
        print("\n📊 Entity Creation Summary:")
        print(
            f"   ✓ DOMAIN_PROFILE entities created: {total_entity_stats['domain_entities_created']}"
        )
        print(
            f"   ✓ PROFILE entities created: {total_entity_stats['profile_entities_created']}"
        )
        print(
            f"   ✓ Relationships created: {total_entity_stats['relationships_created']}"
        )
        if total_entity_stats["errors"] > 0:
            print(f"   ❌ Errors: {total_entity_stats['errors']}")

    return successful


async def import_single_domain(
    domain_name: str,
    domains_data: Dict[str, List[Dict[str, Any]]],
    skip_entities: bool = False,
    bi_direction: bool = False,
) -> int:
    """
    Import a single domain.

    Args:
        domain_name: Name of domain to import
        domains_data: Dictionary mapping domain → chunks
        skip_entities: If True, skip entity creation
        bi_direction: If True, create bidirectional relationships

    Returns:
        1 if successful, 0 otherwise
    """
    if domain_name not in domains_data:
        print(f"❌ ERROR: Domain '{domain_name}' not found in parsed data")
        print("\nAvailable domains:")
        for domain in sorted(domains_data.keys()):
            print(f"   • {domain}")
        return 0

    chunks = domains_data[domain_name]
    print(f"\n📤 Importing domain: {domain_name}")
    print(f"   Chunks to import: {len(chunks)}")
    print(f"   LightRAG service: {settings.lightrag_url}")
    if skip_entities:
        print("   ⚠ Entity creation SKIPPED (--skip-entities flag)")
    else:
        print("   📊 Entity creation ENABLED")
    print()

    success, entity_stats = await submit_domain_to_lightrag(
        domain_name, chunks, skip_entities, bi_direction
    )

    if success:
        print(f"\n✅ Successfully imported domain: {domain_name}")

        # Print entity creation stats
        if not skip_entities:
            print("\n📊 Entity Creation Summary:")
            print(
                f"   ✓ DOMAIN_PROFILE entities created: {entity_stats['domain_entities_created']}"
            )
            print(
                f"   ✓ PROFILE entities created: {entity_stats['profile_entities_created']}"
            )
            print(f"   ✓ Relationships created: {entity_stats['relationships_created']}")
            if entity_stats["errors"] > 0:
                print(f"   ❌ Errors: {entity_stats['errors']}")

        return 1
    else:
        print(f"\n❌ Failed to import domain: {domain_name}")
        return 0


async def main_async(
    domain_filter: str | None, skip_entities: bool = False, bi_direction: bool = False
) -> int:
    """
    Main async entry point.

    Args:
        domain_filter: Optional domain name to filter (None = import all)
        skip_entities: If True, skip entity creation
        bi_direction: If True, create bidirectional relationships

    Returns:
        Exit code (0 for success)
    """
    print("🔧 CIGREF Import to LightRAG")
    print("=" * 60)

    # Load parsed data
    print(f"\n📂 Loading parsed data: {settings.CIGREF_PARSED.name}")

    if not settings.CIGREF_PARSED.exists():
        print(f"❌ ERROR: Parsed data file not found: {settings.CIGREF_PARSED}")
        print("\nPlease run cigref_1_parse.py first:")
        print("   python -m app.cigref_ingest.cigref_1_parse")
        return 1

    with open(settings.CIGREF_PARSED, "r", encoding="utf-8") as f:
        parsed_data = json.load(f)

    domains_data = parsed_data.get("domains", {})
    doc_metadata = parsed_data.get("document_metadata", {})

    print(f"   ✓ Loaded {doc_metadata.get('total_domains', 0)} domains")
    print(f"   ✓ Total chunks: {doc_metadata.get('total_chunks', 0)}")

    # Insert document metadata
    print("\n📊 Inserting document metadata to PostgreSQL...")
    conn = await psycopg.AsyncConnection.connect(settings.postgres_dsn)
    try:
        await create_document_metadata_table(conn)
        await insert_document_metadata(conn, parsed_data)
    finally:
        await conn.close()

    # Import domains
    if domain_filter:
        successful = await import_single_domain(
            domain_filter, domains_data, skip_entities, bi_direction
        )
    else:
        successful = await import_all_domains(domains_data, skip_entities, bi_direction)

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
    parser.add_argument(
        "--skip-entities",
        action="store_true",
        default=False,
        help="Skip entity creation, only submit text chunks (default: False)",
    )
    parser.add_argument(
        "--bi-direction",
        action="store_true",
        default=False,
        help="Create bidirectional relationships (BELONGS_TO_DOMAIN) in addition to forward relationships (HAS_PROFILE) (default: False)",
    )

    args = parser.parse_args()

    try:
        return asyncio.run(main_async(args.domain, args.skip_entities, args.bi_direction))
    except Exception as e:
        print(f"\n❌ ERROR: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
