# Epics Index

> 📋 **Project**: LightRAG-CV - Intelligent CV-to-Job-Profile Matching POC
> 📋 **Related**: [PRD](../prd/index.md) | [Architecture](../architecture/index.md) | [Stories](../stories/README.md)

## Overview

This directory contains epic-level planning artifacts for the LightRAG-CV project. Each epic represents a major milestone in the development cycle with clear goals, deliverables, and success criteria.

---

## Epic List

### [Epic 1: Foundation & Core Infrastructure](epic-1.md)
**Goal**: Establish containerized development environment with PostgreSQL storage, LightRAG integration, and project scaffolding.

**Stories**: 7 | **Status**: Not Started | **Dependencies**: None

**Key Deliverables**:
- Docker Compose environment
- PostgreSQL with pgvector + Apache AGE
- LightRAG service with Ollama integration
- Health check endpoint

---

### [Epic 2: Document Processing Pipeline](epic-2.md)
**Goal**: Implement Docling service for parsing CIGREF profiles and CVs, validate extraction quality, and successfully load test data.

**Stories**: 7 | **Status**: Not Started | **Dependencies**: Epic 1

**Key Deliverables**:
- Docling REST API
- CIGREF profile parsing (validated)
- CV dataset (20-30 test CVs)
- LightRAG knowledge base populated

---

### [Epic 3: MCP Server & OpenWebUI Integration](epic-3.md)
**Goal**: Build MCP server exposing LightRAG-CV tools, integrate with OpenWebUI, and enable end-to-end natural language querying.

**Stories**: 8 | **Status**: Not Started | **Dependencies**: Epic 2

**Key Deliverables**:
- MCP protocol server
- Search tools (profile match, skill search)
- OpenWebUI integration
- Natural language query interpretation
- Conversational refinement

---

### [Epic 4: Hybrid Retrieval & Match Explanation](epic-4.md)
**Goal**: Implement intelligent retrieval mode selection, enhance ranking with graph insights, generate match explanations, and validate with test users.

**Stories**: 7 | **Status**: Not Started | **Dependencies**: Epic 3

**Key Deliverables**:
- Hybrid retrieval mode selection
- Graph-based relationship ranking
- Structured match explanations
- Confidence scoring
- User acceptance testing (UAT)

---

## Epic Summary

| Epic | Stories | Status | Dependencies | Estimated Duration |
|------|---------|--------|--------------|-------------------|
| [Epic 1](epic-1.md) | 7 | Not Started | None | 2-3 weeks |
| [Epic 2](epic-2.md) | 7 | Not Started | Epic 1 | 3 weeks |
| [Epic 3](epic-3.md) | 8 | Not Started | Epic 2 | 3 weeks |
| [Epic 4](epic-4.md) | 7 | Not Started | Epic 3 | 3 weeks |
| **Total** | **29** | - | - | **10-12 weeks** |

---

## Project Timeline

```
Week 1:    Technical spikes + Epic 1 planning
Week 2-3:  Epic 1 (Foundation & Core Infrastructure)
Week 4-6:  Epic 2 (Document Processing Pipeline)
Week 7-9:  Epic 3 (MCP Server & OpenWebUI Integration)
Week 10-12: Epic 4 (Hybrid Retrieval & Match Explanation)
```

---

## Epic Status Definitions

- **Not Started**: Epic not yet begun
- **In Progress**: Active development underway
- **Blocked**: Waiting on dependencies or external factors
- **In QA**: Development complete, testing in progress
- **Complete**: All stories done, QA gates passed
- **Deferred**: Postponed to future phase

---

## Related Documentation

### Requirements & Architecture
- [Product Requirements Document (PRD)](../prd/index.md)
- [Architecture Document](../architecture/index.md)
- [Epic List (PRD)](../prd/epic-list.md)

### Planning Artifacts
- [Stories Index](../stories/README.md)
- [QA Assessments](../qa/assessments/README.md)
- [QA Gates](../qa/gates/README.md)

### Implementation Resources
- [Tech Stack](../architecture/tech-stack.md)
- [Coding Standards](../architecture/coding-standards.md)
- [Database Schema](../architecture/database-schema.md)
- [Source Tree](../architecture/source-tree.md)
