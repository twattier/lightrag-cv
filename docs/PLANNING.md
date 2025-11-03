# LightRAG-CV Planning Hub

> 📋 **Project**: LightRAG-CV - Intelligent CV-to-Job-Profile Matching POC
> 📋 **Purpose**: Central hub for all planning, development tracking, and QA artifacts

---

## Quick Start

### For Product Owners
- 📋 **[PRD (Product Requirements Document)](prd/index.md)** - Complete requirements and business context
- 🎯 **[Epic List](epics/README.md)** - High-level milestones and deliverables
- ✅ **[Checklist Results Report](prd/checklist-results-report.md)** - 87% readiness validation

### For Developers
- 📖 **[Architecture Document](architecture/index.md)** - Technical implementation guide
- 📝 **[Stories Index](stories/README.md)** - All 29 user stories with acceptance criteria
- 🏗️ **[Source Tree](architecture/source-tree.md)** - Repository structure
- 🔧 **[Tech Stack](architecture/tech-stack.md)** - Definitive technology selections

### For QA
- 🔍 **[QA Assessments](qa/assessments/README.md)** - Story testing documentation
- 🚪 **[QA Gates](qa/gates/README.md)** - Quality approval checkpoints
- 🧪 **[Test Strategy](architecture/test-strategy.md)** - Overall testing approach

---

## Project Structure

### Core Documentation

```
docs/
├── PLANNING.md                    ← You are here
├── prd/                           ← Product Requirements
│   ├── index.md                   → Main PRD (with architecture link)
│   ├── goals-and-background-context.md
│   ├── requirements.md            → FR1-FR12, NFR1-NFR12
│   ├── epic-1-foundation-core-infrastructure.md
│   ├── epic-2-document-processing-pipeline.md
│   ├── epic-3-mcp-server-openwebui-integration.md
│   ├── epic-4-hybrid-retrieval-match-explanation.md
│   └── checklist-results-report.md → Validation results
│
├── architecture/                  ← Technical Architecture
│   ├── index.md                   → Main Architecture (with PRD link)
│   ├── tech-stack.md              → CRITICAL: Single source of truth
│   ├── components.md              → Service designs
│   ├── database-schema.md         → PostgreSQL schema
│   ├── core-workflows.md          → Sequence diagrams
│   └── coding-standards.md        → Mandatory development rules
│
├── epics/                         ← Epic Planning Artifacts
│   ├── README.md                  → Epic index
│   ├── epic-1.md                  → Foundation (7 stories)
│   ├── epic-2.md                  → Document Processing (7 stories)
│   ├── epic-3.md                  → MCP Integration (8 stories)
│   └── epic-4.md                  → Hybrid Retrieval (7 stories)
│
├── stories/                       ← User Story Cards
│   ├── README.md                  → All 29 stories indexed
│   ├── story-1.1.md through story-1.7.md
│   ├── story-2.1.md through story-2.7.md
│   ├── story-3.1.md through story-3.8.md
│   └── story-4.1.md through story-4.7.md
│
└── qa/                            ← Quality Assurance
    ├── assessments/               → Detailed test results per story
    │   ├── README.md
    │   └── assessment-template.md
    └── gates/                     → Go/no-go approval points
        ├── README.md
        └── gate-template.md
```

---

## Development Workflow

### 1. Sprint Planning
1. Review [Epic README](epics/README.md) to select next epic
2. Review epic's story list (e.g., [Epic 1](epics/epic-1.md))
3. Prioritize stories based on dependencies
4. Assign stories to developers

### 2. Story Development
1. Developer picks story (e.g., [Story 1.1](stories/story-1.1.md))
2. Review acceptance criteria and architecture references
3. Implement following [Coding Standards](architecture/coding-standards.md)
4. Self-test against acceptance criteria

### 3. QA Assessment
1. QA creates assessment using [template](qa/assessments/assessment-template.md)
2. Execute tests for all acceptance criteria
3. Document results, evidence, and issues
4. Complete assessment document

### 4. QA Gate
1. Gate reviewer evaluates using [template](qa/gates/gate-template.md)
2. Review assessment results
3. Verify architecture compliance
4. Decision: ✅ Approved | ⚠️ Conditional | ❌ Rejected

### 5. Story Completion
1. Update story status to "Complete"
2. Move to next story in epic
3. When epic complete, hold epic retrospective

---

## Project Phases

### ✅ Phase 0: Planning (Complete)
- PRD created and validated (87% readiness)
- Architecture document complete
- Epic and story artifacts generated
- QA process defined

### 🔄 Phase 1: Week 1 - Technical Spikes (Current)
**Critical validation before Epic 1:**
- OpenWebUI MCP integration method
- Apache AGE on WSL2 installation
- LightRAG PostgreSQL adapters
- Ollama connectivity from Docker

**Artifacts**: [Architecture Next Steps](architecture/next-steps.md)

### 📋 Phase 2: Weeks 2-3 - Epic 1
**Goal**: Foundation & Core Infrastructure

**Stories**: [Epic 1](epics/epic-1.md) (7 stories)

