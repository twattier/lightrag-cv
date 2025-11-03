# Introduction

This document outlines the overall project architecture for **LightRAG-CV**, including backend systems, shared services, and infrastructure concerns. Its primary goal is to serve as the guiding architectural blueprint for AI-driven development, ensuring consistency and adherence to chosen patterns and technologies.

**Project Context:** LightRAG-CV is a proof-of-concept (POC) system that validates hybrid vector-graph RAG technology for intelligent CV-to-job-profile matching in IT recruitment. The system ingests CIGREF IT profile nomenclature and candidate CVs, creating a unified knowledge base accessible through natural language queries via OpenWebUI.

**Architectural Focus:** This document focuses on the backend microservices architecture, data storage, and integration patterns. Since the UI is provided by an external service (OpenWebUI), this architecture addresses service design, API contracts, database schemas, and deployment infrastructure running on Windows WSL2 with Docker Compose.

## Starter Template or Existing Project

**Analysis:** The PRD specifies a custom Docker Compose-based microservices architecture rather than a pre-existing starter template. Key architectural components are based on specific technologies:

- **LightRAG**: Using HKUDS/LightRAG library with custom PostgreSQL storage adapters
- **Docling**: IBM's document processing library wrapped in a REST service
- **MCP Server**: Custom implementation following Model Context Protocol specification
- **PostgreSQL**: Custom configuration with pgvector (0.5.0+) and Apache AGE extensions

**Decision:** **N/A - Greenfield project** with custom integration of multiple specialized libraries. The monorepo structure defined in the PRD will be implemented from scratch following Docker Compose best practices for microservices orchestration.

**Constraints:**
- Must use LightRAG's PostgreSQL storage adapters (PGKVStorage, PGVectorStorage, PGGraphStorage, PGDocStatusStorage)
- Docling service must support optional GPU acceleration via Docker Compose profiles
- MCP server implementation constrained by Model Context Protocol specification
- All services must communicate via internal Docker network with configurable ports

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2025-11-03 | v1.0 | Initial architecture document created from PRD v1.0 | Winston (Architect) |

---
