"""
CIGREF Entity Duplicate Identifier (JSON + Database hybrid)

Identifies duplicate CIGREF entities in the database by:
1. Reading canonical entity names from cigref-parsed.json
2. Querying the database for all variations of those entities
3. Identifying duplicates that differ in case or separators

This approach uses the JSON file as the source of truth for canonical names,
similar to how cv1_merge_identify.py works with CV entities.

Usage:
    python -m app.db_clean.cigref1_merge_identify [options]

Arguments:
    --input-file PATH     Path to cigref-parsed.json (default: data/cigref/cigref-parsed.json)
    --output-dir PATH     Output directory for JSON file (default: data/db_clean)
    --dry-run             Show what would be identified without writing file
    --verbose             Enable verbose logging

Output:
    JSON file: data/db_clean/cigref_merge_identify_{datetime}.json

    Format:
    [
        {
            "entity_to_change_into": "APPLICATION LIFE CYCLE",
            "entities_to_change": ["Application_Life_Cycle", "application_life_cycle"],
            "entity_type": "DOMAIN_PROFILE",
            "relationship_counts": {"APPLICATION LIFE CYCLE": 25, "Application_Life_Cycle": 10},
            "normalized_name": "applicationlifecycle"
        }
    ]
"""

import argparse
import asyncio
import json
import logging
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import asyncpg

from app.shared.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def normalize_entity_name(entity_name: str) -> str:
    """
    Normalize entity name for duplicate detection.

    Converts to lowercase and removes all separators (spaces, underscores, hyphens).

    Args:
        entity_name: Original entity name

    Returns:
        Normalized entity name (lowercase, no separators)

    Examples:
        "APPLICATION_LIFE_CYCLE" -> "applicationlifecycle"
        "Application Life Cycle" -> "applicationlifecycle"
        "application-life-cycle" -> "applicationlifecycle"
        "Solution_Architect" -> "solutionarchitect"
        "Solution Architect" -> "solutionarchitect"
    """
    # Convert to lowercase
    normalized = entity_name.lower()

    # Remove all separators (spaces, underscores, hyphens)
    normalized = re.sub(r'[_\s\-]+', '', normalized)

    return normalized


def extract_canonical_entities(
    parsed_data: dict[str, Any]
) -> tuple[dict[str, str], dict[str, str]]:
    """
    Extract canonical CIGREF entity names from cigref-parsed.json.

    Args:
        parsed_data: Parsed CIGREF data loaded from JSON file

    Returns:
        Tuple of:
        - Dictionary mapping normalized_name -> canonical_name
        - Dictionary mapping normalized_name -> entity_type (DOMAIN_PROFILE or PROFILE)
        Example: ({"applicationlifecycle": "APPLICATION LIFE CYCLE"},
                  {"applicationlifecycle": "DOMAIN_PROFILE"})
    """
    canonical_entities: dict[str, str] = {}
    entity_types: dict[str, str] = {}
    domains_data = parsed_data.get("domains", {})

    for domain_name, chunks in domains_data.items():
        # Domain is a DOMAIN_PROFILE entity
        normalized = normalize_entity_name(domain_name)
        canonical_entities[normalized] = domain_name
        entity_types[normalized] = "DOMAIN_PROFILE"

        # Extract profiles from chunks
        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            profile_name = metadata.get("job_profile", "").strip()

            if profile_name:
                # Profile is a PROFILE entity
                normalized = normalize_entity_name(profile_name)
                canonical_entities[normalized] = profile_name
                entity_types[normalized] = "PROFILE"

    return canonical_entities, entity_types


