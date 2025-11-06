# Story 2.5.4: Cleanup & Documentation Update

> 📋 **Epic**: [Epic 2.5: Script Refactoring & Application Structure](../epics/epic-2.5-revised.md)
> 📋 **Architecture**: [Source Tree](../architecture/source-tree.md), [Tech Stack](../architecture/tech-stack.md), [Coding Standards](../architecture/coding-standards.md)

## User Story

**As a** developer,
**I want** obsolete scripts removed and documentation updated,
**so that** the codebase is clean and new developers can navigate it easily.

## Story Status

- **Status**: Not Started
- **Assigned To**: TBD
- **Estimated Effort**: 2-3 hours
- **Dependencies**: Story 2.5.3 ✅
- **Blocks**: None

## Acceptance Criteria

1. ✅ **Obsolete Scripts Removed**:
   - Identify and remove/archive 3-5 obsolete or duplicate scripts
   - Create `.archive/` folder for scripts that might be useful later
   - Document removal decisions

2. ✅ **Artifacts Consolidated**:
   - `query-entities.sql` moved to `/app/artifacts/` or removed if obsolete
   - `scripts/requirements.txt` moved to `/app/requirements.txt` if applicable
   - Any other loose files organized

3. ✅ **Architecture Documentation Updated**:
   - [source-tree.md](../architecture/source-tree.md) reflects new `/app` structure
   - [coding-standards.md](../architecture/coding-standards.md) import patterns updated
   - [tech-stack.md](../architecture/tech-stack.md) documents multi-provider LLM support

4. ✅ **Story Documentation Updated**:
   - Review Stories 2.3, 2.4, Epic 2 for script execution commands
   - Update any `python scripts/x.py` → `python -m app.module.x`
   - Verify no broken links

5. ✅ **Application README Created**:
   - `/app/README.md` created with:
     - Directory structure explanation
     - LLM provider configuration guide
     - Script execution examples
     - Development setup instructions

6. ✅ **Root README Updated**:
   - New script locations documented
   - LLM provider setup instructions added
   - Quick start guide reflects new structure

## Tasks

- [ ] **Task 1: Identify Obsolete Scripts**
  - Compare download scripts: `download-cvs.py`, `download_cv_samples.py`, `explore_and_download_cvs.py`
  - Identify most recent/functional version
  - Mark duplicates/obsolete versions for removal
  - Review test scripts: `test-cigref-parsing.py`, `test-header-extraction.py`
  - Determine if still useful or superseded

- [ ] **Task 2: Archive or Remove Obsolete Scripts**
  - Create `.archive/` directory if needed
  - Move obsolete scripts to `.archive/` with date stamp
  - Document removal decisions in `/app/CLEANUP.md`
  - Git commit: `git commit -m "Archive obsolete scripts from Epic 2.5.4"`

- [ ] **Task 3: Consolidate Artifacts**
  - Review `query-entities.sql`:
    - If used: Move to `/app/artifacts/query-entities.sql`
    - If obsolete: Remove with documentation
  - Review `scripts/requirements.txt`:
    - If app-specific: Move to `/app/requirements.txt`
    - If script-specific: Keep in `/scripts/requirements.txt`
    - Update both if needed

- [ ] **Task 4: Update source-tree.md**
  - Document new `/app` directory structure
  - Show infrastructure vs. workflow separation
  - Add LLM abstraction layer (`app/shared/llm_client.py`)
  - Verify tree matches actual filesystem

- [ ] **Task 5: Update coding-standards.md**
  - Update import pattern examples:
    - `from app.shared.config import settings`
    - `from app.shared.llm_client import get_llm_client`
  - Add module execution pattern:
    - `python -m app.cigref_ingest.ingest_cigref`
  - Document PYTHONPATH requirements

- [ ] **Task 6: Update tech-stack.md**
  - Add multi-provider LLM support section
  - Document Ollama provider (existing)
  - Document OpenAI-compatible provider (LiteLLM)
  - Add configuration variables table
  - Note backward compatibility with `OLLAMA_*` vars

