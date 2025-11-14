# Story 2.8: Knowledge Graph Entity Deduplication

## Status

**Ready for Implementation** ✅

---

## User Story

**As a** developer,
**I want** to identify and merge duplicate CV entities in the knowledge graph that differ only in character case,
**so that** the knowledge graph is clean, consistent, and queries return accurate results without duplicates.

## Story Overview

**Objective:** Clean and improve the knowledge graph after LightRAG import by identifying and merging duplicate entities that differ only in character case.

**Problem:** After CV ingestion into LightRAG, duplicate entities are created with various case patterns:
- `CV_001`, `Cv_001`, `cv_001`
- `Candidate Cv_001`
- Other case variations

**Solution:** Implement a two-stage batch processing pipeline:
1. **Stage 1 (cv1_merge_identify.py):** Identify duplicate entities and determine the canonical form
2. **Stage 2 (cv2_merge_entities.py):** Merge duplicates using the LightRAG API

---

## Prerequisites

**Before starting this story, verify:**

✅ **Story 2.6 Complete**: CVs ingested into LightRAG
- CVs have been successfully imported into the knowledge graph
- Entities exist in `lightrag_full_entities` table
- Relationships exist in `lightrag_full_relations` table

✅ **LightRAG API Available**: Version with `/graph/entities/merge` endpoint
- LightRAG service running on configured port (default: 9621)
- Verify: `curl http://localhost:9621/docs` shows `/graph/entities/merge` endpoint

✅ **PostgreSQL Access**: Database connection configured
- PostgreSQL service running (default: port 5434)
- `POSTGRES_DSN` configured in `.env`
- Verify: Can query `lightrag_full_entities` table

---

## Acceptance Criteria

### AC 1: Folder Structure and Package Setup

**Created:**
- `app/db_clean/` directory with `__init__.py`
- `data/db_clean/` directory with `.gitkeep`
- Both directories follow existing project conventions

**Validation:**
```bash
# Verify folder structure
ls -la app/db_clean/
ls -la data/db_clean/
```

---

### AC 2: Script 1 - cv1_merge_identify.py (Duplicate Identification)

**Implemented:**
- Query PostgreSQL `lightrag_full_entities` table for all CV entities
- Detect case-insensitive duplicates (e.g., CV_001, Cv_001, cv_001)
- Detect "Candidate CV_XXX" pattern duplicates
- Select canonical entity based on relationship count
- Output JSON file: `data/db_clean/cv_merge_identify_{datetime}.json`

**CLI Arguments:**
- `--cv-pattern` (default: "CV_%")
- `--min-cv-id` (default: 1)
- `--max-cv-id` (default: 999)
- `--output-dir` (default: "data/db_clean")
- `--dry-run` (show results without writing file)
- `--verbose` (enable debug logging)

**JSON Output Format:**
```json
[
  {
    "entity_to_change_into": "CV_001",
    "entities_to_change": ["Cv_001", "cv_001"],
    "relationship_counts": {
      "CV_001": 15,
      "Cv_001": 3,
      "cv_001": 1
    }
  }
]
```

**Validation:**
```bash
# Dry run to see what would be identified
python -m app.db_clean.cv1_merge_identify --dry-run --verbose

# Actual run
python -m app.db_clean.cv1_merge_identify --verbose

# Verify output
cat data/db_clean/cv_merge_identify_*.json | jq .
```

---

### AC 3: Script 2 - cv2_merge_entities.py (Merge Execution)

**Implemented:**
- Load merge operations from JSON file (created by Script 1)
- Call LightRAG API `/graph/entities/merge` endpoint for each operation
- Implement retry logic with exponential backoff
- Track success/failure for each merge
- Generate summary report with statistics

**CLI Arguments:**
- `--file` (required: path to merge operations JSON)
- `--api-url` (default: from settings)
- `--dry-run` (show what would be merged without executing)
- `--batch-size` (default: 10)
- `--retry-attempts` (default: 3)
- `--verbose` (enable debug logging)

