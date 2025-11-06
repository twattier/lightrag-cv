#!/usr/bin/env python3
"""
Download sample CVs from HuggingFace datasets for testing.

Part of lightrag-cv application workflows.
Module: app.cv_ingest.download_cv_samples

Downloads a few samples from:
- gigswar/cv_files
- d4rk3r/resumes-raw-pdf
"""

import os
from pathlib import Path

try:
    from datasets import load_dataset
    from huggingface_hub import hf_hub_download
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call(["pip", "install", "-q", "datasets", "huggingface-hub"])
    from datasets import load_dataset
    from huggingface_hub import hf_hub_download


def download_cv_samples():
    """Download sample CVs from HuggingFace datasets."""
    output_dir = Path("data/cvs")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Downloading CV samples from HuggingFace datasets...")
    print("-" * 60)

    # Dataset 1: gigswar/cv_files
    try:
        print("\n1. Loading gigswar/cv_files dataset...")
        ds1 = load_dataset("gigswar/cv_files", split="train", streaming=True)

        print("   Downloading first 5 samples...")
        for i, sample in enumerate(ds1.take(5)):
            # Datasets library provides file content
            if "file" in sample and "path" in sample:
                filename = f"cv_gigswar_{i+1}_{Path(sample['path']).name}"
                output_path = output_dir / filename

                with open(output_path, "wb") as f:
                    f.write(sample["file"]["bytes"])

                print(f"   ✓ Downloaded: {filename}")

        print(f"   ✓ Downloaded 5 samples from gigswar/cv_files")

    except Exception as e:
        print(f"   ✗ Error downloading gigswar/cv_files: {e}")
        print(f"   Trying alternative method...")
        # Alternative: try to access via git-lfs or direct file access

    # Dataset 2: d4rk3r/resumes-raw-pdf
    try:
        print("\n2. Loading d4rk3r/resumes-raw-pdf dataset...")
        ds2 = load_dataset("d4rk3r/resumes-raw-pdf", split="train", streaming=True)

        print("   Downloading first 5 samples...")
        for i, sample in enumerate(ds2.take(5)):
            if "pdf" in sample or "file" in sample:
                # Handle different dataset structures
                file_content = sample.get("pdf", sample.get("file"))
                if isinstance(file_content, dict) and "bytes" in file_content:
                    filename = f"cv_d4rk3r_{i+1}.pdf"
                    output_path = output_dir / filename

                    with open(output_path, "wb") as f:
                        f.write(file_content["bytes"])

                    print(f"   ✓ Downloaded: {filename}")

        print(f"   ✓ Downloaded 5 samples from d4rk3r/resumes-raw-pdf")

    except Exception as e:
        print(f"   ✗ Error downloading d4rk3r/resumes-raw-pdf: {e}")

    print("\n" + "-" * 60)
    print("Download complete! Checking results...")

    # List downloaded files
    cv_files = list(output_dir.glob("cv_*"))
    if cv_files:
        print(f"\nDownloaded {len(cv_files)} CV files to data/cvs/:")
        for cv_file in sorted(cv_files):
            size_mb = cv_file.stat().st_size / (1024 * 1024)
            print(f"  - {cv_file.name} ({size_mb:.2f} MB)")
    else:
        print("\n⚠️  No CV files downloaded. Datasets may require authentication or have different structure.")
        print("    Try manually downloading from:")
        print("    - https://huggingface.co/datasets/gigswar/cv_files")
        print("    - https://huggingface.co/datasets/d4rk3r/resumes-raw-pdf")


if __name__ == "__main__":
    download_cv_samples()