- [ ] **Task 7: Review and Update Story Documentation**
  - Search for `python scripts/` in all story files
  - Update to `python -m app.module.script`
  - Update Story 2.3 (CV Dataset), Story 2.4 (CV Parsing) references
  - Verify Epic 2 documentation links still work

- [ ] **Task 8: Create /app/README.md**
  - Write comprehensive application structure guide:
    - Directory organization explanation
    - Module purposes (`cigref_ingest`, `cv_ingest`, `shared`)
    - LLM provider configuration (Ollama, LiteLLM)
    - Script execution examples
    - Development setup (PYTHONPATH, virtual environment)
    - Troubleshooting common import errors

- [ ] **Task 9: Update Root README.md**
  - Add "Application Structure" section
  - Document script locations (`/scripts` vs `/app`)
  - Add LLM provider setup instructions
  - Update quick start commands
  - Link to `/app/README.md` for detailed info

- [ ] **Task 10: Validation**
  - Verify all internal documentation links work
  - Check external references to script paths
  - Ensure no dead links or outdated commands
  - Review with fresh eyes (imagine onboarding new developer)

## Dev Notes

### Obsolete Script Candidates

Review for removal/archival:

1. **Download Scripts** (likely duplicates):
   - `download-cvs.py` (original)
   - `download_cv_samples.py` (variation)
   - `explore_and_download_cvs.py` (variation)
   - **Action**: Keep most recent, archive others

2. **Test Scripts** (development artifacts):
   - `test-cigref-parsing.py` (early dev test)
   - `test-header-extraction.py` (early dev test)
   - **Action**: Archive if superseded by actual tests

3. **Preparation Scripts** (may be one-time use):
   - `prepare-cigref-for-lightrag.py` (data prep)
   - **Action**: Keep if still useful, otherwise archive

### Directory Structure for source-tree.md

```markdown
### Application Structure (Epic 2.5)

```
lightrag-cv/
├── scripts/                          # Infrastructure scripts only (6 files)
│   ├── setup.sh                     # Environment setup
│   ├── health-check.sh              # Service health checks (shell)
│   ├── health-check.py              # Service health checks (Python)
│   ├── start-docling-gpu.sh         # Start Docling with GPU
│   ├── restart-docling-gpu.sh       # Restart Docling GPU service
│   └── validate-ollama.py           # Validate Ollama connectivity
│
├── app/                              # Application workflows (Epic 2.5)
│   ├── __init__.py
│   ├── README.md                    # Application documentation
│   ├── requirements.txt             # Application dependencies
│   │
│   ├── shared/                       # Shared services and utilities
│   │   ├── __init__.py
│   │   ├── config.py                # Centralized configuration (multi-provider)
│   │   └── llm_client.py            # LLM provider abstraction (Ollama, OpenAI-compatible)
│   │
│   ├── cigref_ingest/                # CIGREF nomenclature workflows (7 files)
│   │   ├── __init__.py
│   │   ├── ingest-cigref.py         # Single-batch CIGREF ingestion
│   │   ├── ingest-cigref-batched.py # Batch CIGREF ingestion (primary)
│   │   ├── prepare-cigref-for-lightrag.py
│   │   ├── analyze-cigref-parsing.py
│   │   ├── test-cigref-parsing.py
│   │   ├── enrich-cigref-hierarchy.py
│   │   └── test-header-extraction.py
│   │
│   ├── cv_ingest/                    # CV processing workflows (9 files)
│   │   ├── __init__.py
│   │   ├── parse-cvs.py             # CV parsing via Docling
│   │   ├── classify-cvs-with-llm.py # CV classification using LLM
│   │   ├── download-cvs.py          # CV dataset download (primary)
│   │   ├── download_cv_samples.py
│   │   ├── create-parsed-manifest.py
│   │   ├── select-validation-sample.py
│   │   └── validate-classification.py
│   │
│   └── artifacts/                    # SQL queries and development artifacts
│       └── query-entities.sql       # Entity query examples
│
├── .archive/                         # Archived obsolete scripts (Epic 2.5.4)
│   └── [obsolete scripts with timestamps]
```
```

