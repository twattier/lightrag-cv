#!/usr/bin/env python3
"""
CV Import Script - Submit CVs to LightRAG with metadata tracking.

Part of lightrag-cv application workflows.
Module: app.cv_ingest.cv4_import

Imports CVs from parsed data into LightRAG with metadata headers and
tracks import status in PostgreSQL document_metadata table.

Cleanup Phase:
Before importing, automatically removes rejected CVs:
- CVs without parsed files
- CVs with is_latin_text != True

Cleanup actions:
- Removes record from cvs-manifest.json
- Deletes parsed JSON file (if exists)
- Deletes source PDF file

Usage:
    python -m app.cv_ingest.cv4_import                  # Import all (with cleanup, with entities)
    python -m app.cv_ingest.cv4_import --skip-cleanup   # Import all (no cleanup, with entities)
    python -m app.cv_ingest.cv4_import --skip-entities  # Import all (with cleanup, no entities)
    python -m app.cv_ingest.cv4_import --candidate-label cv_001  # Import specific CV

Story: Story 2.5.3c - Refactor CV Ingest Workflow for Simplicity
Story: Story 2.9.2 - CV Custom Entity Creation
"""

import argparse
import asyncio
import json
import logging
import sys
from typing import Any, Dict, Optional, Set, Tuple

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


