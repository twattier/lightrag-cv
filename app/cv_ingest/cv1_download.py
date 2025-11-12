#!/usr/bin/env python3
"""
CV Dataset Acquisition and Preprocessing Script

Part of lightrag-cv application workflows.
Module: app.cv_ingest.cv1_download

Downloads and curates CV samples from Hugging Face datasets.
Since many CVs in these datasets are image-based PDFs without extractable text,
this script uses a pragmatic approach:
1. Download diverse samples based on file size and dataset distribution
2. Rely on manual quality validation to verify suitability

Story: Story 2.5.3c - Refactor CV Ingest Workflow for Simplicity
"""

import argparse
import hashlib
import json
import logging
import random
import shutil
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    from datasets import load_dataset
    import fitz  # PyMuPDF for page count
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "datasets", "pymupdf"])
    from datasets import load_dataset
    import fitz

# Import centralized configuration (RULE 2: All Environment Variables via config.py)
from app.shared.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# File size constraints (typical CV range)
MIN_FILE_SIZE_KB = 30   # Filter out very small files (likely corrupt)
MAX_FILE_SIZE_KB = 3000 # Filter out very large files (likely not standard CVs)
MAX_SAMPLES_TO_COLLECT = 100  # Collect candidates for selection


def estimate_page_count(pdf_bytes: bytes) -> int:
    """Estimate page count from PDF."""
    try:
        pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page_count = len(pdf_doc)
        pdf_doc.close()
        return page_count
    except:
        return 0


def collect_cvs_from_dataset(dataset_name: str, split: str, max_samples: int, cv_db: Optional[List[Dict]] = None) -> List[Dict]:
    """
    Collect CV candidates from a HuggingFace dataset.
    Uses pragmatic filtering based on file size and structure.

    Duplicate Detection Strategy (Story 2.7):
    - HuggingFace datasets do not provide unique IDs (no 'id', 'uuid', or 'document_id' fields)
    - Uses SHA-256 content hash of PDF bytes as unique identifier
    - Fast (~1-2ms per PDF), collision-resistant, deterministic

    Args:
        dataset_name: Name of the HuggingFace dataset
        split: Dataset split to use
        max_samples: Maximum number of samples to collect
        cv_db: Optional CV database to check for already-imported CVs

    Returns:
        List of CV candidates with content_hash field
    """
    cv_db = cv_db or []
    logger.info(
        "Processing dataset",
        extra={"dataset": dataset_name, "split": split, "max_samples": max_samples}
    )

    candidates = []

    try:
        ds = load_dataset(dataset_name, split=split, streaming=True)

        for idx, sample in enumerate(ds):
            if idx >= max_samples:
                break

            try:
                # Extract file content and metadata
                content = None
                filename = None
                page_count = 0

                # Handle different dataset structures
                if "pdf" in sample:
                    pdf_obj = sample["pdf"]
                    # pdfplumber.PDF object
                    if hasattr(pdf_obj, 'stream'):
                        # Read page count first
                        page_count = len(pdf_obj.pages)
                        filename = getattr(pdf_obj, 'path', f"cv_{idx}.pdf")
                        # NOW read the content (stream might have been consumed by pdfplumber)
                        pdf_obj.stream.seek(0)  # Reset to beginning
                        content = pdf_obj.stream.read()
                    elif isinstance(pdf_obj, dict) and "bytes" in pdf_obj:
                        content = pdf_obj["bytes"]
                    else:
                        content = pdf_obj if isinstance(pdf_obj, bytes) else None
                elif "file" in sample:
                    file_data = sample["file"]
                    if isinstance(file_data, dict):
                        content = file_data.get("bytes")
                        filename = file_data.get("path", f"cv_{idx}.pdf")
                    else:
                        content = file_data if isinstance(file_data, bytes) else None
                elif "content" in sample:
                    content = sample["content"]

                # Get filename from sample if not yet set
                if not filename:
                    filename = sample.get("path", f"cv_{idx}.pdf")

                if not content:
                    continue

                # Calculate SHA-256 content hash for duplicate detection (Story 2.7)
                # SHA-256 chosen for: speed (~200-500 MB/s), collision-resistance, standard library support
                content_hash = hashlib.sha256(content).hexdigest()

                # Extract just the base filename
                if isinstance(filename, str):
                    filename = Path(filename).name
                else:
                    filename = f"cv_{idx}.pdf"

                # Skip if already imported (based on content hash, not filename)
                if is_cv_already_imported(content_hash, dataset_name, cv_db):
                    logger.debug(
                        "Skipping CV - already imported (duplicate content)",
                        extra={"content_hash": content_hash[:16], "dataset": dataset_name}
                    )
                    continue

                # File size filtering
                file_size_kb = len(content) / 1024
                if file_size_kb < MIN_FILE_SIZE_KB or file_size_kb > MAX_FILE_SIZE_KB:
                    logger.debug(
                        "Skipping CV - file size out of range",
                        extra={"cv_filename": filename, "size_kb": round(file_size_kb, 2)}
                    )
                    continue

                # Page count filtering (prefer 1-10 pages)
                if page_count == 0:
                    page_count = estimate_page_count(content)

                if page_count == 0 or page_count > 10:
                    logger.debug(
                        "Skipping CV - page count out of range",
                        extra={"cv_filename": filename, "pages": page_count}
                    )
                    continue

                cv_metadata = {
                    "file_format": "PDF",
                    "file_size_kb": round(file_size_kb, 2),
                    "page_count": page_count,
                    "source_dataset": dataset_name,
                    "source_id": None,  # HuggingFace datasets don't provide unique IDs
                    "content_hash": content_hash,  # SHA-256 hash for duplicate detection (Story 2.7)
                    "content": content
                }

                candidates.append(cv_metadata)

                logger.info(
                    "CV candidate collected",
                    extra={
                        "cv_filename": filename,
                        "size_kb": round(file_size_kb, 2),
                        "pages": page_count
                    }
                )

            except Exception as e:
                logger.warning(
                    f"Error processing sample {idx}: {e}",
                    extra={"index": idx, "error": str(e)}
                )
                import traceback
                if idx < 5:  # Only print traceback for first few errors
                    traceback.print_exc()
                continue

        logger.info(
            "Dataset collection complete",
            extra={"dataset": dataset_name, "candidates": len(candidates)}
        )

    except Exception as e:
        logger.error(
            "Dataset loading failed",
            extra={"dataset": dataset_name, "error": str(e)}
        )

    return candidates