### /app/README.md Structure

```markdown
# LightRAG-CV Application Workflows

This directory contains the application-layer workflows for the LightRAG-CV project, organized by domain.

## Directory Structure

- **`shared/`** - Shared configuration, utilities, and LLM provider abstraction
- **`cigref_ingest/`** - CIGREF IT profile nomenclature ingestion workflows
- **`cv_ingest/`** - CV parsing, classification, and quality validation workflows
- **`artifacts/`** - SQL queries, data analysis scripts, and development artifacts

## LLM Provider Configuration

### Supported Providers

1. **Ollama** (default) - Local LLM inference
2. **OpenAI-compatible** - Any OpenAI API-compatible service (e.g., LiteLLM)

### Configuration

Set in `.env` file:

```bash
# Ollama (default)
LLM_BINDING=ollama
LLM_BINDING_HOST=http://host.docker.internal:11434
LLM_MODEL=qwen2.5:7b-instruct-q4_K_M
# No API key needed for Ollama

# OpenAI-compatible (e.g., LiteLLM, OpenAI)
LLM_BINDING=litellm
LLM_BINDING_HOST=http://localhost:8000
LLM_MODEL=gpt-3.5-turbo
LLM_BINDING_API_KEY=your-api-key-here

# Same pattern for embeddings
EMBEDDING_BINDING=ollama
EMBEDDING_BINDING_HOST=http://host.docker.internal:11434
EMBEDDING_MODEL=bge-m3:latest
# EMBEDDING_BINDING_API_KEY=your-key  # Only if using openai for embeddings
```

### Backward Compatibility

Legacy `OLLAMA_*` variables still work:

```bash
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_LLM_MODEL=qwen2.5:7b-instruct-q4_K_M
```

## Running Scripts

### Setup PYTHONPATH

```bash
export PYTHONPATH=/home/ubuntu/dev/lightrag-cv
```

### Run as Python Module

```bash
# CIGREF ingestion
python -m app.cigref_ingest.ingest_cigref_batched

# CV parsing
python -m app.cv_ingest.parse_cvs

# CV classification
python -m app.cv_ingest.classify_cvs_with_llm
```

### Run with Arguments

```bash
python -m app.cigref_ingest.ingest_cigref_batched --batch-size 85
python -m app.cv_ingest.parse_cvs --input-dir data/cvs/test-set
```

## Development

### Import Patterns

```python
# Shared configuration
from app.shared.config import settings

# LLM client abstraction
from app.shared.llm_client import get_llm_client

# Cross-module imports
from app.cigref_ingest.prepare_cigref_for_lightrag import prepare_data
```

### Troubleshooting

**ImportError: No module named 'app'**
- Solution: Set PYTHONPATH to project root

**ImportError: No module named 'app.shared.config'**
- Solution: Verify all `__init__.py` files exist

**LLM connection errors**
- Solution: Check `LLM_BINDING_HOST` in `.env`
- Verify Ollama is running: `curl http://localhost:11434/api/version`

## Testing

Run critical workflows after changes:

```bash
# Test CIGREF workflow (1 batch)
python -m app.cigref_ingest.ingest_cigref_batched --batch-size 1

# Test CV parsing (1 file)
python -m app.cv_ingest.parse_cvs

# Test LLM classification (1 file)
python -m app.cv_ingest.classify_cvs_with_llm
```
```

### Success Criteria

- ✅ 3-5 obsolete scripts removed/archived
- ✅ All architecture docs updated
- ✅ `/app/README.md` created with comprehensive guide
- ✅ Root `README.md` updated with new structure
- ✅ No broken documentation links
- ✅ Epic 2.5 complete!

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-11-06 | 1.0 | Story created from Epic 2.5 validation with pragmatic fixes | Sarah (PO) |
