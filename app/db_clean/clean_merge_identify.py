"""
Generic Entity Duplicate Identifier (Database-querying)

Identifies duplicate entities in the LightRAG knowledge graph that differ
in character case or separators (e.g., "APPLICATION_LIFE_CYCLE" vs "Application Life Cycle").

This is a generic implementation that queries the Apache AGE graph database directly
and can work with any entity types. It supports cross-type merging and advanced
filtering options.

Usage:
    python -m app.db_clean.clean_merge_identify [options]

Arguments:
    --entity-types TEXT   Comma-separated entity types to process (default: "DOMAIN_PROFILE,PROFILE")
    --all-types           Search for duplicates across ALL entity types
    --merge-across-types  Merge entities with same name but different types
    --prefer-types TEXT   Comma-separated entity types to prefer as canonical
    --output-dir PATH     Output directory for JSON file (default: data/db_clean)
    --dry-run             Show what would be identified without writing file
    --verbose             Enable verbose logging

Output:
    JSON file: data/db_clean/clean_merge_identify_{datetime}.json

    Format:
    [
        {
            "entity_to_change_into": "APPLICATION LIFE CYCLE",
            "entities_to_change": ["Application_Life_Cycle", "application_life_cycle"],
            "relationship_counts": {"APPLICATION LIFE CYCLE": 25, "Application_Life_Cycle": 10},
            "entity_type": "DOMAIN_PROFILE",
            "entity_types_involved": ["DOMAIN_PROFILE", "concept"],
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


async def fetch_cigref_entities(
    entity_types: list[str] | None = None
) -> list[dict[str, Any]]:
    """
    Fetch all CIGREF entities from the knowledge graph.

    Args:
        entity_types: List of entity types to fetch (e.g., ['DOMAIN_PROFILE', 'PROFILE']).
                     If None, fetches all entity types.

    Returns:
        List of entities with their relationship counts and types
    """
    conn = await asyncpg.connect(settings.postgres_dsn)

    try:
        # Load AGE extension for graph queries
        await conn.execute("LOAD 'age';")
        await conn.execute("SET search_path = ag_catalog, '$user', public;")

        # Build entity type filter for SQL query
        if entity_types is None:
            # Fetch all entity types
            where_clause = "TRUE"
        else:
            entity_type_filters = " OR ".join([
                f"agtype_access_operator(properties, '\"entity_type\"')::text = '\"{et}\"'"
                for et in entity_types
            ])
            where_clause = entity_type_filters

        # Query to find all CIGREF entities and count their relationships from Apache AGE graph
        query = f"""
        WITH cigref_entities AS (
            SELECT
                id,
                trim(both '"' from agtype_access_operator(properties, '"entity_id"')::text) as entity_name,
                trim(both '"' from agtype_access_operator(properties, '"entity_type"')::text) as entity_type
            FROM chunk_entity_relation.base
            WHERE {where_clause}
        ),
        entity_rel_counts AS (
            SELECT
                e.entity_name,
                e.entity_type,
                COUNT(DISTINCT r.id) as relationship_count
            FROM cigref_entities e
            LEFT JOIN chunk_entity_relation."DIRECTED" r
                ON r.start_id = e.id OR r.end_id = e.id
            GROUP BY e.entity_name, e.entity_type
        )
        SELECT
            entity_name,
            entity_type,
            relationship_count
        FROM entity_rel_counts
        ORDER BY entity_type, entity_name
        """

        rows = await conn.fetch(query)

        return [
            {
                "entity_name": row["entity_name"],
                "entity_type": row["entity_type"],
                "relationship_count": row["relationship_count"]
            }
            for row in rows
        ]
    finally:
        await conn.close()


def identify_duplicates_by_normalization(
    entities: list[dict[str, Any]],
    merge_across_types: bool = False,
    target_entity_types: list[str] | None = None
) -> list[dict[str, Any]]:
    """
    Group entities by normalized name and identify duplicates.

    Normalizes entity names by converting to lowercase and removing separators,
    then groups entities that have the same normalized form.

    Args:
        entities: List of entity dictionaries with entity_name, entity_type, and relationship_count
        merge_across_types: If True, merge entities with same name but different types
        target_entity_types: List of preferred entity types (e.g., ['DOMAIN_PROFILE', 'PROFILE'])
                            These types will be prioritized as canonical entities

    Returns:
        List of merge operations to perform
    """
    if merge_across_types:
        # Group only by normalized name (ignore entity type)
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)

        for entity in entities:
            normalized_key = normalize_entity_name(entity["entity_name"])
            entity_with_norm = entity.copy()
            entity_with_norm["normalized_name"] = normalized_key
            groups[normalized_key].append(entity_with_norm)

        # Identify groups with duplicates
        merge_operations = []

        for normalized_name, entity_list in groups.items():
            if len(entity_list) > 1:
                # Sort by priority for canonical entity selection:
                # 1. Prefer target entity types (DOMAIN_PROFILE, PROFILE)
                # 2. Then by relationship count (descending)
                # 3. Then alphabetically
                def sort_key(entity):
                    # Priority 1: Is it a target entity type?
                    is_target_type = (
                        1 if target_entity_types and entity["entity_type"] in target_entity_types
                        else 0
                    )
                    # Priority 2: Relationship count
                    rel_count = entity["relationship_count"]
                    # Priority 3: Entity name (for deterministic ordering)
                    name = entity["entity_name"]

                    return (is_target_type, rel_count, name)

                # Sort by relationship count only (descending)
                sorted_by_relationships = sorted(
                    entity_list,
                    key=lambda x: (x["relationship_count"], x["entity_name"]),
                    reverse=True
                )

                # Select canonical entity (entity with most relationships)
                canonical_entity = sorted_by_relationships[0]["entity_name"]
                canonical_type = sorted_by_relationships[0]["entity_type"]

                # If target entity types are specified, prefer those types for entity_type field
                if target_entity_types:
                    target_entities = [e for e in sorted_by_relationships if e["entity_type"] in target_entity_types]
                    if target_entities:
                        # Use the entity type from target types (e.g., DOMAIN_PROFILE or PROFILE)
                        canonical_type = target_entities[0]["entity_type"]

                entities_to_merge = [
                    e["entity_name"]
                    for e in sorted_by_relationships
                    if e["entity_name"] != canonical_entity
                ]

                # Collect all entity types involved
                entity_types_involved = list(set(e["entity_type"] for e in sorted_by_relationships))

                merge_operations.append({
                    "entity_to_change_into": canonical_entity,
                    "entities_to_change": entities_to_merge,
                    "relationship_counts": {
                        e["entity_name"]: e["relationship_count"]
                        for e in sorted_by_relationships
                    },
                    "entity_type": canonical_type,
                    "entity_types_involved": entity_types_involved,
                    "normalized_name": normalized_name  # Use the lowercase normalized form
                })

        return merge_operations

    # Original behavior: Group by (normalized_name, entity_type) to handle each type separately
    groups_by_type: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)

    for entity in entities:
        # Normalize entity name to detect case and separator variations
        normalized_key = normalize_entity_name(entity["entity_name"])
        entity_type = entity["entity_type"]

        # Add normalized name to entity for reference
        entity_with_norm = entity.copy()
        entity_with_norm["normalized_name"] = normalized_key

        groups_by_type[(normalized_key, entity_type)].append(entity_with_norm)

    # Identify groups with duplicates
    merge_operations = []

    for (normalized_name, entity_type), entity_list in groups_by_type.items():
        if len(entity_list) > 1:
            # Sort by relationship count (descending) to pick canonical entity
            sorted_entities = sorted(
                entity_list,
                key=lambda x: (
                    x["relationship_count"],  # Primary: most relationships
                    x["entity_name"]          # Secondary: alphabetically first
                ),
                reverse=True
            )

            canonical_entity = sorted_entities[0]["entity_name"]
            entities_to_merge = [e["entity_name"] for e in sorted_entities[1:]]

            merge_operations.append({
                "entity_to_change_into": canonical_entity,
                "entities_to_change": entities_to_merge,
                "relationship_counts": {
                    e["entity_name"]: e["relationship_count"]
                    for e in sorted_entities
                },
                "entity_type": entity_type,
                "normalized_name": normalized_name
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
    filename = f"clean_merge_identify_{timestamp}.json"
    filepath = output_path / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(merge_operations, f, indent=2, ensure_ascii=False)

    return filepath


async def main() -> None:
    """Main entry point for generic entity duplicate identification."""
    parser = argparse.ArgumentParser(
        description="Identify duplicate entities in LightRAG knowledge graph"
    )
    parser.add_argument(
        "--entity-types",
        default="DOMAIN_PROFILE,PROFILE",
        help="Comma-separated entity types to process (default: DOMAIN_PROFILE,PROFILE). Use 'ALL' to search all types."
    )
    parser.add_argument(
        "--all-types",
        action="store_true",
        help="Search for duplicates across ALL entity types (overrides --entity-types)"
    )
    parser.add_argument(
        "--merge-across-types",
        action="store_true",
        help="Merge entities with same name but different types (e.g., 'Programmer' person + 'PROGRAMMER' PROFILE)"
    )
    parser.add_argument(
        "--prefer-types",
        help="Comma-separated entity types to prefer as canonical when merging across types (e.g., 'DOMAIN_PROFILE,PROFILE')"
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

    # Parse entity types
    if args.all_types or args.entity_types.upper() == "ALL":
        entity_types = None  # Will fetch all types
        logger.info("Starting entity duplicate identification (ALL TYPES)")
    else:
        entity_types = [et.strip() for et in args.entity_types.split(",")]
        logger.info("Starting entity duplicate identification")
        logger.info(f"Entity types: {entity_types}")

    # Fetch entities from database
    logger.info("Fetching CIGREF entities from PostgreSQL...")
    entities = await fetch_cigref_entities(entity_types)
    logger.info(f"Found {len(entities)} CIGREF entities")

    # Log entity distribution by type
    entity_counts_by_type = defaultdict(int)
    for entity in entities:
        entity_counts_by_type[entity["entity_type"]] += 1

    logger.info("Entity distribution by type:")
    for entity_type, count in sorted(entity_counts_by_type.items(), key=lambda x: x[1], reverse=True):
        logger.info(f"  {entity_type}: {count} entities")

    # Identify duplicates with normalization
    # Determine preferred entity types for canonical selection
    preferred_types = None
    if args.prefer_types:
        preferred_types = [pt.strip() for pt in args.prefer_types.split(",")]
    elif args.merge_across_types and entity_types and entity_types != ['ALL']:
        # If merging across types with specific entity-types filter, use those as preferred
        preferred_types = entity_types

    if args.merge_across_types:
        logger.info("Identifying duplicates with case and separator variations (merging across entity types)...")
        if preferred_types:
            logger.info(f"Prioritizing entity types as canonical: {preferred_types}")
    else:
        logger.info("Identifying duplicates with case and separator variations...")

    all_merge_operations = identify_duplicates_by_normalization(
        entities,
        merge_across_types=args.merge_across_types,
        target_entity_types=preferred_types
    )
    logger.info(f"Found {len(all_merge_operations)} duplicate groups")

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

    if entity_types is not None:
        for entity_type in entity_types:
            ops_count = merge_ops_by_type[entity_type]
            entities_count = entities_to_merge_by_type[entity_type]
            logger.info(f"  {entity_type}: {ops_count} operations, {entities_count} entities to merge")
    else:
        logger.info("  Breakdown by entity type:")
        for entity_type in sorted(merge_ops_by_type.keys()):
            ops_count = merge_ops_by_type[entity_type]
            entities_count = entities_to_merge_by_type[entity_type]
            logger.info(f"    {entity_type}: {ops_count} operations, {entities_count} entities to merge")

    logger.info(f"  Entities remaining after merge: {len(entities) - total_entities_to_merge}")

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