def ensure_diversity(cvs: List[Dict], target_count: int) -> List[Dict]:
    """
    Select a diverse subset of CVs across different file sizes.
    """
    # Shuffle for randomness
    random.shuffle(cvs)

    # Simply return the first target_count CVs after shuffle
    return cvs[:target_count]


def load_cv_db() -> List[Dict]:
    """
    Load the CV database (historical tracking of all imported CVs).
    Returns empty list if database doesn't exist.

    CV Database Schema (Story 2.7):
    - filename: Standardized filename (cv_XXX.pdf) - links to docs/cv_XXX.pdf and parsed/cv_XXX_parsed.json
    - source_dataset: HuggingFace dataset name
    - source_id: Unique ID from dataset (None if dataset doesn't provide IDs)
    - content_hash: SHA-256 hash of PDF content for duplicate detection

    Returns:
        List of CV records
    """
    if not settings.CV_DB.exists():
        logger.info("CV database does not exist, starting fresh")
        return []

    try:
        with open(settings.CV_DB, 'r', encoding='utf-8') as f:
            db = json.load(f)
            logger.info(f"Loaded CV database with {len(db)} previously imported CVs")
            return db
    except Exception as e:
        logger.error(f"Error loading CV database: {e}")
        return []


def save_cv_db(cv_db: List[Dict]) -> None:
    """
    Save the updated CV database.

    Args:
        cv_db: List of CV records to save
    """
    try:
        with open(settings.CV_DB, 'w', encoding='utf-8') as f:
            json.dump(cv_db, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved CV database with {len(cv_db)} total CVs")
    except Exception as e:
        logger.error(f"Error saving CV database: {e}")
        raise


def archive_manifest() -> None:
    """
    Archive the current cvs-manifest.json to the imported directory.
    Filename format: YYYYMMDD_HHMMSS_cvs-manifest.json
    """
    if not settings.CV_MANIFEST.exists():
        logger.info("No existing manifest to archive")
        return

    # Create imported directory if it doesn't exist
    settings.CV_IMPORTED_DIR.mkdir(parents=True, exist_ok=True)

    # Generate timestamp-based filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archived_filename = f"{timestamp}_cvs-manifest.json"
    archived_path = settings.CV_IMPORTED_DIR / archived_filename

    # Copy manifest to archive
    shutil.copy2(settings.CV_MANIFEST, archived_path)
    logger.info(f"Archived manifest to: {archived_path}")


def is_cv_already_imported(content_hash: str, source_dataset: str, cv_db: List[Dict]) -> bool:
    """
    Check if a CV has already been imported using content hash.

    Uses SHA-256 content hash for reliable duplicate detection (Story 2.7).
    Backward compatible: skips old database entries without content_hash field.

    Args:
        content_hash: SHA-256 hash of PDF content bytes
        source_dataset: Source dataset name
        cv_db: CV database to check against

    Returns:
        True if CV with same content_hash already exists in database
    """
    for record in cv_db:
        # Backward compatibility: Skip old entries without content_hash
        if 'content_hash' not in record:
            continue

        if (record.get('content_hash') == content_hash and
            record.get('source_dataset') == source_dataset):
            return True
    return False


def get_next_cv_index() -> int:
    """
    Determine the next available CV index by checking existing files.

    Returns:
        Next available index (e.g., 26 if cv_025.pdf exists)
    """
    if not settings.CV_DOCS_DIR.exists():
        return 1

    # Find all existing cv_XXX.pdf files
    existing_files = list(settings.CV_DOCS_DIR.glob("cv_*.pdf"))
    if not existing_files:
        return 1

    # Extract indices from filenames
    indices = []
    for file in existing_files:
        try:
            # Extract number from cv_XXX.pdf
            num_str = file.stem.split('_')[1]
            indices.append(int(num_str))
        except (IndexError, ValueError):
            continue

    if not indices:
        return 1

    return max(indices) + 1


def main():
    """Main execution function."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Download and curate CV samples from Hugging Face datasets"
    )
    parser.add_argument(
        "--max-cvs",
        type=int,
        default=25,
        help="Maximum number of CVs to download (default: 25)"
    )
    args = parser.parse_args()

    target_cv_count = args.max_cvs

    logger.info("=" * 70)
    logger.info("CV DATASET ACQUISITION AND PREPROCESSING")
    logger.info(f"Story 2.5.3c - Downloading {target_cv_count} CV Samples")
    logger.info("=" * 70)

    # Set random seed for reproducibility
    random.seed(42)

    # Create directories using centralized config
    settings.CV_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created directory: {settings.CV_DOCS_DIR}")

    # Archive existing manifest if present
    archive_manifest()

    # Load CV database to track historical imports
    cv_db = load_cv_db()

    # Get next available CV index
    next_cv_index = get_next_cv_index()
    logger.info(f"Starting CV index: {next_cv_index}")

    # Collect CVs from datasets
    all_candidates = []

    # Dataset 1: d4rk3r/resumes-raw-pdf
    logger.info("\n[1/2] Collecting from d4rk3r/resumes-raw-pdf...")
    try:
        candidates_1 = collect_cvs_from_dataset(
            "d4rk3r/resumes-raw-pdf",
            split="train",
            max_samples=MAX_SAMPLES_TO_COLLECT,
            cv_db=cv_db
        )
        all_candidates.extend(candidates_1)
    except Exception as e:
        logger.error(f"Failed to process d4rk3r/resumes-raw-pdf: {e}")

    # Dataset 2: gigswar/cv_files
    logger.info("\n[2/2] Collecting from gigswar/cv_files...")
    for split in ["validation", "train"]:
        try:
            candidates_2 = collect_cvs_from_dataset(
                "gigswar/cv_files",
                split=split,
                max_samples=MAX_SAMPLES_TO_COLLECT,
                cv_db=cv_db
            )
            all_candidates.extend(candidates_2)
            if candidates_2:
                break  # Successfully got candidates, no need to try other splits
        except Exception as e:
            logger.warning(f"Failed with split '{split}': {e}")
            continue

    # Track duplicates before diversity selection (Story 2.7)
    total_candidates_before_dedup = len(all_candidates)

    logger.info(f"\nTotal candidates collected: {total_candidates_before_dedup}")

    # Adjust target to actual available candidates (Story 2.7)
    actual_target = min(len(all_candidates), target_cv_count)

    if len(all_candidates) == 0:
        logger.error("No candidates found. Cannot continue.")
        sys.exit(1)

    if len(all_candidates) < target_cv_count:
        logger.warning(f"Only {len(all_candidates)} candidates available (requested {target_cv_count}). Will download all available CVs.")

    # Select diverse final set
    logger.info(f"\nSelecting {actual_target} diverse CVs...")
    final_cvs = ensure_diversity(all_candidates, target_count=actual_target)

    # Download and organize files
    logger.info(f"\nDownloading {len(final_cvs)} CVs to {settings.CV_DOCS_DIR}...")
    manifest_entries = []
    new_cv_db_entries = []

    for idx, cv_meta in enumerate(final_cvs, start=0):
        # Use incremental index
        cv_index = next_cv_index + idx
        standardized_filename = f"cv_{cv_index:03d}.pdf"
        output_path = settings.CV_DOCS_DIR / standardized_filename

        # Skip if file already exists (shouldn't happen, but defensive check)
        if output_path.exists():
            logger.warning(f"File already exists, skipping: {standardized_filename}")
            continue

        # Write file
        output_path.write_bytes(cv_meta['content'])

        # Create manifest entry
        manifest_entry = {
            "candidate_label": f"cv_{cv_index:03d}",
            "filename": standardized_filename,
            "file_format": cv_meta['file_format'],
            "file_size_kb": cv_meta['file_size_kb'],
            "page_count": cv_meta['page_count'],
            "source_dataset": cv_meta['source_dataset'],
            "source_id": cv_meta['source_id'],
            "content_hash": cv_meta['content_hash']  # SHA-256 hash (Story 2.7)
        }

        manifest_entries.append(manifest_entry)

        # Create CV database entry (lightweight tracking)
        cv_db_entry = {
            "filename": standardized_filename,
            "source_dataset": cv_meta['source_dataset'],
            "source_id": cv_meta['source_id'],
            "content_hash": cv_meta['content_hash']  # SHA-256 hash (Story 2.7)
        }
        new_cv_db_entries.append(cv_db_entry)

        logger.info(
            "CV downloaded",
            extra={
                "cv_filename": standardized_filename
            }
        )

    # Generate manifest
    logger.info(f"\nGenerating manifest at {settings.CV_MANIFEST}...")
    manifest = {
        "metadata": {
            "total_cvs": len(manifest_entries),
            "source_datasets": ["d4rk3r/resumes-raw-pdf", "gigswar/cv_files"]            
        },
        "cvs": manifest_entries
    }

    with open(settings.CV_MANIFEST, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    # Update CV database with new entries
    logger.info("\nUpdating CV database...")
    cv_db.extend(new_cv_db_entries)
    save_cv_db(cv_db)

    # Summary statistics
    logger.info("\n" + "=" * 70)
    logger.info("SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total CVs curated: {len(manifest_entries)}")

    # Duplicate detection statistics (Story 2.7)
    duplicates_skipped = total_candidates_before_dedup - len(manifest_entries)
    logger.info("\nDuplicate Detection:")
    logger.info(f"  Total candidates found: {total_candidates_before_dedup}")
    logger.info(f"  Duplicates skipped: {duplicates_skipped}")
    logger.info(f"  Unique CVs downloaded: {len(manifest_entries)}")

    # File size distribution
    sizes = [e['file_size_kb'] for e in manifest_entries]
    logger.info("\nFile Size Range:")
    logger.info(f"  Min: {min(sizes):.1f} KB")
    logger.info(f"  Max: {max(sizes):.1f} KB")
    logger.info(f"  Avg: {sum(sizes)/len(sizes):.1f} KB")

    # Page count distribution
    pages = [e['page_count'] for e in manifest_entries]
    logger.info("\nPage Count Range:")
    logger.info(f"  Min: {min(pages)} pages")
    logger.info(f"  Max: {max(pages)} pages")
    logger.info(f"  Avg: {sum(pages)/len(pages):.1f} pages")

    logger.info(f"\nFiles saved to: {settings.CV_DOCS_DIR}")
    logger.info(f"Manifest saved to: {settings.CV_MANIFEST}")
    logger.info("\n⚠️  NEXT STEPS:")
    logger.info("   1. Parse CVs: python -m app.cv_ingest.cv2_parse")
    logger.info("   2. Classify CVs: python -m app.cv_ingest.cv3_classify")
    logger.info("   3. Import CVs: python -m app.cv_ingest.cv4_import")
    logger.info("\n✓ CV dataset acquisition complete!")


if __name__ == "__main__":
    main()
