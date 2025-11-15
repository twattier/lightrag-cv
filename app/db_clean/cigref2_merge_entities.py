"""
CIGREF Entity Merge Executor

Executes entity merge operations on the LightRAG knowledge graph using
the /graph/entities/merge API endpoint.

Usage:
    python -m app.db_clean.cigref2_merge_entities --file data/db_clean/cigref_merge_identify_20250114_103045.json

Arguments:
    --file PATH          Path to merge operations JSON file (required)
    --api-url URL        LightRAG API base URL (default: from settings)
    --dry-run            Show what would be merged without executing
    --batch-size INT     Number of operations per batch (default: 10)
    --retry-attempts INT Max retry attempts for failed operations (default: 3)
    --verbose            Enable verbose logging

Output:
    Console logs with merge results
    JSON report: data/db_clean/cigref_merge_report_{datetime}.json
"""

import argparse
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, TypeVar

import aiohttp

from app.shared.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

T = TypeVar('T')


def load_merge_operations(file_path: str) -> list[dict[str, Any]]:
    """
    Load merge operations from JSON file.

    Args:
        file_path: Path to the merge operations JSON file

    Returns:
        List of merge operation dictionaries

    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the JSON structure is invalid
    """
    filepath = Path(file_path)

    if not filepath.exists():
        raise FileNotFoundError(f"Merge operations file not found: {file_path}")

    with open(filepath, "r", encoding="utf-8") as f:
        operations = json.load(f)

    # Validate structure
    for idx, op in enumerate(operations):
        if "entity_to_change_into" not in op:
            raise ValueError(f"Operation {idx}: missing 'entity_to_change_into'")
        if "entities_to_change" not in op:
            raise ValueError(f"Operation {idx}: missing 'entities_to_change'")
        if not isinstance(op["entities_to_change"], list):
            raise ValueError(f"Operation {idx}: 'entities_to_change' must be a list")

    return operations


