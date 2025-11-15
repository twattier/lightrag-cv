"""
Entity List Deleter

Deletes entities from the LightRAG knowledge graph based on a JSON file
created by clean_extract.py. Calls the LightRAG API delete_entity endpoint
with retry logic and comprehensive error handling.

Usage:
    python -m app.db_clean.clean_list [options]

Arguments:
    --file PATH     Path to JSON file created by clean_extract.py (required)
    --dry-run       Show entities to delete without calling API
    --verbose       Enable verbose logging

Examples:
    # Delete entities from extraction file
    python -m app.db_clean.clean_list --file data/db_clean/clean_extract_20251114_120000.json

    # Dry-run to preview deletions
    python -m app.db_clean.clean_list --file data/db_clean/clean_extract_20251114_120000.json --dry-run

    # Verbose logging
    python -m app.db_clean.clean_list --file data/db_clean/clean_extract_20251114_120000.json --verbose

Output:
    Logs deletion progress and summary statistics:
    - Total entities in input file
    - Successfully deleted count
    - Failed deletions count
    - Entities not found count
    - Total API errors count

Note:
    Entity deletion is permanent and cannot be undone.
    Always use --dry-run first to preview deletions.
"""

import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import Any

import httpx

from app.shared.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_entities_from_file(filepath: str) -> list[dict[str, Any]]:
    """
    Load entities from JSON file created by clean_extract.py.

    Args:
        filepath: Path to JSON file

    Returns:
        List of entity dictionaries

    Raises:
        FileNotFoundError: If file does not exist
        json.JSONDecodeError: If file is not valid JSON
        ValueError: If JSON structure is invalid
    """
    file_path = Path(filepath)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in file {filepath}: {e.msg}",
                e.doc,
                e.pos
            )

    # Validate JSON structure
    if not isinstance(data, list):
        raise ValueError(f"Expected JSON array, got {type(data).__name__}")

    for i, entity in enumerate(data):
        if not isinstance(entity, dict):
            raise ValueError(f"Entity at index {i} is not a dictionary")
        if "entity_name" not in entity:
            raise ValueError(f"Entity at index {i} missing 'entity_name' field")

    return data


async def delete_entity(
    entity_name: str,
    client: httpx.AsyncClient
) -> tuple[bool, str]:
    """
    Delete entity via LightRAG API.

    Args:
        entity_name: Name of entity to delete
        client: httpx AsyncClient instance

    Returns:
        Tuple of (success: bool, error_type: str)
        error_type can be: "success", "not_found", "client_error", "server_error", "network_error"
    """
    try:
        response = await client.request(
            method="DELETE",
            url=f"{settings.lightrag_url}/documents/delete_entity",
            json={"entity_name": entity_name},
            timeout=10.0
        )

        if response.status_code == 200:
            return (True, "success")
        elif response.status_code == 404:
            return (False, "not_found")
        elif 400 <= response.status_code < 500:
            logger.debug(f"Client error for {entity_name}: {response.status_code} - {response.text}")
            return (False, "client_error")
        else:
            logger.debug(f"Server error for {entity_name}: {response.status_code} - {response.text}")
            return (False, "server_error")
    except httpx.HTTPError as e:
        logger.debug(f"Network error for {entity_name}: {e}")
        return (False, "network_error")


async def delete_with_retry(
    entity_name: str,
    client: httpx.AsyncClient,
    max_retries: int = 3
) -> tuple[bool, str]:
    """
    Delete entity with exponential backoff retry logic.

    Args:
        entity_name: Name of entity to delete
        client: httpx AsyncClient instance
        max_retries: Maximum number of retry attempts (default: 3)

    Returns:
        Tuple of (success: bool, error_type: str)
    """
    for retry_count in range(max_retries + 1):
        success, error_type = await delete_entity(entity_name, client)

        # Don't retry on success or not_found
        if success or error_type == "not_found":
            return (success, error_type)

        # Don't retry on client errors (4xx except 404)
        if error_type == "client_error":
            return (False, error_type)

        # Retry on server errors (5xx) and network errors
        if retry_count < max_retries:
            backoff_seconds = 2 ** retry_count
            logger.debug(
                f"Retry {retry_count + 1}/{max_retries} for entity '{entity_name}' "
                f"after {backoff_seconds}s (error: {error_type})"
            )
            await asyncio.sleep(backoff_seconds)

    return (False, error_type)


async def main() -> None:
    """Main entry point for entity deletion."""
    parser = argparse.ArgumentParser(
        description="Delete entities from LightRAG knowledge graph based on JSON file"
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path to JSON file created by clean_extract.py"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show entities to delete without calling API"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.info("Starting entity deletion")
    logger.info(f"Input file: {args.file}")

    # Load entities from JSON file
    try:
        entities = load_entities_from_file(args.file)
        logger.info(f"Loaded {len(entities)} entities from file")
    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        return
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        return
    except ValueError as e:
        logger.error(f"Invalid file structure: {e}")
        return

    if len(entities) == 0:
        logger.info("No entities to delete")
        return

    # Handle dry-run mode
    if args.dry_run:
        logger.info("\nDRY RUN - Would delete the following entities:")
        for entity in entities[:20]:  # Show first 20
            logger.info(
                f"  [{entity.get('entity_type', 'UNKNOWN')}] {entity['entity_name']} "
                f"(relationships: {entity.get('relationship_count', 0)})"
            )
        if len(entities) > 20:
            logger.info(f"  ... and {len(entities) - 20} more")
        logger.info("\nNo deletions performed (dry-run mode)")
        return

    # Delete entities with retry logic
    max_retries = getattr(settings, 'MAX_RETRIES', 3)
    logger.info(f"Deleting entities (max retries: {max_retries})...")

    stats = {
        "total": len(entities),
        "deleted": 0,
        "not_found": 0,
        "failed": 0,
        "client_errors": 0,
        "server_errors": 0,
        "network_errors": 0
    }

    async with httpx.AsyncClient() as client:
        for i, entity in enumerate(entities, 1):
            entity_name = entity["entity_name"]
            entity_type = entity.get("entity_type", "UNKNOWN")

            success, error_type = await delete_with_retry(entity_name, client, max_retries)

            if success:
                stats["deleted"] += 1
                logger.info(f"[{i}/{len(entities)}] Deleted: [{entity_type}] {entity_name}")
            elif error_type == "not_found":
                stats["not_found"] += 1
                logger.warning(f"[{i}/{len(entities)}] Not found: [{entity_type}] {entity_name}")
            else:
                stats["failed"] += 1
                if error_type == "client_error":
                    stats["client_errors"] += 1
                elif error_type == "server_error":
                    stats["server_errors"] += 1
                elif error_type == "network_error":
                    stats["network_errors"] += 1

                logger.error(
                    f"[{i}/{len(entities)}] Failed ({error_type}): [{entity_type}] {entity_name}"
                )

    # Log summary statistics
    logger.info("\n" + "=" * 60)
    logger.info("DELETION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total entities:        {stats['total']}")
    logger.info(f"Successfully deleted:  {stats['deleted']}")
    logger.info(f"Not found:             {stats['not_found']}")
    logger.info(f"Failed:                {stats['failed']}")
    if stats['failed'] > 0:
        logger.info(f"  - Client errors:     {stats['client_errors']}")
        logger.info(f"  - Server errors:     {stats['server_errors']}")
        logger.info(f"  - Network errors:    {stats['network_errors']}")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
