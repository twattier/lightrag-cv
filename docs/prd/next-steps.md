# Next Steps

> 📋 **Implementation readiness**: The architecture document is complete. See [Architecture Next Steps](../architecture/next-steps.md) for Week 1 actions and implementation timeline.

**PRD Handoff Context:** This section provides guidance for UX and Architecture experts who will refine requirements and create implementation plans.

## UX Expert Prompt

Given that this project uses OpenWebUI as the primary interface (a pre-existing chat-based UI), UX work is limited for this POC. However, if you have a UX expert available, here's the focused prompt:

> Review the LightRAG-CV PRD (docs/prd.md) focusing on the User Interface Design Goals section. Your scope is constrained since we're using OpenWebUI as the interface, but we need your expertise on:
>
> 1. **Result Formatting Design**: How should candidate match results and explanations render in a chat interface? Design markdown templates that balance information density with readability.
>
> 2. **Conversational Flow Patterns**: Review Epic 3 stories on conversational refinement. Recommend best practices for multi-turn recruitment searches (when to summarize previous context, how to handle contradictory refinements).
>
> 3. **Explainability UX**: Review Epic 4 match explanation requirements. Design the structure for graph-based explanations that non-technical recruiters can understand and trust.
>
> 4. **OpenWebUI Configuration**: Document any OpenWebUI theme/configuration recommendations for recruitment workflows (contrast, typography for dense CV data, collapsible sections).
>
> 5. **User Testing Protocol**: Design the UAT protocol for Epic 4, Story 4.7 (test scenarios, survey questions, success criteria evaluation).
>
> **Deliverable**: UX guidelines document covering result formatting, explanation rendering, and UAT protocol. No wireframes or full design system needed for POC—focus on making chat-based interaction effective for recruitment use cases.

## Architect Prompt

> I've completed the Product Requirements Document for LightRAG-CV, a proof-of-concept system for intelligent CV-to-job-profile matching using hybrid vector-graph retrieval. The PRD is available at `docs/prd.md` and includes:
>
> - **Goals & Context**: POC validating LightRAG + Docling + PostgreSQL for recruitment matching
> - **Requirements**: 12 functional requirements (FR1-FR12) and 12 non-functional requirements (NFR1-NFR12)
> - **Technical Assumptions**: Detailed tech stack (Docker Compose, PostgreSQL with pgvector+AGE, LightRAG, Docling, MCP server, OpenWebUI, external Ollama)
> - **4 Epics with 28 Stories**: Infrastructure → Document Processing → MCP/OpenWebUI Integration → Hybrid Retrieval & Explanations
>
> **Your Task**: Create the Architecture Document (docs/architecture.md) that provides technical implementation guidance for development. Focus on:
>
> 1. **Service Architecture**: Detail the microservices design (Docling, LightRAG, MCP Server, PostgreSQL), Docker Compose networking, and inter-service communication patterns.
>
> 2. **Data Architecture**: Design PostgreSQL schema for LightRAG's storage adapters (PGKVStorage, PGVectorStorage, PGGraphStorage, PGDocStatusStorage). Document vector embedding strategy and graph entity/relationship model.
>
> 3. **MCP Server Design**: Architect the Model Context Protocol server—tool definitions, LightRAG API integration layer, response formatting, error handling.
>
> 4. **Document Processing Pipeline**: Design Docling service API, chunking strategy for CIGREF profiles and CVs, entity extraction approach, and LightRAG ingestion workflow.
>
> 5. **Retrieval Strategy**: Architect the hybrid retrieval mode selection logic, graph relationship scoring algorithm, and confidence scoring implementation (Epic 4 requirements).
>
> 6. **Critical Technical Decisions**: Address the Week 1 technical spikes:
>    - OpenWebUI MCP integration approach (transport layer, tool discovery)
>    - Apache AGE setup and graph query patterns
>    - LightRAG PostgreSQL adapter validation
>    - qwen3:8b query parsing strategy
>
> 7. **Performance & Scalability**: Design for <10s query response (POC target) with optimization paths for <3s (production target).
>
> 8. **Development Environment**: Detail setup procedures, configuration management (.env), local testing approaches, and Docker Compose profiles (CPU vs. GPU).
>
> **Key Constraints from PRD**:
> - Windows WSL2 + Docker Desktop deployment
> - Local-only processing (no cloud APIs)
> - Single-user POC (no auth required)
> - English-only content
> - Manual testing (no automated test infrastructure for POC)
> - 8-12 week timeline
>
> **Deliverables**:
> - Complete architecture document (docs/architecture.md) following BMAD architecture template
> - Service architecture diagrams (containers, data flow, deployment)
> - Database schema and entity-relationship diagrams
> - MCP tool specifications (tool names, parameters, response schemas)
> - API contracts (Docling REST API, LightRAG API usage patterns)
> - Technical risk mitigation strategies for identified risks
>
> Please review the PRD thoroughly and create an architecture that enables the development team to implement all 28 stories across 4 epics successfully. The architecture should be detailed enough for developers to begin Epic 1 (Foundation & Core Infrastructure) immediately after your review.

---

*Document version: v1.0*
*Generated by: PM Agent - John*
*Date: 2025-11-03*
