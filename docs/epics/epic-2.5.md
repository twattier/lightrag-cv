# Epic 2.5: Script Refactoring & Application Structure

> 📋 **Architecture References**:
> - [Source Tree](../architecture/source-tree.md) - Repository structure
> - [Coding Standards](../architecture/coding-standards.md) - Development practices
> - [Tech Stack](../architecture/tech-stack.md) - Python 3.11, Docker Compose

**Epic Goal**: Restructure the `/scripts` directory into a clean, maintainable application architecture by separating infrastructure scripts from workflow-specific code, consolidating shared services, abstracting LLM provider configuration to support multiple providers (Ollama, OpenAI-compatible via LiteLLM), and eliminating obsolete scripts, while ensuring documentation remains accurate.

## Context

This is a **brownfield refactoring epic** to improve the organization of utility scripts that have accumulated during Epic 2 development. The current flat `/scripts` directory contains 26 mixed-purpose scripts that make it difficult to distinguish infrastructure operations from domain-specific workflows.

### Current State (26 scripts)
- Infrastructure scripts: `setup.sh`, health checks, GPU service management, Ollama validation
- CIGREF workflow scripts: `ingest-cigref*.py`, `prepare-cigref*.py`, `analyze-cigref*.py`, etc.
- CV workflow scripts: `parse-cvs.py`, `classify-cvs*.py`, `download*.py`, etc.
- Shared utilities: `config.py` (centralized configuration, **Ollama-only**)
- Artifacts: `query-entities.sql`, `requirements.txt`
- **LLM Provider Lock-in**: Scripts hardcoded to use Ollama (`OLLAMA_BASE_URL`, `OLLAMA_LLM_MODEL`)

### Target State
- `/scripts/` - 6 infrastructure-only scripts
- `/app/shared/` - Shared configuration with **multi-provider LLM abstraction** (Ollama, OpenAI-compatible)
- `/app/cigref_ingest/` - CIGREF-specific workflows (7 scripts)
- `/app/cv_ingest/` - CV-specific workflows (9 scripts)
- `/app/artifacts/` - SQL queries and development artifacts
- 3-5 obsolete scripts removed or archived
- **Unified LLM config pattern**: `LLM_BINDING_HOST`, `LLM_MODEL`, `EMBEDDING_BINDING_HOST`, `EMBEDDING_MODEL` (matching LightRAG service)

## Stories

### Story 2.5.1: Create Application Structure & Migrate Shared Services
**Effort**: 2-3 hours | **Status**: Not Started

Create `/app` directory structure and migrate shared `config.py` to centralized location.

**Key Tasks**:
- Create `/app/shared/`, `/app/cigref_ingest/`, `/app/cv_ingest/`, `/app/artifacts/` directories
- Move `scripts/config.py` → `app/shared/config.py`
- Add `__init__.py` files for proper Python module structure
- Update `config.py` imports in 2-3 sample scripts to validate pattern
- Verify sample scripts execute successfully with new import paths

**Acceptance Criteria**:
- ✅ New `/app` directory structure exists with proper `__init__.py` files
- ✅ `app/shared/config.py` functions identically to original
- ✅ Sample scripts execute successfully with `from app.shared.config import settings`
- ✅ Zero breaking changes to LightRAG, Docling, PostgreSQL, or Ollama service calls

---

### Story 2.5.2: LLM Provider Abstraction & Multi-Provider Support
**Effort**: 3-4 hours | **Status**: ⚠️ In Review (CONCERNS) | **Dependencies**: Story 2.5.1 ✅

Abstract LLM provider configuration to support multiple providers (Ollama, OpenAI-compatible via LiteLLM) using unified environment variables matching LightRAG service patterns.

**Key Tasks**:
- **Update `app/shared/config.py`** to support multi-provider LLM configuration:
  - Add `LLM_BINDING` (default: `ollama`, options: `ollama`, `openai`, `litellm`)
  - Add `LLM_BINDING_HOST` (replaces `OLLAMA_BASE_URL` for unified access)
  - Add `LLM_MODEL` (replaces `OLLAMA_LLM_MODEL`)
  - Add `EMBEDDING_BINDING` (default: `ollama`)
  - Add `EMBEDDING_BINDING_HOST`
  - Add `EMBEDDING_MODEL` (replaces `OLLAMA_EMBEDDING_MODEL`)
  - Add `EMBEDDING_DIM` (default: `1024` for bge-m3)
  - Keep backward compatibility: Read `OLLAMA_*` vars if new vars not set