# ============================================================================
# Entity Creation Helper Functions (Story 2.9.2)
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
        logger.warning(f"Error checking entity existence: {entity_name} - {e}")
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
        entity_type: Entity type (CV, DOMAIN_JOB, JOB, XP)
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
            logger.error(
                f"Failed to create entity after {settings.MAX_RETRIES} retries: "
                f"{name} (type: {entity_type}) - {e}"
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
            logger.error(
                f"Failed to create relationship after {settings.MAX_RETRIES} retries: "
                f"{src_id} --[{relation}]--> {tgt_id} - {e}"
            )
            return False


async def create_cv_entities(
    cv_meta: Dict[str, Any],
    client: httpx.AsyncClient,
    shared_relationships: Set[Tuple[str, str, str]]
) -> Dict[str, int]:
    """Create custom entities for a CV with relationships.

    This function creates typed entities and relationships for CV knowledge graph:
    - CV entity (unique per CV)
    - DOMAIN_JOB, JOB, XP entities (shared, deduplicated)
    - CV-specific relationships (WORKS_IN, HAS_JOB_TITLE, HAS_EXPERIENCE_LEVEL)
    - Shared relationships (INCLUDES_JOB, REQUIRES_LEVEL) with client-side deduplication

    Args:
        cv_meta: CV metadata from manifest
        client: HTTP client for API calls
        shared_relationships: Set to track created shared relationships (deduplication)

    Returns:
        Dictionary with creation statistics
    """
    stats = {
        "cv_entities_created": 0,
        "domain_job_entities_created": 0,
        "job_entities_created": 0,
        "xp_entities_created": 0,
        "relationships_created": 0,
        "relationships_skipped": 0,  # Duplicates avoided
        "errors": 0
    }

    # Extract metadata
    candidate_label = cv_meta["candidate_label"]
    role_domain = cv_meta.get("role_domain", "Unknown")
    job_title = cv_meta.get("job_title", "Unknown")
    experience_level = cv_meta.get("experience_level", "Unknown")

    # Build CV description
    description = f"{role_domain} / {job_title} / {experience_level}"

    try:
        # Create CV entity (unique per CV)
        cv_exists = await check_entity_exists(candidate_label, client)
        if not cv_exists:
            if await create_entity(candidate_label, description, "CV", client):
                stats["cv_entities_created"] += 1
                logger.info(f"   ✓ Created CV entity: {candidate_label}")
        else:
            logger.info(f"   • CV entity already exists: {candidate_label}")

        # Create shared entities (deduplicated across CVs)
        domain_exists = await check_entity_exists(role_domain, client)
        if not domain_exists:
            if await create_entity(role_domain, role_domain, "DOMAIN_JOB", client):
                stats["domain_job_entities_created"] += 1
                logger.info(f"   ✓ Created DOMAIN_JOB entity: {role_domain}")
        else:
            logger.debug(f"   • DOMAIN_JOB entity already exists: {role_domain}")

        job_exists = await check_entity_exists(job_title, client)
        if not job_exists:
            if await create_entity(job_title, job_title, "JOB", client):
                stats["job_entities_created"] += 1
                logger.info(f"   ✓ Created JOB entity: {job_title}")
        else:
            logger.debug(f"   • JOB entity already exists: {job_title}")

        xp_exists = await check_entity_exists(experience_level, client)
        if not xp_exists:
            if await create_entity(experience_level, experience_level, "XP", client):
                stats["xp_entities_created"] += 1
                logger.info(f"   ✓ Created XP entity: {experience_level}")
        else:
            logger.debug(f"   • XP entity already exists: {experience_level}")

        # Create CV-specific relationships (always create)
        cv_relationships = [
            (candidate_label, "WORKS_IN", role_domain),
            (candidate_label, "HAS_JOB_TITLE", job_title),
            (candidate_label, "HAS_EXPERIENCE_LEVEL", experience_level),
        ]

        for src_id, relation, tgt_id in cv_relationships:
            if await create_relationship(src_id, tgt_id, relation, client):
                stats["relationships_created"] += 1
            else:
                stats["errors"] += 1

        # Create shared relationships (with client-side deduplication)
        shared_rels = [
            (role_domain, "INCLUDES_JOB", job_title),
            (job_title, "REQUIRES_LEVEL", experience_level),
        ]

        for src_id, relation, tgt_id in shared_rels:
            rel_key = (src_id, relation, tgt_id)
            if rel_key not in shared_relationships:
                if await create_relationship(src_id, tgt_id, relation, client):
                    shared_relationships.add(rel_key)  # Track to avoid duplicates
                    stats["relationships_created"] += 1
                else:
                    stats["errors"] += 1
            else:
                # Already created by previous CV
                stats["relationships_skipped"] += 1
                logger.debug(f"   • Skipped duplicate relationship: {src_id} --[{relation}]--> {tgt_id}")

    except Exception as e:
        logger.error(f"Error creating entities for CV: {candidate_label} - {e}")
        stats["errors"] += 1

    return stats


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
                f"[EXPERIENCE_LEVEL: {cv_meta.get('experience_level', 'Unknown')}]\n\n"                
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


async def cleanup_rejected_cvs(manifest: Dict) -> Dict:
    """
    Remove rejected CVs from manifest and delete their files.

    A CV is rejected if:
    1. No parsed file exists, OR
    2. is_latin_text != True

    Cleanup actions:
    - Remove record from manifest
    - Delete parsed JSON file (if exists)
    - Delete source PDF file

    Args:
        manifest: The manifest dict loaded from cvs-manifest.json

    Returns:
        Updated manifest dict with rejected CVs removed
    """
    cvs = manifest.get("cvs", [])
    cvs_to_keep = []
    rejected_count = 0

    logger.info("=" * 70)
    logger.info("CLEANUP: Removing rejected CVs")
    logger.info("=" * 70)

    for cv_meta in cvs:
        candidate_label = cv_meta["candidate_label"]
        parsed_file = settings.CV_PARSED_DIR / f"{candidate_label}_parsed.json"
        pdf_file = settings.CV_DOCS_DIR / cv_meta.get("filename", f"{candidate_label}.pdf")

        # Check rejection criteria
        has_parsed_file = parsed_file.exists()
        is_latin = cv_meta.get("is_latin_text", False)

        if not has_parsed_file or not is_latin:
            # This CV is rejected
            rejected_count += 1
            reason = []
            if not has_parsed_file:
                reason.append("no parsed file")
            if not is_latin:
                reason.append(f"is_latin_text={is_latin}")

            logger.info(f"🗑️  Removing {candidate_label}: {', '.join(reason)}")

            # Delete files
            if parsed_file.exists():
                parsed_file.unlink()
                logger.info(f"   Deleted: {parsed_file.name}")

            if pdf_file.exists():
                pdf_file.unlink()
                logger.info(f"   Deleted: {pdf_file.name}")

            # Don't add to cvs_to_keep
            continue

        # Keep this CV
        cvs_to_keep.append(cv_meta)

    # Update manifest
    manifest["cvs"] = cvs_to_keep

    logger.info("")
    logger.info(f"Rejected CVs removed: {rejected_count}")
    logger.info(f"Valid CVs remaining: {len(cvs_to_keep)}")
    logger.info("=" * 70)
    logger.info("")

    # Save updated manifest
    manifest_path = settings.CV_MANIFEST
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Updated manifest saved: {manifest_path}")
    logger.info("")

    return manifest


async def import_cvs(
    candidate_label: Optional[str] = None,
    skip_cleanup: bool = False,
    skip_entities: bool = False
):
    """
    Main import function - submits CVs to LightRAG and tracks metadata.

    Args:
        candidate_label: If provided, import only this CV. Otherwise import all.
        skip_cleanup: If True, skip the cleanup phase (for testing)
        skip_entities: If True, skip entity creation (backward compatibility)
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

    # Cleanup rejected CVs (unless skipped or importing specific CV)
    if not skip_cleanup and not candidate_label:
        manifest = await cleanup_rejected_cvs(manifest)

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
    if skip_entities:
        logger.info("⚠ Entity creation SKIPPED (--skip-entities flag)")
    else:
        logger.info("📊 Entity creation ENABLED")
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

    # Entity creation stats (Story 2.9.2)
    total_entity_stats = {
        "cv_entities_created": 0,
        "domain_job_entities_created": 0,
        "job_entities_created": 0,
        "xp_entities_created": 0,
        "relationships_created": 0,
        "relationships_skipped": 0,
        "errors": 0
    }

    # Initialize shared relationships tracking set (Story 2.9.2)
    shared_relationships: Set[Tuple[str, str, str]] = set()

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

            # Create custom entities first (if not skipped) - Story 2.9.2
            if not skip_entities:
                entity_stats = await create_cv_entities(cv_meta, client, shared_relationships)
                logger.info(
                    f"   Entities for {candidate_label}: "
                    f"CV={entity_stats['cv_entities_created']}, "
                    f"DOMAIN_JOB={entity_stats['domain_job_entities_created']}, "
                    f"JOB={entity_stats['job_entities_created']}, "
                    f"XP={entity_stats['xp_entities_created']}, "
                    f"Relations={entity_stats['relationships_created']} "
                    f"(skipped {entity_stats['relationships_skipped']} duplicates), "
                    f"Errors={entity_stats['errors']}"
                )
                # Aggregate stats
                total_entity_stats["cv_entities_created"] += entity_stats["cv_entities_created"]
                total_entity_stats["domain_job_entities_created"] += entity_stats["domain_job_entities_created"]
                total_entity_stats["job_entities_created"] += entity_stats["job_entities_created"]
                total_entity_stats["xp_entities_created"] += entity_stats["xp_entities_created"]
                total_entity_stats["relationships_created"] += entity_stats["relationships_created"]
                total_entity_stats["relationships_skipped"] += entity_stats["relationships_skipped"]
                total_entity_stats["errors"] += entity_stats["errors"]

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

    # Entity creation summary (Story 2.9.2)
    if not skip_entities:
        logger.info("=" * 70)
        logger.info("ENTITY CREATION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"CV entities created:         {total_entity_stats['cv_entities_created']}")
        logger.info(f"DOMAIN_JOB entities created: {total_entity_stats['domain_job_entities_created']}")
        logger.info(f"JOB entities created:        {total_entity_stats['job_entities_created']}")
        logger.info(f"XP entities created:         {total_entity_stats['xp_entities_created']}")
        logger.info(f"Relationships created:       {total_entity_stats['relationships_created']}")
        logger.info(f"Relationships skipped:       {total_entity_stats['relationships_skipped']} (duplicates avoided)")
        logger.info(f"Unique shared relationships: {len(shared_relationships)}")
        if total_entity_stats['errors'] > 0:
            logger.warning(f"Entity creation errors:      {total_entity_stats['errors']}")
        logger.info("")

    if successful > 0:
        logger.info("✅ CV import completed successfully!")
    else:
        logger.error("❌ No CVs were imported")
        sys.exit(1)


def main():
    """Main execution with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="Import CVs to LightRAG with metadata tracking and custom entity creation"
    )
    parser.add_argument(
        "--candidate-label",
        type=str,
        help="Import specific CV by candidate_label (e.g., cv_001)"
    )
    parser.add_argument(
        "--skip-cleanup",
        action="store_true",
        help="Skip the cleanup phase (don't remove rejected CVs)"
    )
    parser.add_argument(
        "--skip-entities",
        action="store_true",
        help="Skip entity creation, only submit text chunks (default: False)"
    )
    args = parser.parse_args()

    # Run async import
    asyncio.run(import_cvs(
        candidate_label=args.candidate_label,
        skip_cleanup=args.skip_cleanup,
        skip_entities=args.skip_entities
    ))


if __name__ == "__main__":
    main()
