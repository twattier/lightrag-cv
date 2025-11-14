"""
CV Entity Duplicate Identifier

Identifies duplicate CV entities in the LightRAG knowledge graph that differ
only in character case (e.g., CV_001, Cv_001, cv_001).

Usage:
    python -m app.db_clean.cv1_merge_identify [options]

Arguments:
    --cv-pattern TEXT     CV ID pattern to search (default: "CV_%")
    --min-cv-id INT       Minimum CV ID number to process (default: 1)
    --max-cv-id INT       Maximum CV ID number to process (default: 999)
    --output-dir PATH     Output directory for JSON file (default: data/db_clean)
    --dry-run             Show what would be identified without writing file
    --verbose             Enable verbose logging

Output:
    JSON file: data/db_clean/cv_merge_identify_{datetime}.json

    Format:
    [
        {
            "entity_to_change_into": "CV_001",
            "entities_to_change": ["Cv_001", "cv_001"],
            "relationship_counts": {"CV_001": 15, "Cv_001": 3, "cv_001": 1}
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


async def fetch_cv_entities(
    min_cv_id: int = 1,
    max_cv_id: int = 999,
    pattern: str = "CV_%"
) -> list[dict[str, Any]]:
    """
    Fetch all CV entities from the knowledge graph.

    Args:
        min_cv_id: Minimum CV ID number to process
        max_cv_id: Maximum CV ID number to process
        pattern: SQL pattern to match entity names

    Returns:
        List of entities with their relationship counts
    """
    conn = await asyncpg.connect(settings.postgres_dsn)

    try:
        # Load AGE extension for graph queries
        await conn.execute("LOAD 'age';")
        await conn.execute("SET search_path = ag_catalog, '$user', public;")

        # Query to find all CV entities and count their relationships from Apache AGE graph
        # Note: LightRAG stores the actual graph in Apache AGE (chunk_entity_relation graph)
        # Entities are in chunk_entity_relation.base table with JSONB properties
        # Relationships are in chunk_entity_relation."DIRECTED" table
        query = """
        WITH cv_entities AS (
            SELECT
                id,
                agtype_access_operator(properties, '"entity_id"')::text as entity_name_raw
            FROM chunk_entity_relation.base
        ),
        cv_filtered AS (
            SELECT
                id,
                trim(both '"' from entity_name_raw) as entity_name
            FROM cv_entities
            WHERE entity_name_raw ILIKE $1
        ),
        entity_rel_counts AS (
            SELECT
                e.entity_name,
                COUNT(DISTINCT r.id) as relationship_count
            FROM cv_filtered e
            LEFT JOIN chunk_entity_relation."DIRECTED" r
                ON r.start_id = e.id OR r.end_id = e.id
            GROUP BY e.entity_name
        )
        SELECT
            entity_name,
            relationship_count
        FROM entity_rel_counts
        ORDER BY entity_name
        """

        rows = await conn.fetch(query, pattern)

        return [
            {
                "entity_name": row["entity_name"],
                "relationship_count": row["relationship_count"]
            }
            for row in rows
        ]
    finally:
        await conn.close()


def identify_duplicates(entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group entities by case-insensitive name and identify duplicates.

    Args:
        entities: List of entity dictionaries with entity_name and relationship_count

    Returns:
        List of merge operations to perform
    """
    # Group by lowercase entity name
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for entity in entities:
        # Normalize entity name to detect case variations
        normalized_key = entity["entity_name"].lower()
        groups[normalized_key].append(entity)

    # Identify groups with duplicates
    merge_operations = []

    for normalized_name, entity_list in groups.items():
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
                }
            })

    return merge_operations


