#!/usr/bin/env python3
"""
CV Parsing Script for Story 2.4

Processes all CVs through Docling /parse endpoint and saves parsed outputs.
Implements structured logging, async batch processing, and error handling.

Usage:
    python scripts/parse-cvs.py
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import httpx

from config import settings

# Configure structured logging (RULE 7)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('parse-cvs.log')
    ]
)
logger = logging.getLogger(__name__)


class CVParsingStats:
    """Track parsing statistics."""

    def __init__(self):
        self.total_cvs = 0
        self.successful_parses = 0
        self.failed_parses = 0
        self.total_chunks = 0
        self.processing_times = []
        self.failures: List[Dict] = []

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_cvs == 0:
            return 0.0
        return (self.successful_parses / self.total_cvs) * 100

    @property
    def avg_processing_time(self) -> float:
        """Calculate average processing time in seconds."""
        if not self.processing_times:
            return 0.0
        return sum(self.processing_times) / len(self.processing_times)

    @property
    def avg_chunks_per_cv(self) -> float:
        """Calculate average chunks per CV."""
        if self.successful_parses == 0:
            return 0.0
        return self.total_chunks / self.successful_parses


class CVParser:
    """Handles CV parsing through Docling service."""

    def __init__(self, docling_url: str = "http://localhost:8001"):
        self.docling_url = docling_url
        self.stats = CVParsingStats()

    async def check_docling_health(self) -> bool:
        """Check if Docling service is healthy."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.docling_url}/health")
                if response.status_code == 200:
                    health_data = response.json()
                    logger.info(
                        "Docling service healthy",
                        extra={
                            "status": health_data.get("status"),
                            "gpu_available": health_data.get("gpu_available")
                        }
                    )
                    return True
                else:
                    logger.error(
                        "Docling service unhealthy",
                        extra={"status_code": response.status_code}
                    )
                    return False
        except Exception as e:
            logger.error(
                "Failed to connect to Docling service",
                extra={"error": str(e)}
            )
            return False

    async def parse_cv(
        self,
        cv_path: Path,
        cv_metadata: Dict,
        client: httpx.AsyncClient
    ) -> Optional[Dict]:
        """
        Parse a single CV through Docling.

        Args:
            cv_path: Path to CV file
            cv_metadata: Metadata from cvs-manifest.json
            client: Async HTTP client

        Returns:
            Parsed CV data dict or None if failed
        """
        candidate_label = cv_metadata["candidate_label"]
        start_time = time.time()

        try:
            # Read CV file (RULE 8: Don't log sensitive content)
            with open(cv_path, 'rb') as f:
                cv_content = f.read()

            file_size_kb = len(cv_content) / 1024

            logger.info(
                "Starting CV parse",
                extra={
                    "candidate_label": candidate_label,
                    "cv_filename": cv_metadata["filename"],
                    "file_size_kb": round(file_size_kb, 2)
                }
            )

            # Submit to Docling (RULE 9: Async I/O)
            response = await client.post(
                f"{self.docling_url}/parse",
                files={"file": (cv_metadata["filename"], cv_content, "application/pdf")},
                timeout=300.0  # 5 minutes per CV (increased for larger files)
            )

            processing_time = time.time() - start_time

            if response.status_code == 200:
                parsed_data = response.json()
                chunks_count = len(parsed_data.get("chunks", []))

                # Enrich with metadata from manifest (no classification data)
                enriched_data = {
                    "document_id": candidate_label,
                    "document_type": "CV",
                    "source_filename": cv_metadata["filename"],
                    "candidate_label": candidate_label,
                    "chunks": parsed_data.get("chunks", []),
                    "metadata": {
                        "file_format": cv_metadata.get("file_format"),
                        "file_size_kb": cv_metadata.get("file_size_kb"),
                        "page_count": cv_metadata.get("page_count"),
                        "source_dataset": cv_metadata.get("source_dataset"),
                        "chunks_count": chunks_count,
                        "parsing_timestamp": datetime.utcnow().isoformat() + "Z",
                        "processing_time_ms": round(processing_time * 1000, 2)
                    }
                }

                # Merge Docling metadata if present
                if "metadata" in parsed_data:
                    enriched_data["metadata"].update(parsed_data["metadata"])

                logger.info(
                    "CV parsed successfully",
                    extra={
                        "candidate_label": candidate_label,
                        "chunks_count": chunks_count,
                        "processing_time_ms": round(processing_time * 1000, 2)
                    }
                )

                self.stats.processing_times.append(processing_time)
                self.stats.total_chunks += chunks_count

                return enriched_data
            else:
                logger.error(
                    "Docling parse failed",
                    extra={
                        "candidate_label": candidate_label,
                        "status_code": response.status_code,
                        "error": response.text[:200]
                    }
                )
                self.stats.failures.append({
                    "candidate_label": candidate_label,
                    "cv_filename": cv_metadata["filename"],
                    "error": f"HTTP {response.status_code}: {response.text[:200]}"
                })
                return None

        except httpx.TimeoutException:
            processing_time = time.time() - start_time
            logger.error(
                "CV parse timeout",
                extra={
                    "candidate_label": candidate_label,
                    "processing_time_ms": round(processing_time * 1000, 2)
                }
            )
            self.stats.failures.append({
                "candidate_label": candidate_label,
                "cv_filename": cv_metadata["filename"],
                "error": "Timeout after 300 seconds"
            })
            return None
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(
                "CV parse exception",
                extra={
                    "candidate_label": candidate_label,
                    "error": str(e),
                    "processing_time_ms": round(processing_time * 1000, 2)
                }
            )
            self.stats.failures.append({
                "candidate_label": candidate_label,
                "cv_filename": cv_metadata["filename"],
                "error": str(e)
            })
            return None

    async def parse_all_cvs(
        self,
        cvs_manifest_path: Path,
        test_set_dir: Path,
        output_dir: Path,
        max_concurrent: int = 5
    ) -> CVParsingStats:
        """
        Parse all CVs from manifest with concurrent processing.

        Args:
            cvs_manifest_path: Path to cvs-manifest.json
            test_set_dir: Directory containing CV files
            output_dir: Directory to save parsed outputs
            max_concurrent: Maximum concurrent requests

        Returns:
            CVParsingStats with results
        """
        # Load manifest
        logger.info(
            "Loading CV manifest",
            extra={"manifest_path": str(cvs_manifest_path)}
        )

        with open(cvs_manifest_path, 'r') as f:
            manifest = json.load(f)

        cvs_list = manifest.get("cvs", [])
        self.stats.total_cvs = len(cvs_list)

        logger.info(
            "Starting batch CV parsing",
            extra={
                "total_cvs": self.stats.total_cvs,
                "max_concurrent": max_concurrent
            }
        )

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(
            "Output directory ready",
            extra={"output_dir": str(output_dir)}
        )

        # Process CVs with concurrency limit
        async with httpx.AsyncClient() as client:
            semaphore = asyncio.Semaphore(max_concurrent)

            async def parse_with_limit(cv_metadata: Dict) -> Tuple[str, Optional[Dict]]:
                async with semaphore:
                    cv_path = test_set_dir / cv_metadata["filename"]
                    parsed_data = await self.parse_cv(cv_path, cv_metadata, client)
                    return cv_metadata["candidate_label"], parsed_data

            # Parse all CVs concurrently
            tasks = [parse_with_limit(cv_meta) for cv_meta in cvs_list]
            results = await asyncio.gather(*tasks)

            # Save successful parses
            for candidate_label, parsed_data in results:
                if parsed_data:
                    output_path = output_dir / f"{candidate_label}_parsed.json"
                    with open(output_path, 'w') as f:
                        json.dump(parsed_data, f, indent=2)

                    self.stats.successful_parses += 1
                    logger.info(
                        "Parsed CV saved",
                        extra={
                            "candidate_label": candidate_label,
                            "output_file": str(output_path)
                        }
                    )
                else:
                    self.stats.failed_parses += 1

        return self.stats


