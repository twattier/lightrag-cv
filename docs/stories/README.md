# Stories Index

> 📋 **Project**: LightRAG-CV - Intelligent CV-to-Job-Profile Matching POC
> 📋 **Related**: [Epics](../epics/README.md) | [PRD](../prd/index.md) | [Architecture](../architecture/index.md)

## Overview

This directory contains user story artifacts for the LightRAG-CV project. Each story represents an atomic, testable increment of functionality with clear acceptance criteria and QA gates.

**Total Stories**: 29 (across 4 epics)

---

## Epic 1: Foundation & Core Infrastructure (7 stories)

| # | Story | Status | Est. Effort | Dependencies |
|---|-------|--------|-------------|--------------|
| 1.1 | [Project Repository Setup and Docker Compose Scaffold](story-1.1.md) | Not Started | 2-3 hours | None |
| 1.2 | [PostgreSQL with pgvector and Apache AGE Setup](story-1.2.md) | Not Started | 4-6 hours | 1.1 |
| 1.3 | [LightRAG Server Integration with PostgreSQL Storage](story-1.3.md) | Not Started | 6-8 hours | 1.2 |
| 1.4 | [Ollama Integration Validation](story-1.4.md) | Not Started | 3-4 hours | 1.3 |
| 1.5 | [Docling Service Scaffold with GPU Profile Support](story-1.5.md) | Not Started | 4-6 hours | 1.1 |
| 1.6 | [Infrastructure Health Check Endpoint](story-1.6.md) | Not Started | 3-4 hours | 1.2, 1.3, 1.4, 1.5 |
| 1.7 | [Development Setup Documentation and Scripts](story-1.7.md) | Not Started | 4-6 hours | 1.1-1.6 |

**Epic 1 Total**: ~26-37 hours (3-5 days)

---

## Epic 2: Document Processing Pipeline (7 stories)

| # | Story | Status | Est. Effort | Dependencies |
|---|-------|--------|-------------|--------------|
| 2.1 | [Docling REST API Implementation](story-2.1.md) | Not Started | 6-8 hours | Epic 1 |
| 2.2 | [CIGREF English PDF Parsing and Quality Validation](story-2.2.md) | Not Started | 4-6 hours | 2.1 |
| 2.3 | [CV Dataset Acquisition and Preprocessing](story-2.3.md) | Not Started | 3-4 hours | 2.1 |
| 2.4 | [CV Parsing and Quality Validation](story-2.4.md) | Not Started | 4-6 hours | 2.3 |
| 2.5 | [LightRAG Knowledge Base Ingestion - CIGREF Profiles](story-2.5.md) | Not Started | 6-8 hours | 2.2 |
| 2.6 | [LightRAG Knowledge Base Ingestion - CVs](story-2.6.md) | Not Started | 6-8 hours | 2.4, 2.5 |
| 2.7 | [Document Processing Performance Baseline](story-2.7.md) | Not Started | 4-6 hours | 2.6 |

**Epic 2 Total**: ~33-46 hours (4-6 days)

---

## Epic 3: MCP Server & OpenWebUI Integration (8 stories)

| # | Story | Status | Est. Effort | Dependencies |
|---|-------|--------|-------------|--------------|
| 3.1 | [MCP Server Scaffold and Protocol Implementation](story-3.1.md) | Not Started | 8-12 hours | Epic 2 |
| 3.2 | [Core Search Tool - Profile Match Query](story-3.2.md) | Not Started | 6-8 hours | 3.1 |
| 3.3 | [Core Search Tool - Multi-Criteria Skill Search](story-3.3.md) | Not Started | 6-8 hours | 3.1 |
| 3.4 | [OpenWebUI Configuration and MCP Integration](story-3.4.md) | Not Started | 8-12 hours | 3.2, 3.3 |
| 3.5 | [Natural Language Query Interpretation](story-3.5.md) | Not Started | 6-8 hours | 3.4 |
| 3.6 | [Conversational Query Refinement](story-3.6.md) | Not Started | 6-8 hours | 3.5 |
| 3.7 | [Result Rendering and Display in Chat](story-3.7.md) | Not Started | 4-6 hours | 3.4 |
| 3.8 | [Basic Candidate Detail View](story-3.8.md) | Not Started | 4-6 hours | 3.7 |

**Epic 3 Total**: ~48-68 hours (6-9 days)

---

## Epic 4: Hybrid Retrieval & Match Explanation (7 stories)

| # | Story | Status | Est. Effort | Dependencies |
|---|-------|--------|-------------|--------------|
| 4.1 | [LightRAG Retrieval Mode Strategy Implementation](story-4.1.md) | Not Started | 8-12 hours | Epic 3 |
| 4.2 | [Graph-Based Relationship Extraction for Match Ranking](story-4.2.md) | Not Started | 8-12 hours | 4.1 |
| 4.3 | [Structured Match Explanation Generation](story-4.3.md) | Not Started | 6-8 hours | 4.2 |
| 4.4 | [Match Explanation Rendering in OpenWebUI](story-4.4.md) | Not Started | 4-6 hours | 4.3 |
| 4.5 | [Confidence Scoring and Ranking Refinement](story-4.5.md) | Not Started | 6-8 hours | 4.2 |
| 4.6 | [Query Performance Optimization and Testing](story-4.6.md) | Not Started | 8-12 hours | 4.1, 4.5 |
| 4.7 | [End-to-End User Acceptance Testing](story-4.7.md) | Not Started | 12-16 hours | 4.3, 4.4, 4.6 |

**Epic 4 Total**: ~52-74 hours (7-10 days)

---

## Project Summary

| Metric | Value |
|--------|-------|
| Total Stories | 29 |
| Total Estimated Effort | 159-225 hours |
| Estimated Calendar Time | 10-12 weeks (with overhead) |
| Stories per Epic (avg) | 7.25 |
| Average Story Size | 5.5-7.8 hours |

---

## Story Status Definitions

- **Not Started**: Story not yet begun
- **In Progress**: Active development underway
- **Blocked**: Waiting on dependencies
- **In Review**: Code review in progress
- **In QA**: QA testing in progress
- **QA Gate Pending**: Awaiting QA gate approval
- **Complete**: QA gate passed, story done
- **Deferred**: Postponed to future phase

---

## Story Workflow

```
Not Started → In Progress → In Review → In QA → QA Gate → Complete
                                              ↓
                                        (if issues)
                                              ↓
                                        Blocked/Rework
```

---

## Quick Navigation

### By Epic
- [Epic 1 Stories](../epics/epic-1.md#stories)
- [Epic 2 Stories](../epics/epic-2.md#stories)
- [Epic 3 Stories](../epics/epic-3.md#stories)
- [Epic 4 Stories](../epics/epic-4.md#stories)

### By Type
- **Foundation**: 1.1-1.7
- **Data Processing**: 2.1-2.7
- **Integration**: 3.1-3.8
- **Optimization**: 4.1-4.7

### QA Artifacts
- [QA Assessments](../qa/assessments/README.md)
- [QA Gates](../qa/gates/README.md)

---

## Related Documentation

### Requirements
- [PRD](../prd/index.md)
- [Requirements](../prd/requirements.md)
- [Epic List](../prd/epic-list.md)

### Architecture
- [Architecture Document](../architecture/index.md)
- [Tech Stack](../architecture/tech-stack.md)
- [Components](../architecture/components.md)
- [Database Schema](../architecture/database-schema.md)

### Development
- [Coding Standards](../architecture/coding-standards.md)
- [Source Tree](../architecture/source-tree.md)
- [Infrastructure and Deployment](../architecture/infrastructure-and-deployment.md)
