#!/usr/bin/env python3
"""
Explore HuggingFace CV datasets and download samples.

Part of lightrag-cv application workflows.
Module: app.cv_ingest.explore_and_download_cvs
"""

import os
from pathlib import Path

try:
    from datasets import load_dataset
    import requests
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call(["pip", "install", "-q", "datasets", "requests"])
    from datasets import load_dataset
    import requests


def explore_and_download():
    """Explore dataset structure and download samples."""
    output_dir = Path("data/cvs")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("EXPLORING AND DOWNLOADING CV SAMPLES FROM HUGGINGFACE")
    print("=" * 70)

    # Dataset 1: gigswar/cv_files
    print("\n1. DATASET: gigswar/cv_files")
    print("-" * 70)
    try:
        # Use 'validation' split since 'train' doesn't exist
        print("Loading 'validation' split...")
        ds1 = load_dataset("gigswar/cv_files", split="validation", streaming=True)

        print("Inspecting first sample structure...")
        first_sample = next(iter(ds1))
        print(f"Sample keys: {first_sample.keys()}")

        # Download first 3 samples
        print("\nDownloading 3 samples from validation split...")
        count = 0
        for i, sample in enumerate(ds1.take(3)):
            try:
                # Try different possible field names
                if "file" in sample:
                    file_data = sample["file"]
                    if isinstance(file_data, dict):
                        if "bytes" in file_data:
                            content = file_data["bytes"]
                        elif "content" in file_data:
                            content = file_data["content"]
                        else:
                            print(f"   Unknown file structure: {file_data.keys()}")
                            continue
                    else:
                        content = file_data

                    # Get filename
                    if "path" in sample:
                        base_name = Path(sample["path"]).name
                    else:
                        base_name = f"cv_{i+1}.pdf"

                    filename = f"gigswar_val_{i+1}_{base_name}"
                    output_path = output_dir / filename

                    with open(output_path, "wb") as f:
                        f.write(content)

                    size_kb = len(content) / 1024
                    print(f"   ✓ Downloaded: {filename} ({size_kb:.1f} KB)")
                    count += 1

            except Exception as e:
                print(f"   ✗ Error processing sample {i+1}: {e}")
                import traceback
                traceback.print_exc()

        print(f"\n✓ Successfully downloaded {count} samples from gigswar/cv_files")

    except Exception as e:
        print(f"✗ Error with gigswar/cv_files: {e}")
        import traceback
        traceback.print_exc()

    # Dataset 2: d4rk3r/resumes-raw-pdf
    print("\n2. DATASET: d4rk3r/resumes-raw-pdf")
    print("-" * 70)
    try:
        print("Loading dataset...")
        ds2 = load_dataset("d4rk3r/resumes-raw-pdf", split="train", streaming=True)

        print("Inspecting first sample structure...")
        first_sample = next(iter(ds2))
        print(f"Sample keys: {first_sample.keys()}")

        # Download first 3 samples
        print("\nDownloading 3 samples...")
        count = 0
        for i, sample in enumerate(ds2.take(3)):
            try:
                # Try different possible field names
                content = None
                filename = f"d4rk3r_{i+1}.pdf"

                if "pdf" in sample:
                    pdf_data = sample["pdf"]
                    if isinstance(pdf_data, dict) and "bytes" in pdf_data:
                        content = pdf_data["bytes"]
                    else:
                        content = pdf_data
                elif "file" in sample:
                    file_data = sample["file"]
                    if isinstance(file_data, dict) and "bytes" in file_data:
                        content = file_data["bytes"]
                    else:
                        content = file_data
                elif "content" in sample:
                    content = sample["content"]

                if content:
                    output_path = output_dir / filename

                    with open(output_path, "wb") as f:
                        f.write(content)

                    size_kb = len(content) / 1024
                    print(f"   ✓ Downloaded: {filename} ({size_kb:.1f} KB)")
                    count += 1
                else:
                    print(f"   ✗ Could not find file content in sample {i+1}")
                    print(f"      Available keys: {sample.keys()}")

            except Exception as e:
                print(f"   ✗ Error processing sample {i+1}: {e}")

        print(f"\n✓ Successfully downloaded {count} samples from d4rk3r/resumes-raw-pdf")

    except Exception as e:
        print(f"✗ Error with d4rk3r/resumes-raw-pdf: {e}")
        import traceback
        traceback.print_exc()

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    cv_files = sorted(list(output_dir.glob("*.pdf"))) + sorted(list(output_dir.glob("*.doc*")))
    if cv_files:
        print(f"\n✓ Successfully downloaded {len(cv_files)} CV files to data/cvs/:")
        for cv_file in cv_files:
            size_kb = cv_file.stat().st_size / 1024
            print(f"  - {cv_file.name} ({size_kb:.1f} KB)")
    else:
        print("\n⚠️  No CV files were downloaded successfully.")
        print("\nAlternative: Download manually from:")
        print("  - https://huggingface.co/datasets/gigswar/cv_files/tree/main/data")
        print("  - https://huggingface.co/datasets/d4rk3r/resumes-raw-pdf/tree/main/data")


if __name__ == "__main__":
    explore_and_download()