def print_summary(stats: CVParsingStats):
    """Print parsing summary statistics."""
    print("\n" + "="*60)
    print("CV PARSING SUMMARY")
    print("="*60)
    print(f"Total CVs:              {stats.total_cvs}")
    print(f"Successful parses:      {stats.successful_parses}")
    print(f"Failed parses:          {stats.failed_parses}")
    print(f"Success rate:           {stats.success_rate:.1f}%")
    print(f"Total chunks extracted: {stats.total_chunks}")
    print(f"Avg chunks per CV:      {stats.avg_chunks_per_cv:.1f}")
    print(f"Avg processing time:    {stats.avg_processing_time:.2f}s")
    print("="*60)

    if stats.failures:
        print("\nFAILED CVS:")
        for failure in stats.failures:
            print(f"  - {failure['candidate_label']}: {failure['error']}")
        print("="*60)

    # Assessment against NFR2 (90% threshold)
    if stats.success_rate >= 90.0:
        print("\n✅ SUCCESS: Meets NFR2 quality threshold (90%+)")
    else:
        print("\n⚠️  WARNING: Below NFR2 quality threshold (90%)")
        print("    Mitigation may be required (see Story 2.4 Task 7)")
    print()


async def main():
    """Main execution function."""
    # Configuration paths
    data_dir = Path("/home/wsluser/dev/lightrag-cv/data")
    cvs_dir = data_dir / "cvs"
    manifest_path = cvs_dir / "cvs-manifest.json"
    test_set_dir = cvs_dir / "test-set"
    output_dir = cvs_dir / "parsed"

    # Validate paths
    if not manifest_path.exists():
        logger.error(
            "CV manifest not found",
            extra={"path": str(manifest_path)}
        )
        sys.exit(1)

    if not test_set_dir.exists():
        logger.error(
            "Test set directory not found",
            extra={"path": str(test_set_dir)}
        )
        sys.exit(1)

    # Initialize parser
    parser = CVParser(docling_url="http://localhost:8001")

    # Check Docling health
    logger.info("Checking Docling service health...")
    if not await parser.check_docling_health():
        logger.error("Docling service not available. Exiting.")
        sys.exit(1)

    # Parse all CVs
    try:
        stats = await parser.parse_all_cvs(
            cvs_manifest_path=manifest_path,
            test_set_dir=test_set_dir,
            output_dir=output_dir,
            max_concurrent=5
        )

        # Print summary
        print_summary(stats)

        # Log final stats
        logger.info(
            "CV parsing completed",
            extra={
                "total_cvs": stats.total_cvs,
                "successful": stats.successful_parses,
                "failed": stats.failed_parses,
                "success_rate": round(stats.success_rate, 2)
            }
        )

        # Exit code based on success
        sys.exit(0 if stats.success_rate >= 90.0 else 1)

    except Exception as e:
        logger.error(
            "Fatal error during CV parsing",
            extra={"error": str(e)}
        )
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