**Output:**
- Console logs with merge progress
- JSON report: `data/db_clean/cv_merge_report_{datetime}.json`

**Validation:**
```bash
# Dry run to see what would be merged
python -m app.db_clean.cv2_merge_entities \
  --file data/db_clean/cv_merge_identify_TIMESTAMP.json \
  --dry-run \
  --verbose

# Actual run with small batch size for safety
python -m app.db_clean.cv2_merge_entities \
  --file data/db_clean/cv_merge_identify_TIMESTAMP.json \
  --batch-size 5 \
  --verbose

# Verify report
cat data/db_clean/cv_merge_report_*.json | jq .
```

---

### AC 4: Testing and Validation

**Unit Tests Implemented:**
- Test case-insensitive duplicate detection algorithm
- Test "Candidate CV_XXX" pattern detection
- Test canonical entity selection (relationship count priority)

**Integration Tests Performed:**
- Script 1 dry-run mode works correctly
- Script 2 dry-run mode works correctly
- Actual merge operations execute successfully
- No data loss occurs during merge

**Database Validation:**
```sql
-- Check for remaining duplicates
SELECT
    LOWER(entity_name) as normalized_name,
    COUNT(*) as variant_count,
    STRING_AGG(entity_name, ', ') as variants
FROM lightrag_full_entities
WHERE entity_name ILIKE 'CV_%'
GROUP BY LOWER(entity_name)
HAVING COUNT(*) > 1;

-- Should return 0 rows after successful merge
```

---

### AC 5: Documentation and Code Quality

**Documentation:**
- Inline code comments explain algorithms and logic
- Function docstrings for all public functions
- CLI help text is clear and comprehensive
- Execution workflow documented in implementation plan

**Code Quality:**
- Follows existing codebase patterns (async/await, structured logging)
- Uses `app.shared.config.settings` for configuration
- Implements proper error handling
- Includes retry logic for API failures
- Uses `--dry-run` mode for safety

---

## Implementation Checklist

**Setup:**
- [ ] Create `app/db_clean/` directory with `__init__.py`
- [ ] Create `data/db_clean/` directory with `.gitkeep`

**Script 1 - cv1_merge_identify.py:**
- [ ] Implement database query to fetch CV entities
- [ ] Implement case-insensitive duplicate detection
- [ ] Implement "Candidate CV_XXX" pattern detection
- [ ] Implement canonical entity selection logic
- [ ] Add CLI argument parsing
- [ ] Add dry-run mode support
- [ ] Add JSON output generation
- [ ] Add structured logging

**Script 2 - cv2_merge_entities.py:**
- [ ] Implement JSON file loading
- [ ] Implement LightRAG API client
- [ ] Implement retry logic with exponential backoff
- [ ] Implement batch processing
- [ ] Add CLI argument parsing
- [ ] Add dry-run mode support
- [ ] Add merge report generation
- [ ] Add structured logging

**Testing:**
- [ ] Write unit tests for duplicate detection
- [ ] Test Script 1 in dry-run mode
- [ ] Test Script 1 with actual execution
- [ ] Test Script 2 in dry-run mode
- [ ] Test Script 2 with actual execution
- [ ] Validate results with SQL queries

**Documentation:**
- [ ] Add code comments and docstrings
- [ ] Update implementation plan with execution results
- [ ] Document any issues encountered

---

## Folder Structure

Create the following directories:

```
lightrag-cv/
├── app/
│   └── db_clean/              # NEW: Database cleanup scripts
│       ├── __init__.py        # Empty file for Python package
│       ├── cv1_merge_identify.py
│       └── cv2_merge_entities.py
├── data/
│   └── db_clean/              # NEW: Output data for cleanup operations
│       └── .gitkeep           # Keep directory in git
└── docs/
    └── STORY_2.8_IMPLEMENTATION_PLAN.md  # This file
```

---

## Script 1: cv1_merge_identify.py

### Purpose
Identify duplicate entities with case variations and determine the canonical entity name based on relationship count.

