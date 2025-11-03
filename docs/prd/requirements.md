# Requirements

## Functional Requirements

**FR1:** The system shall parse and ingest the CIGREF IT profile nomenclature PDF (English 2024 edition), extracting structured data including domains, profiles, missions, activities, deliverables, performance indicators, and skills.

**FR2:** The system shall store CIGREF profile data in LightRAG with both vector embeddings and graph relationships representing the hierarchical and relational structure of competencies.

**FR3:** The system shall accept CV uploads in PDF and DOCX formats and process them using Docling with HybridChunker to extract skills, experience, education, and project information.

**FR4:** The system shall index processed CV content in LightRAG's knowledge base with vector embeddings and entity relationship graphs.

**FR5:** The system shall expose LightRAG-CV capabilities through a Model Context Protocol (MCP) server that integrates with OpenWebUI.

**FR6:** The system shall enable users to query the knowledge base using natural language through OpenWebUI (e.g., "Find candidates with 5+ years cloud architecture experience and Kubernetes expertise").

**FR7:** The system shall support multi-criteria search combining CIGREF profile matching, skill/technology filtering, experience level, and domain expertise.

**FR8:** The system shall leverage LightRAG's hybrid retrieval modes (naive, local, global, hybrid) with the MCP server intelligently selecting the appropriate mode based on query complexity.

**FR9:** The system shall provide match explanations for each candidate recommendation including:
- Aligned profile missions and activities
- Key skill matches (exact and semantically similar)
- Graph relationships influencing ranking
- Confidence scores and reasoning transparency

**FR10:** The system shall support conversational query refinement, allowing users to iteratively narrow or expand search criteria through follow-up natural language requests.

**FR11:** The system shall use external Ollama instance with qwen3:8b for generation, bge-m3 for embeddings (1024-dimensional), and bge-reranker-v2-m3 for reranking.

**FR12:** The system shall persist all data using PostgreSQL with pgvector and Apache AGE extensions, utilizing LightRAG's PGKVStorage, PGVectorStorage, PGGraphStorage, and PGDocStatusStorage adapters.

## Non-Functional Requirements

**NFR1:** The system shall return query responses within 10 seconds for typical natural language queries during POC (target <3 seconds for production).

**NFR2:** The system shall successfully parse and chunk 90%+ of CV formats (PDF, DOCX) without critical information loss.

**NFR3:** The system shall extract and store entities/relationships from 85%+ of CIGREF profile content.

**NFR4:** The system shall achieve 70% precision@5 for top-5 candidate rankings as validated by hiring manager review.

**NFR5:** The Docker Compose stack shall run stably for 48+ hours without crashes or memory issues.

**NFR6:** MCP tool invocations from OpenWebUI shall succeed with <5% error rate.

**NFR7:** The system shall deploy via Docker Compose on Windows WSL2/Docker Desktop with configurable ports via .env to avoid conflicts.

**NFR8:** The system shall support optional GPU acceleration for Docling service via Docker Compose profiles.

**NFR9:** All processing shall be performed locally without external cloud API calls to ensure CV data privacy.

**NFR10:** The system shall operate with English language content only for POC scope.

**NFR11:** The system shall function in a single-user environment without authentication requirements for POC.

**NFR12:** Match explanations shall render clearly in OpenWebUI chat interface and be comprehensible to non-technical recruiters.

---
