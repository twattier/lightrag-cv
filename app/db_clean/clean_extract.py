"""
Entity Regex Extractor

Extracts entities from the LightRAG knowledge graph that match regex patterns
for entity_name and/or entity_type. Outputs results to JSON file for use with
clean_list.py for deletion.

Usage:
    python -m app.db_clean.clean_extract [options]

Arguments:
    --name TEXT         Regex pattern for entity name matching (optional)
    --type TEXT         Regex pattern for entity type matching (optional)
    --output-dir PATH   Output directory for JSON file (default: data/db_clean)
    --dry-run           Show matching entities without writing file
    --verbose           Enable verbose logging

Examples:
    # Extract all CV entities
    python -m app.db_clean.clean_extract --name "cv_.*"

    # Extract all DOMAIN_PROFILE entities
    python -m app.db_clean.clean_extract --type "DOMAIN_PROFILE"

    # Extract PROFILE entities with "Architect" in name
    python -m app.db_clean.clean_extract --name ".*Architect.*" --type "PROFILE"

    # Dry-run to preview matches
    python -m app.db_clean.clean_extract --name "cv_.*" --dry-run

Output:
    JSON file: data/db_clean/clean_extract_{datetime}.json

    Format:
    [
        {
            "entity_name": "cv_duplicate_001",
            "entity_type": "CV",
            "relationship_count": 0
        }
    ]

Note:
    At least one of --name or --type must be provided.
    Regex patterns use PostgreSQL POSIX syntax.
"""

import argparse
import asyncio
import json
import logging
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


async def fetch_entities_by_regex(
    name_pattern: str | None = None,
    type_pattern: str | None = None
) -> list[dict[str, Any]]:
    """
    Fetch entities from knowledge graph matching regex patterns.

    Args:
        name_pattern: Regex pattern for entity_name (optional)
        type_pattern: Regex pattern for entity_type (optional)

    Returns:
        List of entities with their relationship counts

    Raises:
        ValueError: If both patterns are None
        asyncpg.PostgresError: If database query fails
    """
    if name_pattern is None and type_pattern is None:
        raise ValueError("At least one of name_pattern or type_pattern must be provided")

    conn = await asyncpg.connect(settings.postgres_dsn)

    try:
        # Load AGE extension for graph queries
        await conn.execute("LOAD 'age';")
        await conn.execute("SET search_path = ag_catalog, '$user', public;")

        # Build WHERE clause with regex filters
        filters = []
        if name_pattern:
            filters.append(
                f"trim(both '\"' from agtype_access_operator(properties, '\"entity_id\"')::text) ~ '{name_pattern}'"
            )
        if type_pattern:
            filters.append(
                f"trim(both '\"' from agtype_access_operator(properties, '\"entity_type\"')::text) ~ '{type_pattern}'"
            )

        where_clause = " AND ".join(filters) if filters else "TRUE"

        # Query to find entities matching regex patterns and count their relationships
        query = f"""
        WITH filtered_entities AS (
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
            FROM filtered_entities e
            LEFT JOIN chunk_entity_relation."DIRECTED" r
                ON r.start_id = e.id OR r.end_id = e.id
            GROUP BY e.entity_name, e.entity_type
        )
        SELECT entity_name, entity_type, relationship_count
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


def save_extracted_entities(
    entities: list[dict[str, Any]],
    output_dir: str = "data/db_clean"
) -> Path:
    """
    Save extracted entities to JSON file with timestamp.

    Args:
        entities: List of entity dictionaries
        output_dir: Output directory path

    Returns:
        Path to the created file
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"clean_extract_{timestamp}.json"
    filepath = output_path / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(entities, f, indent=2, ensure_ascii=False)

    return filepath


async def main() -> None:
    """Main entry point for entity regex extraction."""
    parser = argparse.ArgumentParser(
        description="Extract entities from LightRAG knowledge graph using regex patterns"
    )
    parser.add_argument(
        "--name",
        help="Regex pattern for entity name matching (PostgreSQL POSIX syntax)"
    )
    parser.add_argument(
        "--type",
        help="Regex pattern for entity type matching (PostgreSQL POSIX syntax)"
    )
    parser.add_argument(
        "--output-dir",
        default="data/db_clean",
        help="Output directory for JSON file (default: data/db_clean)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show matching entities without writing file"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Validate at least one pattern is provided
    if not args.name and not args.type:
        parser.error("At least one of --name or --type must be provided")

    logger.info("Starting entity extraction")
    if args.name:
        logger.info(f"Name pattern: {args.name}")
    if args.type:
        logger.info(f"Type pattern: {args.type}")

    # Fetch entities matching regex patterns
    try:
        logger.info("Querying PostgreSQL for matching entities...")
        entities = await fetch_entities_by_regex(args.name, args.type)
        logger.info(f"Found {len(entities)} matching entities")
    except asyncpg.PostgresError as e:
        logger.error(f"Database query failed: {e}")
        return
    except ValueError as e:
        logger.error(f"Invalid arguments: {e}")
        return

    if len(entities) == 0:
        logger.info("No entities matched the specified patterns")
        return

    # Calculate and log summary statistics
    entity_counts_by_type = defaultdict(int)
    total_relationships = 0
    for entity in entities:
        entity_counts_by_type[entity["entity_type"]] += 1
        total_relationships += entity["relationship_count"]

    logger.info("\nSummary:")
    logger.info(f"  Total entities found: {len(entities)}")
    logger.info(f"  Total relationships: {total_relationships}")
    logger.info("  Breakdown by entity type:")
    for entity_type in sorted(entity_counts_by_type.keys()):
        count = entity_counts_by_type[entity_type]
        logger.info(f"    {entity_type}: {count} entities")

    # Handle dry-run mode
    if args.dry_run:
        logger.info("\nDRY RUN - First 10 matching entities:")
        for entity in entities[:10]:
            logger.info(
                f"  [{entity['entity_type']}] {entity['entity_name']} "
                f"(relationships: {entity['relationship_count']})"
            )
        if len(entities) > 10:
            logger.info(f"  ... and {len(entities) - 10} more")
        logger.info("\nNo file created (dry-run mode)")
        return

    # Save to file
    output_file = save_extracted_entities(entities, args.output_dir)
    logger.info(f"\nExtracted entities saved to: {output_file}")
    logger.info(f"Total entities: {len(entities)}")


if __name__ == "__main__":
    asyncio.run(main())
