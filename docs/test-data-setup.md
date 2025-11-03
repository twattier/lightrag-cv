# Test Data Setup Guide

## Current Status

### ✅ Completed

1. **Cigref Nomenclature PDF** - Successfully downloaded
   - File: `data/cigref/Cigref_Nomenclature_des_profils_metiers_SI_EN_2024.pdf`
   - Size: 4.8 MB
   - Source: https://www.cigref.fr/wp/wp-content/uploads/2024/12/Cigref_Nomenclature_des_profils_metiers_SI_EN_2024.pdf
   - **Ready for use in Story 2.2**

### ⚠️ Pending: CV Samples

CV datasets from HuggingFace require git-lfs for download. Two approaches:

## Approach 1: Install git-lfs and Download (Recommended)

```bash
# Install git-lfs
sudo apt-get update
sudo apt-get install -y git-lfs
git lfs install

# Download 5-10 sample CVs from d4rk3r/resumes-raw-pdf
cd data/cvs
git clone --depth=1 https://huggingface.co/datasets/d4rk3r/resumes-raw-pdf temp
cd temp/data
git lfs pull --include="*.pdf"
find . -name "*.pdf" | head -10 | xargs -I {} cp {} ../../
cd ../..
rm -rf temp

# Verify
ls -lh data/cvs/*.pdf
```

## Approach 2: Use huggingface-cli

```bash
# Install HuggingFace CLI
pip install huggingface-hub[cli]

# Download specific files from dataset
huggingface-cli download d4rk3r/resumes-raw-pdf \
  --repo-type dataset \
  --local-dir data/cvs/temp \
  --include "data/*.pdf"

# Copy to main directory
cp data/cvs/temp/data/*.pdf data/cvs/
rm -rf data/cvs/temp
```

## Approach 3: Manual Download

1. Visit https://huggingface.co/datasets/d4rk3r/resumes-raw-pdf/tree/main/data
2. Download 5-10 PDF files manually
3. Save to `data/cvs/` directory

## Alternative: Use Existing Sample

If you have any sample CV PDFs available locally, you can copy them to `data/cvs/` for testing:

```bash
cp /path/to/your/sample/cv.pdf data/cvs/
```

## Data Sources Reference

### 1. gigswar/cv_files
- **URL**: https://huggingface.co/datasets/gigswar/cv_files
- **Splits**: validation, test
- **Format**: PDF files
- **Use case**: General CV parsing tests

### 2. d4rk3r/resumes-raw-pdf
- **URL**: https://huggingface.co/datasets/d4rk3r/resumes-raw-pdf
- **Split**: train
- **Format**: Raw PDF resumes
- **Use case**: Raw resume parsing and extraction

### 3. Cigref IT Profiles Nomenclature
- **URL**: https://www.cigref.fr/wp/wp-content/uploads/2024/12/Cigref_Nomenclature_des_profils_metiers_SI_EN_2024.pdf
- **Status**: ✅ Downloaded
- **Location**: `data/cigref/Cigref_Nomenclature_des_profils_metiers_SI_EN_2024.pdf`
- **Use case**: IT profile taxonomy for Story 2.2

## Next Steps for Story 2.2

With the Cigref PDF now downloaded, you can proceed with Story 2.2:

1. ✅ Cigref PDF is in `data/cigref/` directory
2. Test parsing with Docling API:
   ```bash
   curl -X POST http://localhost:8001/parse \
     -F "file=@data/cigref/Cigref_Nomenclature_des_profils_metiers_SI_EN_2024.pdf" \
     > data/cigref/cigref-parsed.json
   ```
3. Validate parsing quality (AC 3-4 in Story 2.2)
4. Document results in `docs/cigref-parsing-validation.md`

## Helper Scripts

Created helper scripts in `scripts/` directory:
- `download_cv_samples.py` - Python script to download HuggingFace datasets
- `explore_and_download_cvs.py` - Explores dataset structure before downloading
- `download_sample_cvs.sh` - Shell script using git-lfs

Note: These scripts require git-lfs to be installed for HuggingFace dataset access.