### Key Features
- Query PostgreSQL `lightrag_full_entities` table for all CV entities
- Group entities by case-insensitive name
- Count relationships for each entity variant
- Select the entity with the most relationships as the canonical form
- Output structured JSON file for batch merge processing

### Script Signature

```python
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
```

### Implementation Details

#### 1. Database Query Strategy

Query the `lightrag_full_entities` table to find all CV-related entities:

```python
import asyncpg
from app.shared.config import settings

async def fetch_cv_entities(
    min_cv_id: int = 1,
    max_cv_id: int = 999,
    pattern: str = "CV_%"
) -> list[dict]:
    """
    Fetch all CV entities from the knowledge graph.

    Returns list of entities with their relationship counts.
    """
    conn = await asyncpg.connect(settings.postgres_dsn)

    try:
        # Query to find all CV entities and count their relationships
        query = """
        SELECT
            e.entity_name,
            COUNT(r.id) as relationship_count
        FROM lightrag_full_entities e
        LEFT JOIN lightrag_full_relations r
            ON (r.src_id = e.entity_name OR r.tgt_id = e.entity_name)
        WHERE
            e.entity_name ILIKE $1
        GROUP BY e.entity_name
        ORDER BY e.entity_name
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
```

#### 2. Duplicate Detection Algorithm

Group entities by case-insensitive name and identify duplicates:

```python
from collections import defaultdict
import re

def identify_duplicates(entities: list[dict]) -> list[dict]:
    """
    Group entities by case-insensitive name and identify duplicates.

    Returns list of merge operations to perform.
    """
    # Group by lowercase entity name
    groups = defaultdict(list)

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
```

#### 3. Additional Detection: "Candidate CV_XXX" Pattern

Some entities may have the "Candidate" prefix. Handle this variation:

```python
def detect_candidate_prefix_duplicates(entities: list[dict]) -> list[dict]:
    """
    Detect entities with "Candidate CV_XXX" pattern that duplicate "CV_XXX".

    Returns additional merge operations for candidate prefix variants.
    """
    # Create lookup by CV ID
    cv_entities = {}
    candidate_entities = {}

    cv_pattern = re.compile(r'^(CV_\d+)$', re.IGNORECASE)
    candidate_pattern = re.compile(r'^Candidate\s+(CV_\d+)$', re.IGNORECASE)

    for entity in entities:
        name = entity["entity_name"]

        # Check for CV_XXX pattern
        cv_match = cv_pattern.match(name)
        if cv_match:
            cv_id = cv_match.group(1).upper()
            if cv_id not in cv_entities or entity["relationship_count"] > cv_entities[cv_id]["relationship_count"]:
                cv_entities[cv_id] = entity

        # Check for Candidate CV_XXX pattern
        candidate_match = candidate_pattern.match(name)
        if candidate_match:
            cv_id = candidate_match.group(1).upper()
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
```

#### 4. Output Generation

```python
import json
from datetime import datetime
from pathlib import Path

def save_merge_operations(
    merge_operations: list[dict],
    output_dir: str = "data/db_clean"
) -> Path:
    """
    Save merge operations to JSON file with timestamp.

    Returns path to the created file.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"cv_merge_identify_{timestamp}.json"
    filepath = output_path / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(merge_operations, f, indent=2, ensure_ascii=False)

    return filepath
```

#### 5. Main Function with CLI

```python
import argparse
import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
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

    # Identify case-insensitive duplicates
    logger.info("Identifying case-insensitive duplicates...")
    case_duplicates = identify_duplicates(entities)
    logger.info(f"Found {len(case_duplicates)} case variation groups")

    # Identify "Candidate CV_XXX" duplicates
    logger.info("Identifying 'Candidate CV_XXX' duplicates...")
    candidate_duplicates = detect_candidate_prefix_duplicates(entities)
    logger.info(f"Found {len(candidate_duplicates)} candidate prefix duplicates")

    # Combine all merge operations
    all_merge_operations = case_duplicates + candidate_duplicates

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
```

