#!/usr/bin/env python3
"""
CV Dataset Acquisition and Preprocessing Script

Downloads and curates 20-30 CV samples from Hugging Face datasets.
Since many CVs in these datasets are image-based PDFs without extractable text,
this script uses a pragmatic approach:
1. Download diverse samples based on file size and dataset distribution
2. Rely on manual quality validation (Story AC 5) to verify suitability

Story: Story 2.3 - CV Dataset Acquisition and Preprocessing
"""

import json
import logging
import random
import sys
from collections import defaultdict
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CVS_DIR = DATA_DIR / "cvs"
TEST_SET_DIR = CVS_DIR / "test-set"
MANIFEST_PATH = CVS_DIR / "cvs-manifest.json"

TARGET_CV_COUNT = 25  # Target 20-30 CVs
MAX_SAMPLES_TO_COLLECT = 100  # Collect candidates for selection

# File size constraints (typical CV range)
MIN_FILE_SIZE_KB = 30   # Filter out very small files (likely corrupt)
MAX_FILE_SIZE_KB = 3000 # Filter out very large files (likely not standard CVs)


def estimate_page_count(pdf_bytes: bytes) -> int:
    """Estimate page count from PDF."""
    try:
        pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page_count = len(pdf_doc)
        pdf_doc.close()
        return page_count
    except:
        return 0


def infer_domain_from_filename(filename: str) -> str:
    """
    Infer likely IT domain from filename keywords.
    Returns a general domain or "General IT" if unclear.
    """
    filename_lower = filename.lower()

    domain_keywords = {
        'Software Development': ['developer', 'programmer', 'software', 'frontend', 'backend', 'fullstack'],
        'Infrastructure': ['devops', 'sre', 'cloud', 'infrastructure', 'sysadmin'],
        'Data': ['data', 'analytics', 'ml', 'ai', 'scientist', 'analyst'],
        'Security': ['security', 'cybersecurity', 'infosec', 'pentester'],
        'Management': ['manager', 'lead', 'cto', 'director', 'head']
    }

    for domain, keywords in domain_keywords.items():
        if any(kw in filename_lower for kw in keywords):
            return domain

    return "General IT"


def infer_experience_level(filename: str, file_size_kb: float) -> str:
    """
    Infer experience level from filename and file size heuristics.
    Larger files often indicate more experience (more content).
    """
    filename_lower = filename.lower()

    if any(kw in filename_lower for kw in ['junior', 'entry', 'graduate']):
        return 'junior'
    elif any(kw in filename_lower for kw in ['senior', 'lead', 'principal', 'staff']):
        return 'senior'
    elif 'mid' in filename_lower:
        return 'mid'

    # Use file size as proxy
    if file_size_kb < 100:
        return 'junior'
    elif file_size_kb > 250:
        return 'senior'
    else:
        return 'mid'