async def fetch_entities_by_normalized_names(
    normalized_names: list[str]
) -> list[dict[str, Any]]:
    """
    Fetch all entities from the database that match the normalized names.

    This finds all case and separator variations of the canonical CIGREF entities.

    Args:
        normalized_names: List of normalized entity names to search for

    Returns:
        List of entities with their relationship counts and types
    """
    if not normalized_names:
        return []

    conn = await asyncpg.connect(settings.postgres_dsn)

    try:
        # Load AGE extension for graph queries
        await conn.execute("LOAD 'age';")
        await conn.execute("SET search_path = ag_catalog, '$user', public;")

        # Query to find all entities that match the normalized names
        # We'll query all entities and filter in Python for flexibility
        query = """
        WITH all_entities AS (
            SELECT
                id,
                trim(both '"' from agtype_access_operator(properties, '"entity_id"')::text) as entity_name,
                trim(both '"' from agtype_access_operator(properties, '"entity_type"')::text) as entity_type
            FROM chunk_entity_relation.base
        ),
        entity_rel_counts AS (
            SELECT
                e.entity_name,
                e.entity_type,
                COUNT(DISTINCT r.id) as relationship_count
            FROM all_entities e
            LEFT JOIN chunk_entity_relation."DIRECTED" r
                ON r.start_id = e.id OR r.end_id = e.id
            GROUP BY e.entity_name, e.entity_type
        )
        SELECT
            entity_name,
            entity_type,
            relationship_count
        FROM entity_rel_counts
        ORDER BY entity_name
        """

        rows = await conn.fetch(query)

        # Filter entities that match our normalized names
        matching_entities = []
        normalized_set = set(normalized_names)

        for row in rows:
            entity_name = row["entity_name"]
            normalized = normalize_entity_name(entity_name)

            if normalized in normalized_set:
                matching_entities.append({
                    "entity_name": entity_name,
                    "entity_type": row["entity_type"],
                    "relationship_count": row["relationship_count"],
                    "normalized_name": normalized
                })

        return matching_entities

    finally:
        await conn.close()


def identify_duplicates_for_canonical(
    entities: list[dict[str, Any]],
    canonical_entities: dict[str, str],
    canonical_entity_types: dict[str, str]
) -> list[dict[str, Any]]:
    """
    Group entities by normalized name and identify duplicates.

    Uses the canonical entity names from the JSON file as the target for merging.

    Args:
        entities: List of entity dictionaries from database
        canonical_entities: Dictionary mapping normalized_name -> canonical_name
        canonical_entity_types: Dictionary mapping normalized_name -> entity_type (DOMAIN_PROFILE or PROFILE)

    Returns:
        List of merge operations to perform
    """
    # Group entities by normalized_name (not by type, as we want to merge across types)
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for entity in entities:
        normalized_name = entity["normalized_name"]
        groups[normalized_name].append(entity)

    # Identify groups with duplicates or entities that don't match canonical
    merge_operations = []

    for normalized_name, entity_list in groups.items():
        # Get the canonical name and type from JSON
        canonical_name = canonical_entities.get(normalized_name)
        canonical_type = canonical_entity_types.get(normalized_name)

        if not canonical_name or not canonical_type:
            # This entity is not in the CIGREF canonical list
            continue

        # Only create merge operation if there are multiple entities (duplicates exist)
        if len(entity_list) > 1:
            # Sort by relationship count (descending) to find entity with most relationships
            sorted_entities = sorted(
                entity_list,
                key=lambda x: (
                    x["relationship_count"],  # Primary: most relationships
                    x["entity_name"]  # Secondary: alphabetically
                ),
                reverse=True
            )

            # The entity with most relationships becomes the merge target
            target_entity = sorted_entities[0]["entity_name"]

            # All other entities should be merged into the target
            entities_to_change = [e["entity_name"] for e in sorted_entities[1:]]

            merge_operations.append({
                "entity_to_change_into": target_entity,  # Entity with most relationships
                "entities_to_change": entities_to_change,
                "entity_type": canonical_type,  # Use canonical type from JSON
                "relationship_counts": {
                    e["entity_name"]: e["relationship_count"]
                    for e in sorted_entities
                },
                "normalized_name": canonical_name  # Canonical CIGREF name (uppercase)
            })

    return merge_operations