- **Create `app/shared/llm_client.py`** - LLM provider abstraction layer:
  - `get_llm_client()` factory function returning provider-specific client
  - Support Ollama provider: `/api/generate` endpoint (existing)
  - Support OpenAI-compatible provider: `/v1/chat/completions` endpoint (LiteLLM)
  - Unified interface: `generate(prompt, model, temperature, max_tokens, format='json')` → response
  - Handle provider-specific request/response formats
  - Timeout and retry logic

- **Update `.env.example`** with new variables:
  ```bash
  # LLM Provider Configuration (matches lightrag service)
  LLM_BINDING=ollama              # Options: ollama, openai, litellm
  LLM_BINDING_HOST=http://host.docker.internal:11434
  LLM_MODEL=qwen2.5:7b-instruct-q4_K_M
  LLM_BINDING_API_KEY=            # Required when LLM_BINDING=openai or litellm
  LLM_TIMEOUT=1200

  # Embedding Provider Configuration
  EMBEDDING_BINDING=ollama
  EMBEDDING_BINDING_HOST=http://host.docker.internal:11434
  EMBEDDING_MODEL=bge-m3:latest
  EMBEDDING_BINDING_API_KEY=      # Required when EMBEDDING_BINDING=openai
  EMBEDDING_DIM=1024
  EMBEDDING_TIMEOUT=600

  # Backward compatibility (deprecated, use LLM_BINDING_HOST/LLM_MODEL)
  OLLAMA_BASE_URL=http://host.docker.internal:11434
  OLLAMA_LLM_MODEL=qwen2.5:7b-instruct-q4_K_M
  ```

- **Test LLM abstraction with simple one-liner**:
  ```bash
  python -c "from app.shared.llm_client import get_llm_client; print(get_llm_client().generate('Hello'))"
  ```

**Acceptance Criteria**:
- ⚠️ `app/shared/config.py` supports multi-provider configuration with backward compatibility (PARTIAL - fallback not implemented)
- ✅ `app/shared/llm_client.py` provides unified interface for Ollama and OpenAI-compatible providers
- ⚠️ LLM abstraction tested with simple one-liner (PARTIAL - static validation only)
- ⚠️ LightRAG service health check passes: `curl http://localhost:9621/health` (NOT TESTED - services not running)
- ✅ `.env.example` documents new unified variables matching LightRAG service pattern
- ❌ Existing Ollama workflows continue to function without `.env` changes (FAIL - backward compatibility not implemented)
- ✅ Documentation updated with provider configuration examples