class LightRAGClient:
    """Client for LightRAG API operations."""

    def __init__(self, base_url: str | None = None):
        """
        Initialize LightRAG client.

        Args:
            base_url: Base URL for LightRAG API. If None, uses settings.
        """
        self.base_url = base_url or getattr(settings, 'lightrag_api_url', "http://localhost:9621")

    async def merge_entities(
        self,
        entities_to_change: list[str],
        entity_to_change_into: str
    ) -> dict[str, Any]:
        """
        Merge multiple entities into a single entity.

        Args:
            entities_to_change: List of entity names to merge and delete
            entity_to_change_into: Target entity that will receive all relationships

        Returns:
            API response dictionary

        Raises:
            aiohttp.ClientError: On API request failure
        """
        url = f"{self.base_url}/graph/entities/merge"

        payload = {
            "entities_to_change": entities_to_change,
            "entity_to_change_into": entity_to_change_into
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                response_data = await response.json()

                if response.status != 200:
                    raise aiohttp.ClientError(
                        f"API returned status {response.status}: {response_data}"
                    )

                return response_data

    async def edit_entity(
        self,
        entity_name: str,
        new_entity_name: str,
        entity_type: str
    ) -> dict[str, Any]:
        """
        Edit entity name and type using LightRAG API.

        Args:
            entity_name: Current entity name
            new_entity_name: New entity name (canonical name)
            entity_type: New entity type (DOMAIN_PROFILE or PROFILE)

        Returns:
            API response dictionary

        Raises:
            aiohttp.ClientError: On API request failure
        """
        url = f"{self.base_url}/graph/entity/edit"

        payload = {
            "entity_name": entity_name,
            "updated_data": {
                "entity_name": new_entity_name,
                "entity_type": entity_type
            },
            "allow_rename": True,
            "allow_merge": False
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                response_data = await response.json()

                if response.status != 200:
                    raise aiohttp.ClientError(
                        f"API returned status {response.status}: {response_data}"
                    )

                return response_data


async def retry_with_backoff(
    func: Callable[..., T],
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    *args: Any,
    **kwargs: Any
) -> T:
    """
    Retry a function with exponential backoff.

    Args:
        func: Async function to retry
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each attempt
        *args: Positional arguments to pass to func
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result of the function call

    Raises:
        Last exception if all attempts fail
    """
    delay = initial_delay
    last_exception = None

    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < max_attempts:
                logger.warning(
                    f"Attempt {attempt}/{max_attempts} failed: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                await asyncio.sleep(delay)
                delay *= backoff_factor
            else:
                logger.error(f"All {max_attempts} attempts failed")

    if last_exception:
        raise last_exception
    raise RuntimeError("Retry failed without exception")


async def execute_merge_operations(
    operations: list[dict[str, Any]],
    client: LightRAGClient,
    batch_size: int = 10,
    retry_attempts: int = 3,
    dry_run: bool = False
) -> dict[str, Any]:
    """
    Execute all merge operations with batching and error tracking.

    Args:
        operations: List of merge operation dictionaries
        client: LightRAG API client
        batch_size: Number of concurrent operations
        retry_attempts: Max retry attempts per operation
        dry_run: If True, only simulate operations

    Returns:
        Summary dictionary with success/failure counts
    """
    results: dict[str, Any] = {
        "total": len(operations),
        "successful": 0,
        "failed": 0,
        "details": []
    }

    for i in range(0, len(operations), batch_size):
        batch = operations[i:i + batch_size]

        logger.info(f"Processing batch {i // batch_size + 1} ({len(batch)} operations)")

        for op in batch:
            entity_to_change_into = op["entity_to_change_into"]
            entities_to_change = op["entities_to_change"]
            entity_type = op.get("entity_type", "UNKNOWN")
            normalized_name = op.get("normalized_name")

            result: dict[str, Any] = {
                "entity_to_change_into": entity_to_change_into,
                "entities_to_change": entities_to_change,
                "entity_type": entity_type,
                "normalized_name": normalized_name,
                "status": None,
                "message": None,
                "relationships_transferred": None,
                "entity_updated": False,
                "update_message": None
            }

            if dry_run:
                dry_run_message = f"DRY RUN: Would merge [{entity_type}] {entities_to_change} -> {entity_to_change_into}"
                if normalized_name and normalized_name != entity_to_change_into:
                    dry_run_message += f" and rename to '{normalized_name}'"
                logger.info(dry_run_message)
                result["status"] = "dry_run"
                result["message"] = "Dry run - not executed"
                results["details"].append(result)
                continue

            try:
                # Execute merge with retry logic
                response = await retry_with_backoff(
                    client.merge_entities,
                    max_attempts=retry_attempts,
                    entities_to_change=entities_to_change,
                    entity_to_change_into=entity_to_change_into
                )

                result["status"] = "success"
                result["message"] = response.get("message", "Success")
                result["relationships_transferred"] = response.get("data", {}).get(
                    "relationships_transferred", 0
                )

                results["successful"] += 1

                logger.info(
                    f"✓ Merged {len(entities_to_change)} [{entity_type}] entities into '{entity_to_change_into}' "
                    f"({result['relationships_transferred']} relationships)"
                )

                # After successful merge, update target entity to canonical name and type if needed
                if normalized_name and normalized_name != entity_to_change_into:
                    try:
                        update_response = await retry_with_backoff(
                            client.edit_entity,
                            max_attempts=retry_attempts,
                            entity_name=entity_to_change_into,
                            new_entity_name=normalized_name,
                            entity_type=entity_type
                        )

                        result["entity_updated"] = True
                        result["update_message"] = update_response.get("message", "Updated")

                        logger.info(
                            f"  ↳ Renamed '{entity_to_change_into}' to '{normalized_name}' [{entity_type}]"
                        )

                    except Exception as update_error:
                        result["entity_updated"] = False
                        result["update_message"] = f"Update failed: {update_error}"

                        logger.warning(
                            f"  ⚠ Failed to rename '{entity_to_change_into}' to '{normalized_name}': {update_error}"
                        )

            except Exception as e:
                result["status"] = "failed"
                result["message"] = str(e)
                results["failed"] += 1

                logger.error(
                    f"✗ Failed to merge [{entity_type}] {entities_to_change} -> {entity_to_change_into}: {e}"
                )

            results["details"].append(result)

            # Small delay between operations to avoid overwhelming the API
            await asyncio.sleep(0.5)

    return results


def save_merge_report(results: dict[str, Any], output_dir: str = "data/db_clean") -> Path:
    """
    Save merge execution report to JSON file.

    Args:
        results: Results dictionary from execute_merge_operations
        output_dir: Output directory path

    Returns:
        Path to the created file
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"cigref_merge_report_{timestamp}.json"
    filepath = output_path / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    return filepath


async def main() -> None:
    """Main entry point for CIGREF entity merge execution."""
    parser = argparse.ArgumentParser(
        description="Execute CIGREF entity merge operations on LightRAG knowledge graph"
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path to merge operations JSON file"
    )
    parser.add_argument(
        "--api-url",
        help="LightRAG API base URL (default: from settings)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be merged without executing"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of operations per batch (default: 10)"
    )
    parser.add_argument(
        "--retry-attempts",
        type=int,
        default=3,
        help="Max retry attempts for failed operations (default: 3)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.info("Starting CIGREF entity merge execution")
    logger.info(f"Input file: {args.file}")

    # Load merge operations
    logger.info("Loading merge operations...")
    operations = load_merge_operations(args.file)
    logger.info(f"Loaded {len(operations)} merge operations")

    # Initialize API client
    client = LightRAGClient(base_url=args.api_url)
    logger.info(f"LightRAG API: {client.base_url}")

    if args.dry_run:
        logger.info("DRY RUN MODE - No changes will be made")

    # Execute merge operations
    logger.info("Executing merge operations...")
    results = await execute_merge_operations(
        operations=operations,
        client=client,
        batch_size=args.batch_size,
        retry_attempts=args.retry_attempts,
        dry_run=args.dry_run
    )

    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("MERGE EXECUTION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total operations: {results['total']}")
    logger.info(f"Successful: {results['successful']}")
    logger.info(f"Failed: {results['failed']}")

    # Count entity updates
    entities_updated = sum(1 for d in results['details'] if d.get('entity_updated', False))
    if entities_updated > 0:
        logger.info(f"Entities renamed to canonical names: {entities_updated}")

    if results['failed'] > 0:
        logger.warning("\nFailed operations:")
        for detail in results['details']:
            if detail['status'] == 'failed':
                logger.warning(
                    f"  - [{detail.get('entity_type', 'UNKNOWN')}] {detail['entities_to_change']} -> "
                    f"{detail['entity_to_change_into']}: {detail['message']}"
                )

    # Show update warnings
    update_failures = [d for d in results['details'] if d.get('update_message') and 'failed' in d.get('update_message', '').lower()]
    if update_failures:
        logger.warning("\nEntity rename warnings:")
        for detail in update_failures:
            logger.warning(
                f"  - '{detail['entity_to_change_into']}' -> '{detail.get('normalized_name', 'N/A')}': "
                f"{detail['update_message']}"
            )

    # Save report
    if not args.dry_run:
        report_file = save_merge_report(results)
        logger.info(f"\nDetailed report saved to: {report_file}")


if __name__ == "__main__":
    asyncio.run(main())