**Key Deliverables**:
- Docker Compose environment
- PostgreSQL with pgvector + Apache AGE
- LightRAG + Ollama integration
- Health check endpoint

### 📋 Phase 3: Weeks 4-6 - Epic 2
**Goal**: Document Processing Pipeline

**Stories**: [Epic 2](epics/epic-2.md) (7 stories)

**Key Deliverables**:
- Docling REST API
- CIGREF profile parsing
- 20-30 test CVs processed
- Knowledge base populated

### 📋 Phase 4: Weeks 7-9 - Epic 3
**Goal**: MCP Server & OpenWebUI Integration

**Stories**: [Epic 3](epics/epic-3.md) (8 stories)

**Key Deliverables**:
- MCP protocol server
- Search tools (profile, skill)
- OpenWebUI integration
- Natural language queries working

### 📋 Phase 5: Weeks 10-12 - Epic 4
**Goal**: Hybrid Retrieval & Match Explanation

**Stories**: [Epic 4](epics/epic-4.md) (7 stories)

**Key Deliverables**:
- Hybrid retrieval modes
- Graph-based ranking
- Match explanations
- User acceptance testing

---

## Key Metrics & Success Criteria

### Project Metrics
| Metric | Target | Current |
|--------|--------|---------|
| Total Stories | 29 | 29 created |
| Planning Readiness | 85%+ | 87% ✅ |
| Epic Count | 4 | 4 |
| Timeline | 10-12 weeks | On track |

### Quality Gates (NFRs from PRD)
| NFR | Target | Epic | Story |
|-----|--------|------|-------|
| NFR1: Query Response Time | <10s | Epic 4 | 4.6 |
| NFR2: CV Parsing Success | 90%+ | Epic 2 | 2.4 |
| NFR3: CIGREF Extraction | 85%+ | Epic 2 | 2.2 |
| NFR4: Match Precision@5 | 70%+ | Epic 4 | 4.7 |
| NFR9: Local-Only Processing | 100% | Epic 1 | 1.4 |
| NFR11: Timeline | 8-12 weeks | All | - |
| NFR12: Explainable Matches | Pass UAT | Epic 4 | 4.3, 4.4 |

---

## Risk Management

### High-Priority Risks (from Checklist)
1. **OpenWebUI MCP Integration** - Week 1 spike required
   - Mitigation: Validate early, have fallback options
   - Owner: Developer
   - Due: Week 1

2. **Test User Availability** - UAT requires 2-5 users
   - Mitigation: Recruit users NOW for Week 10-12
   - Owner: Product Manager
   - Due: Week 2

### Medium-Priority Risks
- Apache AGE maturity on WSL2
- qwen3:8b performance for <10s queries
- Recruiter user guide completeness

**Full risk analysis**: [Checklist Results Report](prd/checklist-results-report.md)

---

## Document Cross-References

### Requirements → Architecture
- [PRD Requirements](prd/requirements.md) ↔️ [Tech Stack](architecture/tech-stack.md)
- [PRD Technical Assumptions](prd/technical-assumptions.md) ↔️ [Infrastructure](architecture/infrastructure-and-deployment.md)
- [PRD Epic 1](prd/epic-1-foundation-core-infrastructure.md) ↔️ [Components](architecture/components.md)

### Epics → Stories → QA
- [Epic](epics/epic-1.md) → [Stories](stories/story-1.1.md) → [Assessment](qa/assessments/assessment-template.md) → [Gate](qa/gates/gate-template.md)

### Architecture → Implementation
- [Components](architecture/components.md) → Service source code
- [Database Schema](architecture/database-schema.md) → PostgreSQL init scripts
- [Coding Standards](architecture/coding-standards.md) → ALL code

---

## Quick Links

### 🔍 Research & Context
- [Goals and Background](prd/goals-and-background-context.md)
- [User Interface Design Goals](prd/user-interface-design-goals.md)
- [High Level Architecture](architecture/high-level-architecture.md)

### 🏗️ Implementation Details
- [Data Models](architecture/data-models.md)
- [Core Workflows](architecture/core-workflows.md)
- [External APIs (Ollama)](architecture/external-apis.md)
- [Error Handling Strategy](architecture/error-handling-strategy.md)

### 🔒 Non-Functional
- [Security](architecture/security.md)
- [Test Strategy](architecture/test-strategy.md)

### 📊 Status & Progress
- [Checklist Results Report](prd/checklist-results-report.md) - Initial validation
- [Epic Status](epics/README.md) - Current epic progress
- [Story Status](stories/README.md) - Individual story tracking

---

## Contact & Escalation

### Roles
- **Product Owner**: Sarah (PO Agent)
- **Architect**: Winston (Architect Agent)
- **Project Manager**: John (PM Agent)

### Escalation Path
1. **Story-level issues** → Developer + PO
2. **Epic-level blockers** → PO + Tech Lead
3. **Architecture changes** → Architect review required
4. **Timeline risks** → PM + Stakeholders

---

**Last Updated**: 2025-11-03
**Document Version**: v1.0
**Status**: ✅ Planning Complete, Ready for Development

---

*This planning hub provides comprehensive navigation across all project artifacts. For questions or updates, contact the Product Owner.*