---

## Script 2: cv2_merge_entities.py

### Purpose
Execute the entity merge operations by calling the LightRAG `/graph/entities/merge` API endpoint.

### Key Features
- Load merge operations from JSON file created by `cv1_merge_identify.py`
- Call LightRAG API `/graph/entities/merge` for each operation
- Track success/failure for each merge
- Generate summary report
- Support dry-run mode for safety
- Implement retry logic for API failures

### Script Signature

```python
"""
CV Entity Merge Executor

Executes entity merge operations on the LightRAG knowledge graph using
the /graph/entities/merge API endpoint.

Usage:
    python -m app.db_clean.cv2_merge_entities --file data/db_clean/cv_merge_identify_20250114_103045.json

Arguments:
    --file PATH          Path to merge operations JSON file (required)
    --api-url URL        LightRAG API base URL (default: from settings)
    --dry-run            Show what would be merged without executing
    --batch-size INT     Number of operations per batch (default: 10)
    --retry-attempts INT Max retry attempts for failed operations (default: 3)
    --verbose            Enable verbose logging

Output:
    Console logs with merge results
    JSON report: data/db_clean/cv_merge_report_{datetime}.json
"""
```

### Implementation Details

#### 1. Load Merge Operations

```python
import json
from pathlib import Path

def load_merge_operations(file_path: str) -> list[dict]:
    """
    Load merge operations from JSON file.

    Returns list of merge operation dictionaries.
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
```

#### 2. LightRAG API Client

```python
import aiohttp
from typing import Optional
from app.shared.config import settings

class LightRAGClient:
    """Client for LightRAG API operations."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.lightrag_api_url or "http://localhost:9621"

    async def merge_entities(
        self,
        entities_to_change: list[str],
        entity_to_change_into: str
    ) -> dict:
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
```

#### 3. Retry Logic

```python
import asyncio
from typing import Callable, TypeVar

T = TypeVar('T')

async def retry_with_backoff(
    func: Callable[..., T],
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    *args,
    **kwargs
) -> T:
    """
    Retry a function with exponential backoff.

    Args:
        func: Async function to retry
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each attempt

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

    raise last_exception
```

#### 4. Batch Processing

```python
async def execute_merge_operations(
    operations: list[dict],
    client: LightRAGClient,
    batch_size: int = 10,
    retry_attempts: int = 3,
    dry_run: bool = False
) -> dict:
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
    results = {
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

            result = {
                "entity_to_change_into": entity_to_change_into,
                "entities_to_change": entities_to_change,
                "status": None,
                "message": None,
                "relationships_transferred": None
            }

            if dry_run:
                logger.info(
                    f"DRY RUN: Would merge {entities_to_change} -> {entity_to_change_into}"
                )
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
                    f"✓ Merged {len(entities_to_change)} entities into '{entity_to_change_into}' "
                    f"({result['relationships_transferred']} relationships)"
                )

            except Exception as e:
                result["status"] = "failed"
                result["message"] = str(e)
                results["failed"] += 1

                logger.error(
                    f"✗ Failed to merge {entities_to_change} -> {entity_to_change_into}: {e}"
                )

            results["details"].append(result)

            # Small delay between operations to avoid overwhelming the API
            await asyncio.sleep(0.5)

    return results
```

#### 5. Report Generation

```python
def save_merge_report(results: dict, output_dir: str = "data/db_clean") -> Path:
    """
    Save merge execution report to JSON file.

    Returns path to the created file.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"cv_merge_report_{timestamp}.json"
    filepath = output_path / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    return filepath
```

#### 6. Main Function with CLI

