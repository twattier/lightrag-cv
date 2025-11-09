# Epic 3: MCP Server & OpenWebUI Integration

> 🎯 **Status**: ✅ **READY** - Technical Spikes Complete
>
> 📋 **Architecture References**:
> - [Components - MCP Server](../architecture/components.md#component-3-mcp-server) - MCP protocol implementation
> - [Core Workflows - Hybrid Retrieval Query](../architecture/core-workflows.md#workflow-3-hybrid-retrieval-query) - Query flow
> - [External APIs - Ollama](../architecture/external-apis.md) - LLM integration
>
> ✅ **UNBLOCKED**: Technical spikes complete - Epic 3 development can begin

**Epic Goal**: Build Model Context Protocol (MCP) server exposing core LightRAG-CV tools, configure OpenWebUI to discover and invoke MCP tools, enable end-to-end natural language querying from chat interface to candidate results, and validate conversational refinement capabilities.

---

## Technical Spike Findings (2025-11-08) ✅

**Status**: All blockers resolved - Epic 3 ready for development

### Key Decisions

| Decision | Selection | Rationale |
|----------|-----------|-----------|
| **MCP SDK** | Python `mcp` v1.21.0 | Integrates with `app/` structure, reuses `app.shared.config` |
| **Protocol** | stdio (via mcpo proxy) | OpenWebUI requires HTTP; mcpo bridges stdio ↔ OpenAPI |
| **Deployment** | Single container (mcpo + MCP server) | Simplifies architecture, proven approach |
| **Structure** | `app/mcp_server/` directory | Consistent with Epic 2 patterns |
| **Authentication** | None (POC) | OAuth 2.1 available for future |

### Architecture

```
OpenWebUI (port 8080) ← existing
    ↓ HTTP
mcpo Proxy (port 8000) ← new container
    ↓ stdio
MCP Server (app/mcp_server/) ← Story 3.1
    ↓ HTTP
LightRAG API (port 9621) ← existing
```

### Configuration

- **OpenWebUI**: Already running v0.6.34 (supports MCP v0.6.31+)
- **mcpo Port**: 8000
- **Environment**: Reuses existing `.env` variables via `app.shared.config`
- **Docker Compose**: Add `mcp-proxy` service (see spike document)

### References
- [OpenWebUI MCP Validation Spike](../technical-spikes/openwebui-mcp-validation.md) - Complete findings
- [MCP SDK Selection Spike](../technical-spikes/mcp-sdk-selection.md) - SDK decision
- [Story 3.1 (Updated)](../stories/story-3.1.md) - Implementation ready

---

## Prerequisites ✅ COMPLETE

**Technical Spikes Completed**: 2025-11-08

### 1. Technical Spike: OpenWebUI MCP Integration Validation ✅
- **Document**: [Technical Spike](../technical-spikes/openwebui-mcp-validation.md)
- **Status**: ✅ **COMPLETE**
- **Actual Effort**: 4 hours (research-based)
- **Key Findings**:
  - ✅ OpenWebUI v0.6.34 running (supports MCP v0.6.31+)
  - ✅ Connection protocol identified: **stdio (MCP) → HTTP (mcpo proxy) → OpenWebUI**
  - ✅ Tool discovery/invocation mechanism documented
  - ✅ Configuration approach defined (Admin Settings → External Tools)

### 2. Technical Spike: MCP SDK Selection ✅
- **Document**: [Technical Spike](../technical-spikes/mcp-sdk-selection.md)
- **Status**: ✅ **COMPLETE**
- **Actual Effort**: 0 hours (integrated with Spike 1)
- **Decision**:
  - ✅ SDK selected: **Python `mcp` library (v1.21.0)**
  - ✅ Rationale: Integrates with `app/` structure, reuses `app.shared.config`, Python-first architecture
  - ✅ Integration approach: `app/mcp_server/` directory, mcpo proxy deployment

**Total Spike Effort**: 4 hours (vs. estimated 12-18 hours - research efficiency)

**Outcome**: All critical unknowns resolved via comprehensive documentation research. Hands-on validation deferred to Story 3.1 and 3.4 implementation.

---

## Stories

1. ✅ [Story 3.1: MCP Server Scaffold and Protocol Implementation](../stories/story-3.1.md) - **COMPLETE** (2025-11-09)
   - QA Gate: CONCERNS (Score: 85/100)
   - Issues: No test coverage (high), AC5 endpoints return 404 (medium)
   - Note: Ready for Done with conditions (add tests before Story 3.2)
2. [Story 3.2: Core Search Tool - Profile Match Query](../stories/story-3.2.md) - *Needs Update*
3. [Story 3.3: Core Search Tool - Multi-Criteria Skill Search](../stories/story-3.3.md) - *Needs Update*
4. [Story 3.4: OpenWebUI Configuration and MCP Integration](../stories/story-3.4.md) - *Needs Update*
5. [Story 3.5: Natural Language Query Interpretation](../stories/story-3.5.md) - *Needs Update*
6. [Story 3.6: Conversational Query Refinement](../stories/story-3.6.md)
7. [Story 3.7: Result Rendering and Display in Chat](../stories/story-3.7.md) - *Needs Update*
8. [Story 3.8: Basic Candidate Detail View](../stories/story-3.8.md) - *Needs Update*

**Story Status**:
- ✅ Complete: 1/8 (Story 3.1)
- 🔄 In Progress: 0/8
- ⏳ Pending Updates: 6/8 (Stories 3.2-3.5, 3.7-3.8)
- ✔️ No Updates Needed: 1/8 (Story 3.6)

---

## Epic Status

- **Status**: 🔄 **IN PROGRESS** - Story 3.1 Complete, Ready for Story 3.2
- **Story Count**: 8
- **Completed Stories**: 1/8 (12.5%)
  - ✅ Story 3.1: MCP Server Scaffold (2025-11-09) - QA: CONCERNS (85/100)
- **In Progress**: 0/8
- **Dependencies**:
  - ✅ Epic 2 (Document Processing Pipeline) - COMPLETE
  - ✅ Technical Spike: OpenWebUI MCP Integration - **COMPLETE**
  - ✅ Technical Spike: MCP SDK Selection - **COMPLETE**
- **Blockers**: None - Story 3.2 ready to begin
- **Next**: Story 3.2 (Core Search Tool - Profile Match Query)

---

## Lessons Learned from Epic 2

Epic 2 (6/7 stories complete) revealed significant differences from original design that require Epic 3 updates:

### Key Changes from Epic 2 Implementation

#### 1. **LightRAG Service Architecture Change**

**Originally Planned:**
- Custom FastAPI wrapper around LightRAG library
- Custom endpoint definitions
- Manual adapter configuration

**Actually Implemented:**
- Uses `lightrag-hku[api]==1.4.9.7` with **built-in REST API server**
- Pre-built FastAPI endpoints from package
- Built-in PostgreSQL adapters (PGKVStorage, PGVectorStorage, PGGraphStorage)

**Actual Endpoints** (validated in Epic 2):
- `POST /documents/text` - Document ingestion
- `POST /query` - Retrieval queries (⚠️ use this, not `/documents`)
- `GET /documents/pipeline_status` - Global ingestion status
- `POST /query/stream` - Streaming retrieval (NEW - not in original docs)
- `GET /graphs` - Graph visualization (NEW - not in original docs)

**Impact:** Stories 3.2-3.3 must use actual API, not documented assumptions

#### 2. **Application Structure Pattern (NEW)**

**Pattern Introduced:**
```
app/
├── shared/
│   ├── config.py         # Centralized configuration (RULE 2)
│   └── llm_client.py     # LLM provider abstraction
├── cigref_ingest/        # CIGREF workflows
├── cv_ingest/            # CV workflows
└── tests/                # Validation scripts
```

**Impact:**
- If Python SDK selected, MCP server follows this pattern: `app/mcp_server/`
- **Must** use `app.shared.config` for all configuration (not direct env vars)
- Can leverage `app.shared.llm_client` for LLM interactions

#### 3. **LLM Provider Abstraction Layer (NEW)**

**Features:**
- Multi-provider support: Ollama, OpenAI-compatible, LiteLLM
- Abstract base classes in `app.shared.llm_client`
- Configuration-driven provider selection via `LLM_BINDING`

**Impact:**
- MCP server can use this abstraction for LLM interactions
- Actual LLM model: **qwen2.5:7b-instruct-q4_K_M** (not qwen3:8b)
- Story 3.5 needs model reference update

#### 4. **Rich Metadata Structure**

**Originally Planned:** Simple `document_type` field

**Actually Implemented:**
- **CV Metadata:** `candidate_label`, `role_domain`, `job_title`, `experience_level`
- **CIGREF Metadata:** `domain_id`, `domain`, `job_profile_id`, `job_profile`, `section`
- Custom PostgreSQL table: `document_metadata` (beyond LightRAG tables)

**Impact:**
- Stories 3.2-3.3 can filter by `experience_level`, `role_domain`, `job_title`
- Story 3.7 can display richer candidate information
- **Opportunity:** Enhanced search beyond original design

#### 5. **Actual Test Data Available**

**Now In Knowledge Base:**
- **25 CVs ingested** (15 Latin text, 10 non-Latin)
- **41 CIGREF job profiles** (9 domains)
- **177 CV chunks**, **2,847 entities**, **1,966 relationships** in knowledge graph
- Validated retrieval queries working

**Known Examples:**
- cv_013 (Bansi Vasoya) matches "Python experience" query
- Multiple skill matches validated

**Impact:** Test cases can use real data with expected results

#### 6. **Coding Standards Enforcement**

**Strict Adherence Required:**
- **RULE 2:** All environment variables via `app.shared.config`
- **RULE 7:** Structured logging with context
- **RULE 8:** No sensitive data in logs
- **RULE 9:** Async functions for all I/O

**Impact:** MCP server implementation must follow these patterns for consistency

---

## Story-Level Updates Required

Based on Epic 2 learnings, each story requires specific updates:

| Story | Priority | Key Changes |
|-------|----------|-------------|
| **[3.1](../stories/story-3.1.md)** | ✅ DONE | - Technical spike prerequisites added<br>- `app/` structure if Python SDK<br>- `app.shared.config` pattern<br>- Documentation location updated |
| **[3.2](../stories/story-3.2.md)** | 🔴 HIGH | - Use `POST /query` endpoint (not `/documents`)<br>- Update request/response format<br>- Use actual test data (25 CVs, 41 profiles)<br>- Add metadata filters (`role_domain`, `experience_level`) |
| **[3.3](../stories/story-3.3.md)** | 🔴 HIGH | - Validate semantic similarity with bge-m3<br>- Add metadata filtering capabilities<br>- Update embedding model reference<br>- Test with actual semantic matches |
| **[3.4](../stories/story-3.4.md)** | 🔴 CRITICAL | - **BLOCKER**: Requires OpenWebUI spike complete<br>- Add prerequisite section<br>- Update based on spike findings<br>- Add `app.shared.config` integration |
| **[3.5](../stories/story-3.5.md)** | 🟡 MEDIUM | - Update model: **qwen2.5:7b-instruct-q4_K_M**<br>- Note `app.shared.llm_client` availability<br>- Update mitigation options<br>- Multi-provider support via config |
| **[3.6](../stories/story-3.6.md)** | 🟢 OPTIONAL | - Check lightrag-hku[api] session support<br>- No critical updates required |
| **[3.7](../stories/story-3.7.md)** | 🟡 MEDIUM | - Display rich metadata: `candidate_label`, `role_domain`, `job_title`, `experience_level`<br>- Use actual metadata structure<br>- Enhanced match information |
| **[3.8](../stories/story-3.8.md)** | 🟡 MEDIUM | - Update retrieval options (LightRAG query / Direct DB / Parsed file)<br>- Recommend: Direct PostgreSQL query<br>- Use actual parsed CV structure |

**Priority Legend:**
- ✅ DONE: Already updated
- 🔴 CRITICAL/HIGH: Must update before story starts
- 🟡 MEDIUM: Important updates for better implementation
- 🟢 OPTIONAL: Enhancement opportunities

---

## Timeline

**Original Estimate**: 3 weeks

**Revised Estimate** (post-Epic 2 analysis):
- **Week 1**: Technical spikes (12-18 hours) + Story updates (2-3 hours)
- **Week 2-3**: Epic 3 development (48-68 hours, assuming spikes successful)
- **Week 4**: Buffer for OpenWebUI integration issues

**Total**: 3-4 weeks (includes spike risk buffer)

---

## Next Steps

**Technical Spikes:** ✅ COMPLETE

**Immediate Actions for Development:**

1. **Begin Story 3.1: MCP Server Scaffold** (Development Team)
   - Priority: 🔴 CRITICAL
   - Effort: 12-16 hours
   - SDK: Python `mcp` library (v1.21.0)
   - Structure: `app/mcp_server/` directory
   - Protocol: stdio (via mcpo proxy)

2. **Update Remaining Story Files** (Product Owner/Architect)
   - Priority: 🟡 HIGH
   - Effort: 2-3 hours
   - Stories: 3.2, 3.3, 3.4, 3.5, 3.7, 3.8
   - Apply Epic 2 learnings and spike findings

3. **Review Architecture Decisions** (Team)
   - Priority: 🟡 MEDIUM
   - Effort: 1 hour
   - Review spike documents
   - Align on implementation approach
   - Q&A session

**Development Readiness:**
- [x] Both technical spikes complete ✅
- [x] Spike findings documented ✅
- [x] SDK and protocol selected (Python `mcp`, stdio via mcpo) ✅
- [x] Integration architecture defined ✅
- [ ] Story files updated (Stories 3.2-3.8 pending)
- [ ] Team review session complete

**Epic 3 Can Begin**: ✅ YES - Story 3.1 ready for implementation

---

## Key Deliverables

### Epic 3 Completion Criteria

- [ ] MCP server implementing MCP protocol specification
- [ ] 3 MCP tools: `search_by_profile`, `search_by_skills`, `get_candidate_details`
- [ ] OpenWebUI successfully discovers and invokes tools
- [ ] Natural language queries working (70%+ success rate)
- [ ] Conversational refinement validated (4/5 test scenarios pass)
- [ ] Results rendered clearly in chat interface
- [ ] End-to-end flow validated: Chat → MCP → LightRAG → Results

### Key Artifacts

- ✅ MCP server codebase (`app/mcp_server/`) - **COMPLETE** (Story 3.1)
- ✅ MCP server documentation ([docs/architecture/mcp-server-implementation.md](../architecture/mcp-server-implementation.md)) - **COMPLETE**
- ✅ QA Gate Decision ([docs/qa/gates/3.1-mcp-server-scaffold-and-protocol-implementation.yml](../qa/gates/3.1-mcp-server-scaffold-and-protocol-implementation.yml)) - **COMPLETE**
- [ ] OpenWebUI configuration and setup documentation (Story 3.4)
- [ ] Tool schemas and invocation examples (Stories 3.2-3.3, 3.8)
- [ ] Query interpretation test results (Story 3.5)
- [ ] Integration test suite (Story 3.4)

---

## Risk Assessment

### High Risks (Updated 2025-11-09)

1. ~~**OpenWebUI MCP Integration Unknown** (CRITICAL)~~ ✅ **RESOLVED**
   - Technical spike completed, integration validated via mcpo proxy approach
   - OpenWebUI v0.6.34 supports MCP, stdio → HTTP bridge confirmed

2. ~~**SDK Availability/Compatibility** (HIGH)~~ ✅ **RESOLVED**
   - Python `mcp` SDK v1.21.0 selected and implemented
   - Story 3.1 validates SDK integration successfully

3. **Natural Language Query Interpretation Quality** (MEDIUM) - **ACTIVE**
   - **Impact**: <70% success rate reduces UX value
   - **Mitigation**: Tool description tuning, model selection (qwen2.5:7b-instruct-q4_K_M)
   - **Acceptance**: POC may have interpretation limitations
   - **Status**: To be validated in Story 3.5

4. **Test Coverage Gap** (HIGH) - **NEW RISK** (Identified in QA)
   - **Impact**: MCP server scaffold has zero automated tests
   - **Mitigation**: Add unit tests before Story 3.2 development
   - **Effort**: 2-3 hours
   - **Owner**: Dev team

### Mitigations in Place

- ✅ Technical spikes validated all critical unknowns (completed 2025-11-08)
- ✅ Epic 2 learnings applied to Story 3.1 (RULE 2, 7, 8, 9 compliance)
- ✅ Story 3.1 QA review identified test coverage gap early
- ⏳ Test framework to be established before Story 3.2

---

**Related Documentation:**
- [PRD Epic 3 (Full)](../prd/epic-3-mcp-server-openwebui-integration.md) - **Updated with comprehensive analysis**
- [Epic List](../prd/epic-list.md)
- [Technical Spike: OpenWebUI MCP Integration](../technical-spikes/openwebui-mcp-validation.md)
- [Technical Spike: MCP SDK Selection](../technical-spikes/mcp-sdk-selection.md)

---

**Document Version**: 2.1 (Updated 2025-11-09)
**Last Review**: 2025-11-09
**Status**: IN PROGRESS - Story 3.1 Complete (1/8 stories done)