async def detect_candidate_prefix_duplicates(
    all_cv_entities: list[dict[str, Any]],
    postgres_dsn: str
) -> list[dict[str, Any]]:
    """
    Detect entities with "Candidate CV_XXX" pattern that duplicate "CV_XXX".

    Fetches "Candidate" entities from AGE graph and matches them with CV entities.

    Args:
        all_cv_entities: List of CV entity dictionaries with entity_name and relationship_count
        postgres_dsn: PostgreSQL connection string

    Returns:
        Additional merge operations for candidate prefix variants
    """
    conn = await asyncpg.connect(postgres_dsn)

    try:
        await conn.execute("LOAD 'age';")
        await conn.execute("SET search_path = ag_catalog, '$user', public;")

        # Fetch all "Candidate CV" entities from AGE graph
        candidate_rows = await conn.fetch("""
            WITH candidate_entities AS (
                SELECT
                    id,
                    trim(both '"' from agtype_access_operator(properties, '"entity_id"')::text) as entity_name
                FROM chunk_entity_relation.base
                WHERE agtype_access_operator(properties, '"entity_id"')::text ILIKE '%Candidate%CV%'
            ),
            entity_rel_counts AS (
                SELECT
                    e.entity_name,
                    COUNT(DISTINCT r.id) as relationship_count
                FROM candidate_entities e
                LEFT JOIN chunk_entity_relation."DIRECTED" r
                    ON r.start_id = e.id OR r.end_id = e.id
                GROUP BY e.entity_name
            )
            SELECT entity_name, relationship_count FROM entity_rel_counts
        """)

        candidate_entities_from_db = [
            {
                "entity_name": row["entity_name"],
                "relationship_count": row["relationship_count"]
            }
            for row in candidate_rows
        ]

    finally:
        await conn.close()

    # Create lookup by CV ID
    cv_entities: dict[str, dict[str, Any]] = {}
    candidate_entities: dict[str, list[dict[str, Any]]] = {}

    # Pattern to match CV_XXX (with or without underscore, case-insensitive)
    cv_pattern = re.compile(r'^(CV)[_\s]?(\d+)$', re.IGNORECASE)
    # Pattern to match "Candidate CV XXX" with flexible spacing/underscore
    candidate_pattern = re.compile(r'^Candidate\s+(CV)[_\s]?(\d+)$', re.IGNORECASE)

    # Build lookup of base CV entities
    for entity in all_cv_entities:
        name = entity["entity_name"]
        cv_match = cv_pattern.match(name)
        if cv_match:
            # Normalize to CV_XXX format
            cv_id = f"CV_{cv_match.group(2)}"
            if cv_id not in cv_entities or entity["relationship_count"] > cv_entities[cv_id]["relationship_count"]:
                cv_entities[cv_id] = entity

    # Group candidate entities by CV ID
    for entity in candidate_entities_from_db:
        name = entity["entity_name"]
        candidate_match = candidate_pattern.match(name)
        if candidate_match:
            # Normalize to CV_XXX format
            cv_id = f"CV_{candidate_match.group(2)}"
            if cv_id not in candidate_entities:
                candidate_entities[cv_id] = []
            candidate_entities[cv_id].append(entity)

    # Create merge operations for candidate variants
    merge_operations = []

    for cv_id, candidate_list in candidate_entities.items():
        if cv_id in cv_entities:
            # Merge into the base CV entity
            canonical = cv_entities[cv_id]["entity_name"]
            entities_to_merge = [e["entity_name"] for e in candidate_list]

            relationship_counts = {
                cv_entities[cv_id]["entity_name"]: cv_entities[cv_id]["relationship_count"]
            }
            for e in candidate_list:
                relationship_counts[e["entity_name"]] = e["relationship_count"]

            merge_operations.append({
                "entity_to_change_into": canonical,
                "entities_to_change": entities_to_merge,
                "relationship_counts": relationship_counts,
                "note": "Merging 'Candidate CV_XXX' variant into base CV entity"
            })

    return merge_operations