**QA Review Results** (2025-11-06):
- **Gate**: CONCERNS (Quality Score: 70/100)
- **Gate File**: [docs/qa/gates/2.5.2-llm-provider-abstraction.yml](../qa/gates/2.5.2-llm-provider-abstraction.yml)
- **Story File**: [docs/stories/story-2.5.2.llm-provider-abstraction.md](../stories/story-2.5.2.llm-provider-abstraction.md)
- **Status**: Changes Required
- **Blocker**: Backward compatibility NOT implemented - missing OLLAMA_* fallback chain in app/shared/config.py (AC #6)
- **Required Fixes**:
  1. Add fallback pattern: `LLM_BINDING_HOST = os.getenv("LLM_BINDING_HOST") or os.getenv("OLLAMA_BASE_URL", "default")`
  2. Add missing `llm_url` and `embedding_url` property methods
  3. Verify backward compatibility with existing scripts using OLD env vars
- **Strengths**: Excellent architecture (95/100 code quality), comprehensive documentation, clean abstraction design
- **Next Steps**: Fix blocker issues, re-test, update gate to PASS

---

### Story 2.5.3: Migrate CIGREF & CV Workflow Scripts
**Effort**: 3-4 hours | **Status**: Not Started | **Dependencies**: Story 2.5.2

Move all CIGREF and CV workflow scripts to appropriate `/app` subdirectories with updated imports, leveraging the new LLM provider abstraction.

**Key Tasks**:
- **CIGREF Workflows** → `/app/cigref_ingest/`:
  - `ingest-cigref.py`, `ingest-cigref-batched.py`
  - `prepare-cigref-for-lightrag.py`
  - `analyze-cigref-parsing.py`, `test-cigref-parsing.py`
  - `enrich-cigref-hierarchy.py`, `test-header-extraction.py`

- **CV Workflows** → `/app/cv_ingest/`:
  - `parse-cvs.py`, `classify-cvs-with-llm.py`
  - `download-cvs.py`, `download_cv_samples.py`, `explore_and_download_cvs.py`
  - `download_sample_cvs.sh`
  - `create-parsed-manifest.py`
  - `select-validation-sample.py`, `validate-classification.py`

- Update all imports: `from config import settings` → `from app.shared.config import settings`
- **Update `classify-cvs-with-llm.py`**: Replace direct `httpx.post()` calls with `llm_client.generate()` abstraction
- **Run 3 critical workflows manually** to verify:
  - `python -m app.cigref_ingest.ingest_cigref_batched` (test with 1 doc)
  - `python -m app.cv_ingest.parse_cvs` (test with 1 CV)
  - `python -m app.cv_ingest.classify_cvs_with_llm` (test with 1 CV)

**Acceptance Criteria**:
- ✅ 16+ scripts migrated to `/app` subdirectories
- ✅ All import paths updated and validated
- ✅ `classify-cvs-with-llm.py` uses `llm_client.generate()` abstraction from Story 2.5.2
- ✅ **Manual testing complete**: 3 critical workflows execute successfully:
  - CIGREF ingestion workflow (1 batch test)
  - CV parsing workflow (1 CV test)
  - LLM classification workflow (1 CV test)
- ✅ No changes to service API calls or `.env` variables
- ✅ If any ImportError occurs, fix and re-test before marking complete

---

### Story 2.5.4: Cleanup & Documentation Update
**Effort**: 2-3 hours | **Status**: Not Started | **Dependencies**: Story 2.5.3

Remove obsolete scripts, consolidate artifacts, and update all documentation to reflect new structure and LLM provider configuration.

**Key Tasks**:
- **Obsolete Script Identification**:
  - Compare `download-cvs.py`, `download_cv_samples.py`, `explore_and_download_cvs.py` for duplicates
  - Review test scripts for relevance (`test-cigref-parsing.py`, `test-header-extraction.py`)
  - Identify development artifacts vs. production workflows
  - Remove or archive obsolete versions to `.archive/` folder

- **Artifact Consolidation**:
  - Move `query-entities.sql` to `/app/artifacts/` (if used) or remove (if obsolete)
  - Move `scripts/requirements.txt` to `/app/requirements.txt` (if applicable)

- **Documentation Updates**:
  - Update [source-tree.md](../architecture/source-tree.md) with new `/app` structure
  - Update [coding-standards.md](../architecture/coding-standards.md) import patterns
  - Update [tech-stack.md](../architecture/tech-stack.md) with multi-provider LLM support
  - Update Story 2.3, 2.4, 2.5 script execution commands if referenced
  - Create `/app/README.md` explaining application structure and LLM provider configuration
  - Update root `README.md` with new script locations and LLM provider setup
  - Update `.env.example` documentation with LLM provider examples (already done in Story 2.5.2)

**Acceptance Criteria**:
- ✅ 3-5 obsolete scripts removed or archived
- ✅ [source-tree.md](../architecture/source-tree.md) accurately reflects new structure with LLM abstraction layer
- ✅ [coding-standards.md](../architecture/coding-standards.md) import patterns updated
- ✅ [tech-stack.md](../architecture/tech-stack.md) documents multi-provider LLM support
- ✅ All story documentation references validated (no broken links)
- ✅ `/app/README.md` created with structure explanation and LLM provider configuration guide
- ✅ Root `README.md` updated with new script locations and LLM provider setup instructions

---

## Epic Status

- **Status**: Not Started
- **Story Count**: 4
- **Estimated Effort**: 12-16 hours
- **Dependencies**: Epic 2 (Stories 2.1-2.5) ✅ Complete
- **Blocked By**: None
- **Type**: Brownfield Refactoring (organizational + multi-provider LLM abstraction)

## Success Criteria

1. **Clear Separation**: Infrastructure scripts (`/scripts`) vs. application workflows (`/app`)
2. **Zero Breaking Changes**: All service integrations (LightRAG, Docling, PostgreSQL, Ollama) unchanged
3. **Multi-Provider LLM Support**: Scripts work with both Ollama and OpenAI-compatible providers via unified config
4. **Configuration Alignment**: Script LLM config matches LightRAG service patterns (`LLM_BINDING_HOST`, `LLM_MODEL`, `EMBEDDING_BINDING_HOST`, `EMBEDDING_MODEL`)
5. **Backward Compatibility**: Existing `OLLAMA_*` environment variables continue to work without changes
6. **Workflow Validation**: CIGREF ingestion and CV parsing execute successfully from new locations (manual test with 1 doc/CV each)
7. **Documentation Accuracy**: All cross-references updated, no broken links
8. **Reduced Technical Debt**: 20-30% reduction in script count through obsolete file removal
9. **Improved Developer Onboarding**: New structure self-explanatory via documentation

## Risk Mitigation

**Primary Risks**:
1. Breaking existing CIGREF or CV ingestion workflows due to incorrect import paths
2. LLM provider abstraction introducing bugs in existing Ollama-based workflows
3. Configuration changes breaking LightRAG service integration

**Mitigation**:
1. **Import Path Safety**: Story 2.5.1 validates pattern with sample scripts before creating LLM abstraction in 2.5.2
2. **LLM Abstraction Safety**: Story 2.5.2 tests abstraction with one-liner (not dependent on migrated scripts), checks LightRAG health
3. **Workflow Migration Safety**: Story 2.5.3 runs 3 critical workflows manually after migration
4. **Quick Rollback**: Git-based rollback strategy
   - Before Story 2.5.3: `git commit -m "Checkpoint before app structure migration"`
   - If rollback needed: `git reset --hard HEAD~1`
5. **Manual Testing**: Run scripts after migration - if ImportError, fix and re-test
6. **Incremental Deployment**: Can deploy Story 2.5.1 independently; 2.5.2 must complete before 2.5.3; 2.5.4 is final cleanup

**Rollback Plan**:
1. `git reset --hard HEAD~1` (or specific commit before Story 2.5.3)
2. Verify scripts run from `/scripts/` location
3. Remove `/app` directory if needed

## Compatibility Requirements

- ✅ **Service APIs unchanged**: LightRAG, Docling, PostgreSQL, Ollama integrations remain identical
- ✅ **Database schema unchanged**: No migrations required
- ✅ **Import path updates only**: `from config` → `from app.shared.config`
- ✅ **Environment variables unchanged**: `.env` file unmodified (backward compatibility)
- ✅ **Docker Compose unchanged**: No service definition changes

## New Directory Structure

```
lightrag-cv/
├── scripts/                          # Infrastructure only (6 files)
│   ├── setup.sh
│   ├── health-check.sh
│   ├── health-check.py
│   ├── start-docling-gpu.sh
│   ├── restart-docling-gpu.sh
│   └── validate-ollama.py
│
├── app/                              # Application workflows (NEW)
│   ├── __init__.py
│   ├── README.md
│   ├── requirements.txt
│   │
│   ├── shared/                       # Shared services
│   │   ├── __init__.py
│   │   ├── config.py                 # Multi-provider LLM config
│   │   └── llm_client.py             # LLM provider abstraction (Ollama, OpenAI-compatible)
│   │
│   ├── cigref_ingest/                # CIGREF workflows (7 files)
│   │   ├── __init__.py
│   │   ├── ingest-cigref.py
│   │   ├── ingest-cigref-batched.py
│   │   ├── prepare-cigref-for-lightrag.py
│   │   ├── analyze-cigref-parsing.py
│   │   ├── test-cigref-parsing.py
│   │   ├── enrich-cigref-hierarchy.py
│   │   └── test-header-extraction.py
│   │
│   ├── cv_ingest/                    # CV workflows (9 files)
│   │   ├── __init__.py
│   │   ├── parse-cvs.py
│   │   ├── classify-cvs-with-llm.py
│   │   ├── download-cvs.py
│   │   ├── download_cv_samples.py
│   │   ├── create-parsed-manifest.py
│   │   ├── select-validation-sample.py
│   │   └── validate-classification.py
│   │
│   └── artifacts/                    # SQL queries, dev artifacts
│       └── query-entities.sql
│
├── services/                         # Docker services (unchanged)
├── data/                             # Data files (unchanged)
├── docs/                             # Documentation (updated)
└── volumes/                          # Docker volumes (unchanged)
```

---

**Related Documentation:**
- [PRD Epic 2 (Full)](../prd/epic-2-document-processing-pipeline.md)
- [Architecture - Source Tree](../architecture/source-tree.md)
- [Architecture - Coding Standards](../architecture/coding-standards.md)
- [Epic List](../prd/epic-list.md)
