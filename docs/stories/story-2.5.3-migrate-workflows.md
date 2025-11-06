# Story 2.5.3: Migrate CIGREF & CV Workflow Scripts

> 📋 **Epic**: [Epic 2.5: Script Refactoring & Application Structure](../epics/epic-2.5-revised.md)
> 📋 **Architecture**: [Source Tree](../architecture/source-tree.md), [Coding Standards](../architecture/coding-standards.md)

## User Story

**As a** developer,
**I want** all CIGREF and CV workflow scripts moved to `/app` subdirectories,
**so that** the codebase is organized and maintainable.

## Story Status

- **Status**: Not Started
- **Assigned To**: TBD
- **Estimated Effort**: 3-4 hours
- **Dependencies**: Story 2.5.2 ✅
- **Blocks**: Story 2.5.4

## Acceptance Criteria

1. ✅ **CIGREF Scripts Migrated** (7 files):
   - Moved to `/app/cigref_ingest/`:
     - `ingest-cigref.py`
     - `ingest-cigref-batched.py`
     - `prepare-cigref-for-lightrag.py`
     - `analyze-cigref-parsing.py`
     - `test-cigref-parsing.py`
     - `enrich-cigref-hierarchy.py`
     - `test-header-extraction.py`
   - All imports updated: `from config` → `from app.shared.config`

2. ✅ **CV Scripts Migrated** (9 files):
   - Moved to `/app/cv_ingest/`:
     - `parse-cvs.py`
     - `classify-cvs-with-llm.py`
     - `download-cvs.py`
     - `download_cv_samples.py`
     - `explore_and_download_cvs.py`
     - `download_sample_cvs.sh`
     - `create-parsed-manifest.py`
     - `select-validation-sample.py`
     - `validate-classification.py`
   - All imports updated

3. ✅ **LLM Abstraction Integration**:
   - `classify-cvs-with-llm.py` updated to use `llm_client.generate()` instead of direct `httpx.post()`
   - Other LLM-using scripts updated if applicable

4. ✅ **Manual Testing Complete**:
   - **CIGREF workflow**: Run `python -m app.cigref_ingest.ingest_cigref_batched` with 1 test document
   - **CV parsing workflow**: Run `python -m app.cv_ingest.parse_cvs` with 1 test CV
   - **LLM classification workflow**: Run `python -m app.cv_ingest.classify_cvs_with_llm` with 1 test CV
   - All 3 workflows execute successfully without ImportError

5. ✅ **Original Scripts Removed**:
   - Original `/scripts/*.py` workflow files deleted (keeping only infrastructure scripts)
   - Git commit created before deletion for rollback safety

6. ✅ **No Breaking Changes**:
   - Service APIs unchanged
   - `.env` variables unchanged
   - Service health checks pass

## Tasks

- [ ] **Task 1: Git Checkpoint Before Migration**
  - Create safety checkpoint: `git commit -m "Checkpoint before Epic 2.5.3 script migration"`
  - Verify clean working directory

- [ ] **Task 2: Migrate CIGREF Workflow Scripts**
  - Move 7 CIGREF scripts to `/app/cigref_ingest/`
  - Update all imports: `from config import settings` → `from app.shared.config import settings`
  - Search for any other local imports and update paths
  - Add docstring to each file indicating new module structure

- [ ] **Task 3: Migrate CV Workflow Scripts**
  - Move 9 CV scripts to `/app/cv_ingest/`
  - Update all imports
  - Search for cross-references between scripts and update paths
  - Handle shell script (`download_sample_cvs.sh`) - ensure paths are correct

- [ ] **Task 4: Update `classify-cvs-with-llm.py` for LLM Abstraction**
  - Replace direct `httpx.post(f"{OLLAMA_URL}/api/generate")` calls
  - Use `from app.shared.llm_client import get_llm_client`
  - Update to `client.generate()` pattern
  - Test with 1 CV to verify abstraction works

- [ ] **Task 5: Manual Testing - CIGREF Workflow**
  - Set PYTHONPATH: `export PYTHONPATH=/home/ubuntu/dev/lightrag-cv`
  - Run: `python -m app.cigref_ingest.ingest_cigref_batched --batch-size 1`
  - Verify no ImportError
  - Verify LightRAG ingestion starts successfully
  - Document any issues and fix before proceeding