def consolidate_merge_operations(
    cv_entities: list[dict[str, Any]],
    candidate_merge_ops: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Consolidate CV case variations and Candidate variants into unified merge operations.

    Groups all entities by normalized CV ID (e.g., CV_001, CV_012) and creates
    a single merge operation per CV ID that includes both case variations
    (cv_001, Cv_001, CV_001) and candidate variants (Candidate CV_001).

    Args:
        cv_entities: List of CV entity dictionaries from AGE graph
        candidate_merge_ops: List of candidate merge operations

    Returns:
        List of consolidated merge operations, one per CV ID
    """
    # Pattern to extract CV ID and normalize it
    cv_pattern = re.compile(r'^(CV)[_\s]?(\d+)$', re.IGNORECASE)

    # Group all entities by normalized CV ID
    cv_groups: dict[str, list[dict[str, Any]]] = {}

    # Add base CV entities
    for entity in cv_entities:
        cv_match = cv_pattern.match(entity["entity_name"])
        if cv_match:
            cv_id = f"CV_{cv_match.group(2)}"  # Normalize to CV_XXX
            if cv_id not in cv_groups:
                cv_groups[cv_id] = []
            cv_groups[cv_id].append(entity)

    # Add candidate entities from merge operations
    for candidate_op in candidate_merge_ops:
        # Extract CV ID from the canonical entity name
        canonical = candidate_op["entity_to_change_into"]
        cv_match = cv_pattern.match(canonical)
        if cv_match:
            cv_id = f"CV_{cv_match.group(2)}"
            # Add all candidate entities to the group
            for candidate_name in candidate_op["entities_to_change"]:
                # Find the entity with this name in relationship_counts
                rel_count = candidate_op["relationship_counts"].get(candidate_name, 0)
                cv_groups[cv_id].append({
                    "entity_name": candidate_name,
                    "relationship_count": rel_count
                })

    # Create unified merge operations
    merge_operations = []

    for cv_id, entity_list in cv_groups.items():
        if len(entity_list) <= 1:
            # No duplicates for this CV ID
            continue

        # Sort by relationship count (descending), then alphabetically
        sorted_entities = sorted(
            entity_list,
            key=lambda x: (
                x["relationship_count"],  # Primary: most relationships
                x["entity_name"]          # Secondary: alphabetically first
            ),
            reverse=True
        )

        # Remove duplicates (same entity name might appear in both lists)
        seen_names = set()
        unique_entities = []
        for entity in sorted_entities:
            if entity["entity_name"] not in seen_names:
                seen_names.add(entity["entity_name"])
                unique_entities.append(entity)

        if len(unique_entities) <= 1:
            # After deduplication, no merge needed
            continue

        canonical_entity = unique_entities[0]["entity_name"]
        entities_to_merge = [e["entity_name"] for e in unique_entities[1:]]

        merge_operations.append({
            "entity_to_change_into": canonical_entity,
            "entities_to_change": entities_to_merge,
            "relationship_counts": {
                e["entity_name"]: e["relationship_count"]
                for e in unique_entities
            },
            "cv_id": cv_id
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
    filename = f"cv_merge_identify_{timestamp}.json"
    filepath = output_path / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(merge_operations, f, indent=2, ensure_ascii=False)

    return filepath


async def main() -> None:
    """Main entry point for CV entity duplicate identification."""
    parser = argparse.ArgumentParser(
        description="Identify duplicate CV entities in LightRAG knowledge graph"
    )
    parser.add_argument(
        "--cv-pattern",
        default="CV_%",
        help="CV ID pattern to search (default: CV_%%)"
    )
    parser.add_argument(
        "--min-cv-id",
        type=int,
        default=1,
        help="Minimum CV ID number (default: 1)"
    )
    parser.add_argument(
        "--max-cv-id",
        type=int,
        default=999,
        help="Maximum CV ID number (default: 999)"
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

    logger.info("Starting CV entity duplicate identification")
    logger.info(f"Pattern: {args.cv_pattern}, Range: {args.min_cv_id}-{args.max_cv_id}")

    # Fetch entities from database
    logger.info("Fetching CV entities from PostgreSQL...")
    entities = await fetch_cv_entities(
        min_cv_id=args.min_cv_id,
        max_cv_id=args.max_cv_id,
        pattern=args.cv_pattern
    )
    logger.info(f"Found {len(entities)} CV entities")

    # Fetch all "Candidate CV" entities to include in unified merge operations
    logger.info("Fetching 'Candidate CV_XXX' entities...")
    candidate_duplicates = await detect_candidate_prefix_duplicates(entities, settings.postgres_dsn)
    logger.info(f"Found {len(candidate_duplicates)} candidate groups")

    # Combine CV entities and Candidate entities for unified processing
    logger.info("Creating unified merge operations by CV ID...")
    all_merge_operations = consolidate_merge_operations(entities, candidate_duplicates)

    # Calculate statistics
    total_entities_to_merge = sum(len(op["entities_to_change"]) for op in all_merge_operations)

    logger.info(f"\nSummary:")
    logger.info(f"  Total merge operations: {len(all_merge_operations)}")
    logger.info(f"  Total entities to merge: {total_entities_to_merge}")
    logger.info(f"  Entities remaining after merge: {len(entities) - total_entities_to_merge}")

    if args.dry_run:
        logger.info("\nDRY RUN - Would create the following merge operations:")
        for op in all_merge_operations:
            logger.info(f"  {op['entities_to_change']} -> {op['entity_to_change_into']}")
        return

    # Save to file
    output_file = save_merge_operations(all_merge_operations, args.output_dir)
    logger.info(f"\nMerge operations saved to: {output_file}")
    logger.info(f"Total size: {len(all_merge_operations)} operations")


if __name__ == "__main__":
    asyncio.run(main())