def collect_cvs_from_dataset(dataset_name: str, split: str, max_samples: int) -> List[Dict]:
    """
    Collect CV candidates from a HuggingFace dataset.
    Uses pragmatic filtering based on file size and structure.
    """
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

                # Extract just the base filename
                if isinstance(filename, str):
                    filename = Path(filename).name
                else:
                    filename = f"cv_{idx}.pdf"

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

                # Infer metadata from filename and file characteristics
                domain = infer_domain_from_filename(filename)
                experience_level = infer_experience_level(filename, file_size_kb)

                cv_metadata = {
                    "original_filename": filename,
                    "role_domain": domain,
                    "experience_level": experience_level,
                    "file_format": "PDF",
                    "file_size_kb": round(file_size_kb, 2),
                    "page_count": page_count,
                    "source_dataset": dataset_name,
                    "content": content
                }

                candidates.append(cv_metadata)

                logger.info(
                    "CV candidate collected",
                    extra={
                        "cv_filename": filename,
                        "domain": domain,
                        "experience": experience_level,
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
    Select a diverse subset of CVs across domains, experience levels, and file sizes.
    """
    # Shuffle for randomness
    random.shuffle(cvs)

    # Group by domain and experience
    groups = defaultdict(list)
    for cv in cvs:
        key = (cv['role_domain'], cv['experience_level'])
        groups[key].append(cv)

    # Round-robin selection from groups
    selected = []
    available_groups = list(groups.keys())

    while len(selected) < target_count and available_groups:
        for key in available_groups[:]:
            if groups[key]:
                selected.append(groups[key].pop(0))
                if len(selected) >= target_count:
                    break
            else:
                available_groups.remove(key)

    # If still need more, add any remaining
    if len(selected) < target_count:
        remaining = [cv for group_cvs in groups.values() for cv in group_cvs]
        needed = target_count - len(selected)
        selected.extend(remaining[:needed])

    return selected


def main():
    """Main execution function."""
    logger.info("=" * 70)
    logger.info("CV DATASET ACQUISITION AND PREPROCESSING")
    logger.info("Story 2.3 - Curating 20-30 CV Samples")
    logger.info("=" * 70)

    # Set random seed for reproducibility
    random.seed(42)

    # Create directories
    TEST_SET_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created directory: {TEST_SET_DIR}")

    # Collect CVs from datasets
    all_candidates = []

    # Dataset 1: d4rk3r/resumes-raw-pdf
    logger.info("\n[1/2] Collecting from d4rk3r/resumes-raw-pdf...")
    try:
        candidates_1 = collect_cvs_from_dataset(
            "d4rk3r/resumes-raw-pdf",
            split="train",
            max_samples=MAX_SAMPLES_TO_COLLECT
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
                max_samples=50
            )
            all_candidates.extend(candidates_2)
            if candidates_2:
                break  # Successfully got candidates, no need to try other splits
        except Exception as e:
            logger.warning(f"Failed with split '{split}': {e}")
            continue

    logger.info(f"\nTotal candidates collected: {len(all_candidates)}")

    if len(all_candidates) < 20:
        logger.error(f"Insufficient candidates ({len(all_candidates)}). Need at least 20.")
        logger.info("Consider adjusting filtering criteria or max_samples.")
        sys.exit(1)

    # Select diverse final set
    logger.info(f"\nSelecting {TARGET_CV_COUNT} diverse CVs...")
    final_cvs = ensure_diversity(all_candidates, target_count=TARGET_CV_COUNT)

    # Download and organize files
    logger.info(f"\nDownloading {len(final_cvs)} CVs to {TEST_SET_DIR}...")
    manifest_entries = []

    for idx, cv_meta in enumerate(final_cvs, start=1):
        # Standardized filename
        standardized_filename = f"cv_{idx:03d}.pdf"
        output_path = TEST_SET_DIR / standardized_filename

        # Write file
        output_path.write_bytes(cv_meta['content'])

        # Create manifest entry
        manifest_entry = {
            "candidate_label": f"cv_{idx:03d}",
            "filename": standardized_filename,
            "original_filename": cv_meta['original_filename'],
            "role_domain": cv_meta['role_domain'],
            "experience_level": cv_meta['experience_level'],
            "file_format": cv_meta['file_format'],
            "file_size_kb": cv_meta['file_size_kb'],
            "page_count": cv_meta['page_count'],
            "source_dataset": cv_meta['source_dataset'],
            "manual_tags": [],
            "notes": "Requires manual validation - many CVs are image-based PDFs"
        }

        manifest_entries.append(manifest_entry)

        logger.info(
            "CV downloaded",
            extra={
                "cv_filename": standardized_filename,
                "domain": cv_meta['role_domain'],
                "experience": cv_meta['experience_level']
            }
        )

    # Generate manifest
    logger.info(f"\nGenerating manifest at {MANIFEST_PATH}...")
    manifest = {
        "metadata": {
            "total_cvs": len(manifest_entries),
            "source_datasets": ["d4rk3r/resumes-raw-pdf", "gigswar/cv_files"],
            "filtering_criteria": {
                "file_size_range": f"{MIN_FILE_SIZE_KB}-{MAX_FILE_SIZE_KB} KB",
                "page_count_range": "1-10 pages",
                "selection_method": "Diverse sampling across inferred domains and experience levels"
            },
            "notes": [
                "Many CVs in these datasets are image-based PDFs without extractable text",
                "Domain and experience level were inferred from filenames and file characteristics",
                "Manual quality validation (AC 5) is critical to verify suitability for Story 2.4"
            ]
        },
        "cvs": manifest_entries
    }

    with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    # Summary statistics
    logger.info("\n" + "=" * 70)
    logger.info("SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total CVs curated: {len(manifest_entries)}")

    # Domain distribution
    domain_dist = defaultdict(int)
    for entry in manifest_entries:
        domain_dist[entry['role_domain']] += 1

    logger.info("\nDomain Distribution:")
    for domain, count in sorted(domain_dist.items()):
        logger.info(f"  {domain}: {count}")

    # Experience distribution
    exp_dist = defaultdict(int)
    for entry in manifest_entries:
        exp_dist[entry['experience_level']] += 1

    logger.info("\nExperience Level Distribution:")
    for level, count in sorted(exp_dist.items()):
        logger.info(f"  {level}: {count}")

    # File size distribution
    sizes = [e['file_size_kb'] for e in manifest_entries]
    logger.info("\nFile Size Range:")
    logger.info(f"  Min: {min(sizes):.1f} KB")
    logger.info(f"  Max: {max(sizes):.1f} KB")
    logger.info(f"  Avg: {sum(sizes)/len(sizes):.1f} KB")

    logger.info(f"\nFiles saved to: {TEST_SET_DIR}")
    logger.info(f"Manifest saved to: {MANIFEST_PATH}")
    logger.info("\n⚠️  IMPORTANT: Proceed with Task 5 (Manual Quality Validation)")
    logger.info("   Many CVs are image-based. Verify 3-5 samples for suitability.")
    logger.info("\n✓ CV dataset acquisition complete!")


if __name__ == "__main__":
    main()