```python
async def main():
    parser = argparse.ArgumentParser(
        description="Execute CV entity merge operations on LightRAG knowledge graph"
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

    logger.info("Starting CV entity merge execution")
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

    if results['failed'] > 0:
        logger.warning("\nFailed operations:")
        for detail in results['details']:
            if detail['status'] == 'failed':
                logger.warning(
                    f"  - {detail['entities_to_change']} -> {detail['entity_to_change_into']}: "
                    f"{detail['message']}"
                )

    # Save report
    if not args.dry_run:
        report_file = save_merge_report(results)
        logger.info(f"\nDetailed report saved to: {report_file}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Configuration Requirements

### Environment Variables

Add to `.env` file (if not already present):

```bash
# LightRAG API Configuration
LIGHTRAG_API_URL=http://localhost:9621

# PostgreSQL Connection
POSTGRES_DSN=postgresql://lightrag_user:lightrag_dev_2024@localhost:5434/lightrag_db
```

### Update `app/shared/config.py`

Ensure the settings object includes:

```python
class Settings(BaseSettings):
    # ... existing settings ...

    lightrag_api_url: str = "http://localhost:9621"
    postgres_dsn: str = "postgresql://lightrag_user:lightrag_dev_2024@localhost:5434/lightrag_db"
```

---

## Testing Strategy

### 1. Unit Tests

Create `app/db_clean/test_cv_merge.py`:

```python
import pytest
from app.db_clean.cv1_merge_identify import (
    identify_duplicates,
    detect_candidate_prefix_duplicates
)

def test_identify_case_duplicates():
    """Test case-insensitive duplicate detection."""
    entities = [
        {"entity_name": "CV_001", "relationship_count": 10},
        {"entity_name": "Cv_001", "relationship_count": 5},
        {"entity_name": "cv_001", "relationship_count": 2},
        {"entity_name": "CV_002", "relationship_count": 8},
    ]

    result = identify_duplicates(entities)

    assert len(result) == 1
    assert result[0]["entity_to_change_into"] == "CV_001"
    assert set(result[0]["entities_to_change"]) == {"Cv_001", "cv_001"}

def test_detect_candidate_prefix():
    """Test detection of 'Candidate CV_XXX' duplicates."""
    entities = [
        {"entity_name": "CV_001", "relationship_count": 10},
        {"entity_name": "Candidate CV_001", "relationship_count": 3},
        {"entity_name": "CV_002", "relationship_count": 8},
    ]

    result = detect_candidate_prefix_duplicates(entities)

    assert len(result) == 1
    assert result[0]["entity_to_change_into"] == "CV_001"
    assert result[0]["entities_to_change"] == ["Candidate CV_001"]
```

### 2. Integration Tests

```bash
# Test cv1_merge_identify.py in dry-run mode
python -m app.db_clean.cv1_merge_identify --dry-run --verbose

# Test with limited range
python -m app.db_clean.cv1_merge_identify --min-cv-id 1 --max-cv-id 10 --verbose

# Test cv2_merge_entities.py in dry-run mode
python -m app.db_clean.cv2_merge_entities \
  --file data/db_clean/cv_merge_identify_20250114_103045.json \
  --dry-run \
  --verbose
```

### 3. Validation Queries

After executing merges, validate the results:

```sql
-- Check for remaining duplicates
SELECT
    LOWER(entity_name) as normalized_name,
    COUNT(*) as variant_count,
    STRING_AGG(entity_name, ', ') as variants
FROM lightrag_full_entities
WHERE entity_name ILIKE 'CV_%'
GROUP BY LOWER(entity_name)
HAVING COUNT(*) > 1;

-- Verify entity relationship counts
SELECT
    e.entity_name,
    COUNT(r.id) as relationship_count
FROM lightrag_full_entities e
LEFT JOIN lightrag_full_relations r
    ON (r.src_id = e.entity_name OR r.tgt_id = e.entity_name)