def save_merge_operations(
    merge_operations: list[dict[str, Any]],
    output_dir: str = "data/db_clean"
) -> Path:
    """
    Save merge operations to JSON file with timestamp.

    Args:
        merge_operations: List of merge operation dictionaries
        output_dir: Output directory path

    Returns:
        Path to the created file
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"cigref_merge_identify_{timestamp}.json"
    filepath = output_path / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(merge_operations, f, indent=2, ensure_ascii=False)

    return filepath


async def main() -> None:
    """Main entry point for CIGREF entity duplicate identification."""
    parser = argparse.ArgumentParser(
        description="Identify duplicate CIGREF entities using JSON + Database"
    )
    parser.add_argument(
        "--input-file",
        type=Path,
        default=settings.CIGREF_PARSED,
        help=f"Path to cigref-parsed.json (default: {settings.CIGREF_PARSED})"
    )
    parser.add_argument(
        "--output-dir",
        default="data/db_clean",
        help="Output directory for JSON file (default: data/db_clean)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be identified without writing file"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.info("Starting CIGREF entity duplicate identification (JSON + Database)")
    logger.info(f"Input file: {args.input_file}")

    # Step 1: Load canonical entity names from JSON
    if not args.input_file.exists():
        logger.error(f"Input file not found: {args.input_file}")
        logger.error("Please run cigref_1_parse.py first:")
        logger.error("   python -m app.cigref_ingest.cigref_1_parse")
        return

    logger.info(f"Loading canonical entities from {args.input_file.name}...")
    with open(args.input_file, "r", encoding="utf-8") as f:
        parsed_data = json.load(f)

    canonical_entities, canonical_entity_types = extract_canonical_entities(parsed_data)
    logger.info(f"Found {len(canonical_entities)} canonical CIGREF entities")

    # Step 2: Query database for all variations
    logger.info("Querying database for entity variations...")
    normalized_names = list(canonical_entities.keys())
    database_entities = await fetch_entities_by_normalized_names(normalized_names)
    logger.info(f"Found {len(database_entities)} entities in database matching canonical entities")

    # Count by entity type
    entity_counts_by_type = defaultdict(int)
    for entity in database_entities:
        entity_counts_by_type[entity["entity_type"]] += 1

    logger.info("Entity distribution in database by type:")
    for entity_type, count in sorted(entity_counts_by_type.items(), key=lambda x: x[1], reverse=True):
        logger.info(f"  {entity_type}: {count} entities")

    # Step 3: Identify duplicates
    logger.info("Identifying entities that need to be merged to canonical names...")
    all_merge_operations = identify_duplicates_for_canonical(
        database_entities,
        canonical_entities,
        canonical_entity_types
    )
    logger.info(f"Found {len(all_merge_operations)} merge operations needed")

    # Calculate statistics
    total_entities_to_merge = sum(len(op["entities_to_change"]) for op in all_merge_operations)

    # Count by entity type
    merge_ops_by_type = defaultdict(int)
    entities_to_merge_by_type = defaultdict(int)
    for op in all_merge_operations:
        merge_ops_by_type[op["entity_type"]] += 1
        entities_to_merge_by_type[op["entity_type"]] += len(op["entities_to_change"])

    logger.info("\nSummary:")
    logger.info(f"  Total merge operations: {len(all_merge_operations)}")
    logger.info(f"  Total entities to merge: {total_entities_to_merge}")
    logger.info("  Breakdown by entity type:")
    for entity_type in sorted(merge_ops_by_type.keys()):
        ops_count = merge_ops_by_type[entity_type]
        entities_count = entities_to_merge_by_type[entity_type]
        logger.info(f"    {entity_type}: {ops_count} operations, {entities_count} entities to merge")

    if args.dry_run:
        logger.info("\nDRY RUN - Would create the following merge operations:")
        for op in all_merge_operations[:10]:  # Show first 10
            logger.info(
                f"  [{op['entity_type']}] {op['entities_to_change']} -> {op['entity_to_change_into']}"
            )
        if len(all_merge_operations) > 10:
            logger.info(f"  ... and {len(all_merge_operations) - 10} more")
        return

    # Save to file
    output_file = save_merge_operations(all_merge_operations, args.output_dir)
    logger.info(f"\nMerge operations saved to: {output_file}")
    logger.info(f"Total size: {len(all_merge_operations)} operations")


if __name__ == "__main__":
    asyncio.run(main())