- [ ] **Task 6: Manual Testing - CV Parsing Workflow**
  - Run: `python -m app.cv_ingest.parse_cvs` (with test CV)
  - Verify Docling parsing works
  - Verify no ImportError
  - Document results

- [ ] **Task 7: Manual Testing - LLM Classification Workflow**
  - Run: `python -m app.cv_ingest.classify_cvs_with_llm` (with test CV)
  - Verify LLM abstraction layer works
  - Verify Ollama connection via abstraction
  - Verify classification completes
  - Document results

- [ ] **Task 8: Remove Original Scripts from `/scripts/`**
  - Delete migrated workflow scripts from `/scripts/`
  - Keep infrastructure scripts: `setup.sh`, `health-check.*`, `*-docling-gpu.sh`, `validate-ollama.py`
  - Verify only 6 infrastructure scripts remain
  - Git commit: `git commit -m "Remove migrated workflow scripts from /scripts/"`

- [ ] **Task 9: Update Script Execution Paths**
  - Search for references to old paths in documentation
  - Update any `python scripts/ingest-cigref.py` → `python -m app.cigref_ingest.ingest_cigref`
  - Create list of affected docs for Story 2.5.4

- [ ] **Task 10: Final Service Health Checks**
  - Verify LightRAG: `curl http://localhost:9621/health`
  - Verify Docling: `curl http://localhost:8000/health`
  - Verify PostgreSQL connectivity
  - Confirm no regressions

## Dev Notes

### Migration Pattern

For each script:

1. **Move file**:
   ```bash
   mv scripts/ingest-cigref.py app/cigref_ingest/ingest-cigref.py
   ```

2. **Update imports**:
   ```python
   # OLD
   from config import settings

   # NEW
   from app.shared.config import settings
   ```

3. **Update any cross-script imports**:
   ```python
   # OLD
   from prepare_cigref_for_lightrag import prepare_data

   # NEW
   from app.cigref_ingest.prepare_cigref_for_lightrag import prepare_data
   ```

4. **Add module docstring**:
   ```python
   """
   CIGREF Profile Ingestion Script

   Part of lightrag-cv application workflows.
   Module: app.cigref_ingest.ingest_cigref
   """
   ```

### LLM Abstraction Migration

For `classify-cvs-with-llm.py`:

```python
# OLD (direct httpx calls)
import httpx
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL")

async with httpx.AsyncClient() as client:
    response = await client.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": "qwen2.5:7b", "prompt": prompt}
    )
    result = response.json()

# NEW (using abstraction)
from app.shared.llm_client import get_llm_client

client = get_llm_client()
result = await client.generate(
    prompt=prompt,
    model=None,  # Uses default from config
    format='json'
)
```

### Running Migrated Scripts

Always set PYTHONPATH before running:

```bash
export PYTHONPATH=/home/ubuntu/dev/lightrag-cv

# Run as module (recommended)
python -m app.cigref_ingest.ingest_cigref_batched

# Or with full path
python app/cigref_ingest/ingest-cigref-batched.py
```

### Troubleshooting Import Errors

If ImportError occurs:

1. **Check PYTHONPATH**: Must include project root
2. **Verify `__init__.py` files**: All directories must have them
3. **Check import statements**: Use absolute imports from `app.`
4. **Look for circular imports**: Avoid importing between workflow scripts

### Testing Checklist

After migration, verify:
- ✅ CIGREF ingestion starts without errors
- ✅ CV parsing completes successfully
- ✅ LLM classification uses abstraction layer
- ✅ No service health regressions
- ✅ Original scripts removed from `/scripts/`

### Rollback Procedure

If critical issues found:

```bash
# Rollback to checkpoint
git reset --hard HEAD~1

# Or restore specific commit
git reset --hard <commit-before-migration>

# Remove /app directory if needed
rm -rf app/
```

### Success Criteria

- ✅ All 16 scripts migrated to `/app` subdirectories
- ✅ All imports updated and working
- ✅ LLM abstraction integrated in `classify-cvs-with-llm.py`
- ✅ Manual testing of 3 critical workflows passes
- ✅ Original workflow scripts removed from `/scripts/`
- ✅ Ready for Story 2.5.4 documentation updates

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-11-06 | 1.0 | Story created from Epic 2.5 validation with pragmatic fixes | Sarah (PO) |
