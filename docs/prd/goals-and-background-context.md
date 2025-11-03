# Goals and Background Context

## Goals

- Validate that hybrid vector-graph RAG technology (LightRAG) can meaningfully improve CV-to-profile matching accuracy and speed
- Demonstrate 40-60% reduction in manual screening time for IT recruitment
- Prove technical feasibility of Docling + LightRAG + PostgreSQL integration within 8-12 weeks
- Enable natural language conversational search for CV matching through OpenWebUI
- Establish baseline metrics for matching quality, retrieval performance, and explainability
- Create an intelligent knowledge base for matching IT professional CVs against CIGREF job profile nomenclature

## Background Context

HR professionals and technical recruiters face significant challenges matching IT candidates to standardized competency frameworks like CIGREF's IT profile nomenclature. Traditional keyword-based ATS systems miss nuanced relationships between skills, experiences, and job requirements, leading to time-consuming manual reviews and inconsistent evaluations. LightRAG-CV addresses this by combining Docling's intelligent document parsing with LightRAG's hybrid vector-graph retrieval architecture and PostgreSQL persistence, enabling sophisticated natural language queries through OpenWebUI via a Model Context Protocol (MCP) server.

This proof-of-concept validates whether the hybrid retrieval approach—which understands both semantic similarity and structural relationships between competencies—can deliver explainable, accurate candidate recommendations that reduce screening time while improving match quality. The system ingests both CIGREF profile documentation and candidate CVs, creating a unified knowledge base accessible through conversational interaction.

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2025-11-03 | v1.0 | Initial PRD created from Project Brief | John (PM Agent) |

---