WHERE e.entity_name ILIKE 'CV_%'
GROUP BY e.entity_name
ORDER BY relationship_count DESC
LIMIT 20;
```

---

## Execution Workflow

### Step-by-Step Execution

1. **Create folders:**
   ```bash
   mkdir -p app/db_clean
   mkdir -p data/db_clean
   touch app/db_clean/__init__.py
   ```

2. **Run identification (dry-run first):**
   ```bash
   python -m app.db_clean.cv1_merge_identify --dry-run --verbose
   ```

3. **Run identification (actual):**
   ```bash
   python -m app.db_clean.cv1_merge_identify --verbose
   ```

4. **Review the output file:**
   ```bash
   cat data/db_clean/cv_merge_identify_*.json | jq .
   ```

5. **Run merge (dry-run first):**
   ```bash
   python -m app.db_clean.cv2_merge_entities \
     --file data/db_clean/cv_merge_identify_TIMESTAMP.json \
     --dry-run \
     --verbose
   ```

6. **Run merge (actual):**
   ```bash
   python -m app.db_clean.cv2_merge_entities \
     --file data/db_clean/cv_merge_identify_TIMESTAMP.json \
     --batch-size 5 \
     --verbose
   ```

7. **Review the merge report:**
   ```bash
   cat data/db_clean/cv_merge_report_*.json | jq .
   ```

8. **Validate results using SQL queries**

---

## Error Handling

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| `asyncpg.exceptions.InvalidCatalogNameError` | PostgreSQL connection failed | Check `POSTGRES_DSN` in `.env` |
| `aiohttp.ClientError: 400` | Entity doesn't exist | Verify entity names before merge |
| `aiohttp.ClientError: 500` | LightRAG API error | Check LightRAG service logs |
| `FileNotFoundError` | JSON file not found | Verify file path in `--file` argument |
| API timeout | Large merge operation | Reduce `--batch-size` |

### Logging

All scripts use Python's `logging` module with structured context:

```python
logger.info("Processing batch", extra={
    "batch_number": batch_idx,
    "batch_size": len(batch),
    "total_operations": len(operations)
})
```

---

## Performance Considerations

### Database Queries
- The `fetch_cv_entities` query joins entities and relations tables
- Expected query time: ~1-2 seconds for 1000 entities
- Add index if slow: `CREATE INDEX idx_entities_name_ilike ON lightrag_full_entities(LOWER(entity_name))`

### API Rate Limiting
- Default batch size: 10 concurrent operations
- Default delay between operations: 0.5 seconds
- Adjust `--batch-size` if LightRAG API shows errors

### Memory Usage
- Script loads all merge operations into memory
- Expected memory: ~1MB per 1000 operations
- For large datasets (>10K operations), consider chunking the JSON file

---

## Success Criteria

- [ ] Scripts execute without errors
- [ ] All duplicate entities are identified correctly
- [ ] Merge operations preserve all relationships
- [ ] No data loss in the knowledge graph
- [ ] Execution reports are clear and actionable
- [ ] Dry-run mode works correctly
- [ ] Validation queries show no remaining duplicates

---

## Next Steps After Story 2.8

1. **Monitor knowledge graph quality:**
   - Schedule periodic duplicate checks
   - Set up alerts for new case variations

2. **Extend to other entity types:**
   - Apply same pattern to company names, skills, etc.
   - Create generic entity deduplication framework

3. **Preventive measures:**
   - Add entity normalization during ingestion
   - Update `cv4_import.py` to normalize entity names before sending to LightRAG

4. **Documentation:**
   - Add execution results to project documentation
   - Create runbook for periodic cleanup operations

---

## References

- LightRAG API Documentation: `/graph/entities/merge` endpoint
- Existing patterns: `app/cv_ingest/cv4_import.py`
- Database schema: `lightrag_full_entities`, `lightrag_full_relations`
- Configuration: `app/shared/config.py`

---

## Questions for Product Owner

Before implementation, clarify:

1. Should we preserve the entity with the most relationships, or prefer uppercase `CV_XXX` format?
2. Are there other entity naming patterns to consider (e.g., "Resume CV_XXX")?
3. Should we back up the database before running merge operations?
4. What is the acceptable downtime window for running these scripts?
5. Should we notify users/systems before/after merge operations?

---

**Document Version:** 1.0
**Created:** 2025-01-14
**Author:** Development Team
**Status:** Ready for Implementation
