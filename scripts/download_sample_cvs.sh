#!/bin/bash
# Download sample CV PDFs for testing

set -e

OUTPUT_DIR="data/cvs"
mkdir -p "$OUTPUT_DIR"

echo "=================================================="
echo "Downloading sample CV PDFs for testing"
echo "=================================================="
echo

# For now, let's note that we need sample CVs
# The HuggingFace datasets require git-lfs or special handling

echo "Note: HuggingFace datasets require git-lfs for direct download."
echo "Installing git-lfs..."

# Install git-lfs
if ! command -v git-lfs &> /dev/null; then
    echo "Installing git-lfs..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y git-lfs
    else
        echo "Please install git-lfs manually: https://git-lfs.github.com/"
        exit 1
    fi
fi

git lfs install

echo
echo "Cloning d4rk3r/resumes-raw-pdf dataset (first 5 files)..."
cd "$OUTPUT_DIR"

# Clone with depth=1 and just get a few files
GIT_LFS_SKIP_SMUDGE=1 git clone --depth=1 https://huggingface.co/datasets/d4rk3r/resumes-raw-pdf temp_dataset

cd temp_dataset/data || cd temp_dataset

# Pull just a few PDF files
echo "Pulling first 5 PDF files..."
find . -name "*.pdf" | head -5 | while read -r file; do
    echo "  Downloading: $file"
    git lfs pull --include="$file"
    cp "$file" "../$(basename "$file")"
done

cd ../..
rm -rf temp_dataset

echo
echo "=================================================="
echo "Summary:"
ls -lh "$OUTPUT_DIR"/*.pdf 2>/dev/null | wc -l | xargs echo "Downloaded CV files:"
ls -lh "$OUTPUT_DIR"/*.pdf 2>/dev/null || echo "No PDF files found"
echo "=================================================="
