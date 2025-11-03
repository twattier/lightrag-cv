# LightRAG-CV Product Requirements Document (PRD)

---

## Goals and Background Context

### Goals

- Validate that hybrid vector-graph RAG technology (LightRAG) can meaningfully improve CV-to-profile matching accuracy and speed
- Demonstrate 40-60% reduction in manual screening time for IT recruitment
- Prove technical feasibility of Docling + LightRAG + PostgreSQL integration within 8-12 weeks
- Enable natural language conversational search for CV matching through OpenWebUI
- Establish baseline metrics for matching quality, retrieval performance, and explainability
- Create an intelligent knowledge base for matching IT professional CVs against CIGREF job profile nomenclature

### Background Context

HR professionals and technical recruiters face significant challenges matching IT candidates to standardized competency frameworks like CIGREF's IT profile nomenclature. Traditional keyword-based ATS systems miss nuanced relationships between skills, experiences, and job requirements, leading to time-consuming manual reviews and inconsistent evaluations. LightRAG-CV addresses this by combining Docling's intelligent document parsing with LightRAG's hybrid vector-graph retrieval architecture and PostgreSQL persistence, enabling sophisticated natural language queries through OpenWebUI via a Model Context Protocol (MCP) server.

This proof-of-concept validates whether the hybrid retrieval approach—which understands both semantic similarity and structural relationships between competencies—can deliver explainable, accurate candidate recommendations that reduce screening time while improving match quality. The system ingests both CIGREF profile documentation and candidate CVs, creating a unified knowledge base accessible through conversational interaction.

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2025-11-03 | v1.0 | Initial PRD created from Project Brief | John (PM Agent) |

---

## Requirements

### Functional Requirements

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

### Non-Functional Requirements

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

## User Interface Design Goals

### Overall UX Vision

The user experience centers on **conversational, natural language interaction** that feels like consulting with an intelligent assistant rather than operating a traditional search interface. Recruiters should be able to express complex, multi-criteria requirements in plain English without learning query syntax or navigating complex filter menus. The system prioritizes **transparency and explainability**—every recommendation should come with clear reasoning that helps recruiters understand and trust the results. The interface should support iterative refinement, allowing users to naturally narrow or expand searches through follow-up questions, mimicking how they would work with a human research assistant.

### Key Interaction Paradigms

- **Conversational Query**: Users type natural language questions in a chat interface (e.g., "Show me senior DevOps engineers with AWS and Terraform experience")
- **Iterative Refinement**: Follow-up queries that modify previous searches (e.g., "Now show only candidates with leadership experience")
- **Explainable Results**: Each candidate recommendation displays as a rich card or message showing match reasoning, graph relationships, and skill alignments
- **Contextual Clarification**: System can ask clarifying questions when queries are ambiguous (e.g., "By 'cloud experience' do you mean AWS, Azure, GCP, or any cloud platform?")
- **Progressive Disclosure**: Initial results show summary information with expandable details for deeper exploration of candidate-profile alignments

### Core Screens and Views

Since this is an OpenWebUI-based solution, the interface is primarily chat-driven:

- **Chat Interface**: Primary view where all queries are entered and results are displayed
- **Candidate Detail View**: Expanded view showing full CV content, all matched CIGREF missions/activities, graph relationship visualizations, and confidence scores
- **Match Explanation Panel**: Structured breakdown of why a candidate was recommended, including skill overlaps, experience alignment, and graph-based insights
- **Query History**: Sidebar or panel showing previous searches for easy recall and refinement

### Accessibility

**WCAG AA compliance** through OpenWebUI's existing accessibility features. No custom accessibility work required for POC—leverage OpenWebUI's built-in support for screen readers, keyboard navigation, and contrast standards.

**Assumption**: OpenWebUI already meets basic accessibility requirements. If specific recruitment workflows require enhanced accessibility (e.g., high-volume screen reader use), this would be addressed in Phase 2.

### Branding

**Minimal branding requirements for POC**. Use OpenWebUI's default theme with potential minor customization:
- Clean, professional aesthetic appropriate for HR/recruitment workflows
- Clear visual hierarchy distinguishing system messages from candidate results
- Readable typography for dense information (CV content, competency descriptions)

**Assumption**: No corporate branding requirements exist for POC. If production deployment requires specific brand alignment, this would be configured in OpenWebUI's theming system during Phase 2.

### Target Device and Platforms

**Web Responsive (Desktop-Primary)**

Primary use case is desktop/laptop usage by recruiters at their workstations during candidate screening workflows. The OpenWebUI interface should be:
- Optimized for desktop browsers (Chrome, Edge, Firefox)
- Functional on tablets (iPad) for managers reviewing shortlists on the go
- Mobile-accessible but not optimized (basic chat functionality works, but dense candidate information may be cramped)

**Assumption**: Recruiters primarily work at desks with large screens when conducting detailed candidate evaluation. Mobile access is secondary for Phase 2 consideration.

---

## Technical Assumptions

### Repository Structure: Monorepo

**Decision**: Single repository containing all services (Docling, LightRAG, MCP Server, PostgreSQL configuration), documentation, and deployment artifacts.

**Rationale**: POC scope benefits from simplified coordination and versioning. All components are tightly coupled for this specific use case, making a monorepo more efficient for rapid iteration. The brief's repository structure diagram shows all services under a single `lightrag-cv/` root.

**Structure**:
```
lightrag-cv/
├── docker-compose.yml
├── .env.example
├── services/
│   ├── docling/          # Docling service container
│   ├── lightrag/         # LightRAG server config
│   ├── mcp-server/       # MCP server implementation
│   └── postgres/         # PostgreSQL configuration
├── data/
│   ├── cigref/           # CIGREF reference PDF
│   └── cvs/              # Test CV files
├── docs/                 # Documentation
└── scripts/              # Setup and utility scripts
```

### Service Architecture

**Microservices architecture within containerized environment**

**Core Services**:
- **Docling Service**: Standalone Python service exposing REST API for document processing with optional GPU acceleration
- **LightRAG Server**: Python-based RAG engine from HKUDS/LightRAG with API support
- **MCP Server**: Protocol server (Python or TypeScript) exposing LightRAG-CV tools to OpenWebUI
- **PostgreSQL Database**: Unified persistence with pgvector (0.5.0+) and Apache AGE extensions

**External Dependencies**:
- **Ollama**: External LLM inference server (host or separate container) providing:
  - `qwen3:8b` for generation
  - `bge-m3:latest` for embeddings (1024-dimensional)
  - `xitao/bge-reranker-v2-m3` for reranking
- **OpenWebUI**: External service providing user interface

**Communication Flow**:
1. User queries OpenWebUI in natural language
2. OpenWebUI invokes MCP Server tools via MCP protocol
3. MCP Server translates to LightRAG API calls
4. LightRAG queries PostgreSQL (vectors + graphs) and generates response via Ollama
5. MCP Server formats results and returns to OpenWebUI
6. OpenWebUI renders conversational response with candidate recommendations

**Container Orchestration**: Docker Compose with internal networking, configurable ports via .env, and named volumes for PostgreSQL persistence.

### Testing Requirements

**POC-appropriate testing strategy**:

- **Manual Testing Primary**: Manual evaluation of 20 natural language test queries with recruiter/hiring manager validation
- **Integration Testing**: End-to-end workflow testing (CV upload → processing → query → results) to validate MCP-OpenWebUI-LightRAG integration
- **Data Quality Validation**: Manual inspection of parsed CIGREF content and sample CVs to verify extraction accuracy
- **Performance Baseline**: Manual timing of query response times (target <10s for POC)
- **Stability Testing**: 48+ hour run test to validate container stability

**No automated test harness for MVP**—focus on working functionality over test infrastructure. Phase 2 would add:
- Unit tests for MCP server tool logic
- Integration tests for LightRAG PostgreSQL storage
- Automated query quality metrics

**Rationale**: POC timeline (8-12 weeks) and single-developer assumption make automated testing infrastructure a poor ROI. Manual validation with test users provides sufficient quality signal for go/no-go decision.

### Additional Technical Assumptions and Requests

#### Programming Languages & Frameworks

- **MCP Server**: Python (using `mcp` library) OR TypeScript (using `@modelcontextprotocol/sdk`)
  - **Preference**: Python for consistency with LightRAG and Docling ecosystems
  - **Decision point**: Confirm OpenWebUI MCP transport compatibility (stdio vs SSE) during Week 1 spike

- **LightRAG Integration**: Python client for LightRAG REST API (documented in `lightrag/api/README.md`)

- **Docling Service**: Python service wrapping Docling library with REST endpoints

#### Database Configuration

- **PostgreSQL 16+** with required extensions:
  - `pgvector` 0.5.0+ for vector similarity search
  - `Apache AGE` for graph database capabilities

- **LightRAG Storage Adapters**: Use PostgreSQL-based storage implementations:
  - `PGKVStorage` (key-value store)
  - `PGVectorStorage` (embeddings)
  - `PGGraphStorage` (entity relationships)
  - `PGDocStatusStorage` (document tracking)

- **Connection Management**: Direct connections for POC; consider pgBouncer for Phase 2 if concurrent load requires pooling

#### Deployment & Infrastructure

- **Target Platform**: Docker Desktop on Windows WSL2 (Ubuntu or compatible distro)
- **Container Runtime**: Docker Compose v2.x
- **GPU Support**: Optional NVIDIA GPU acceleration via Docker Compose profiles (requires nvidia-docker runtime)
  ```bash
  # Run with GPU
  docker compose --profile gpu up

  # Run CPU-only
  docker compose up
  ```

- **Port Configuration**: All ports configurable via .env to avoid conflicts:
  ```env
  MCP_SERVER_PORT=3000
  LIGHTRAG_API_PORT=9621
  DOCLING_API_PORT=8000
  POSTGRES_PORT=5432
  ```

- **Networking**: Single Docker network for inter-service communication; only MCP server port exposed to host

- **Volumes**:
  - Named volumes for PostgreSQL data persistence
  - Bind mounts for configuration files and data directories

#### Security & Privacy

- **Local-Only Processing**: All LLM inference, embedding generation, and data processing performed locally—no cloud API calls (critical for CV PII handling)
- **Network Isolation**: Services communicate via internal Docker network
- **Credential Management**: Database passwords and API keys in `.env` file (NOT committed to repo; use `.env.example` template)
- **No Authentication for POC**: Single-user assumption; authentication deferred to Phase 2 via OpenWebUI's existing auth

#### Data Processing

- **Document Formats Supported**: PDF and DOCX for CVs; PDF for CIGREF reference
- **Chunking Strategy**: Docling HybridChunker for intelligent content segmentation
- **Embedding Dimensionality**: 1024-dimensional vectors (bge-m3)
- **Graph Entity Types**: Skills, experiences, certifications, CIGREF missions, activities, deliverables, performance indicators
- **Language Support**: English only for POC

#### LLM Configuration

- **Context Window**: `OLLAMA_LLM_NUM_CTX=40960` (40K tokens for qwen3:8b)
- **Model Quantization**: Use default Ollama quantization (likely Q4_K_M for 8B models)
- **Inference Mode**: External Ollama service accessed via `http://host.docker.internal:11434`
- **Reranking**: bge-reranker-v2-m3 for result reranking to improve top-k precision

#### MCP Protocol

- **Protocol Version**: Latest stable MCP specification from modelcontextprotocol.io
- **Transport**: TBD based on OpenWebUI compatibility testing (Week 1 spike)—likely stdio or SSE
- **Tool Discovery**: MCP server must implement tool discovery for OpenWebUI to enumerate available capabilities
- **Resource Serving**: Structured match explanations exposed as MCP resources

#### Logging & Observability

- **POC Logging**: Docker Compose logs (`docker compose logs -f`) sufficient for debugging
- **Error Handling**: Basic error messages returned via MCP protocol; no centralized logging infrastructure
- **Monitoring**: Manual observation during test sessions; no metrics dashboard for POC
- **Phase 2**: Would add structured logging (ELK stack or similar), metrics (Prometheus/Grafana), and distributed tracing

#### Performance Considerations

- **Query Timeout**: 10 second target for POC (acceptable for validation; production target <3s)
- **Batch Processing**: One CV at a time for POC; no batch ingestion pipeline
- **Index Updates**: Assume full knowledge base rebuild for POC; incremental updates deferred to Phase 2
- **Concurrent Users**: Single user for POC; architecture should support 5-10 concurrent for Phase 2

#### Development Workflow

- **Environment Setup**: Scripted setup via `scripts/setup.sh` or similar
- **Configuration Management**: `.env` file for all configurable parameters with `.env.example` template
- **Documentation**: Focus on setup instructions, architecture overview, and usage examples—minimal API documentation for POC
- **Version Control**: Git repository with standard `.gitignore` (exclude `.env`, data files, PostgreSQL volumes)

---

## Epic List

**Epic 1: Foundation & Core Infrastructure**
**Goal**: Establish containerized development environment with PostgreSQL storage, basic LightRAG integration, and project scaffolding that enables subsequent feature development while delivering a working health-check endpoint.

**Epic 2: Document Processing Pipeline**
**Goal**: Implement Docling service integration for parsing CIGREF profiles and CVs, with validated extraction quality and successful ingestion into LightRAG knowledge base.

**Epic 3: MCP Server & OpenWebUI Integration**
**Goal**: Build Model Context Protocol server exposing core search tools, integrate with OpenWebUI, and enable end-to-end natural language querying of the knowledge base.

**Epic 4: Hybrid Retrieval & Match Explanation**
**Goal**: Implement intelligent retrieval mode selection, candidate ranking with graph-based insights, and structured match explanations that render clearly in OpenWebUI.

---

## Epic 1: Foundation & Core Infrastructure

**Epic Goal**: Establish containerized development environment with PostgreSQL storage (pgvector + Apache AGE), basic LightRAG integration, Ollama connectivity validation, and project scaffolding that enables subsequent feature development while delivering a working health-check endpoint to verify all services are operational.

### Story 1.1: Project Repository Setup and Docker Compose Scaffold

**As a** developer,
**I want** a structured repository with Docker Compose configuration scaffolding,
**so that** I have a foundation for organizing services and can begin local development.

#### Acceptance Criteria

1. Repository structure created matching the architecture specification:
   - `/services/docling/`, `/services/lightrag/`, `/services/mcp-server/`, `/services/postgres/`
   - `/data/cigref/`, `/data/cvs/`
   - `/docs/`, `/scripts/`
   - Root-level `docker-compose.yml`, `.env.example`, `.gitignore`, `README.md`

2. `.env.example` template includes all required configuration variables:
   - LLM configuration (Ollama binding, model names, context size)
   - Embedding configuration (model, dimensions)
   - Reranking configuration
   - PostgreSQL connection details
   - Service ports (MCP, LightRAG, Docling, PostgreSQL)

3. `.gitignore` properly excludes `.env`, data files, PostgreSQL volumes, Python `__pycache__`, and other generated artifacts

4. `README.md` includes setup instructions for copying `.env.example` to `.env` and basic Docker Compose usage

5. `docker-compose.yml` scaffold created with service definitions (empty/placeholder initially) for: `postgres`, `lightrag`, `docling`, `mcp-server`

### Story 1.2: PostgreSQL with pgvector and Apache AGE Setup

**As a** developer,
**I want** PostgreSQL 16+ running in Docker with pgvector and Apache AGE extensions installed,
**so that** LightRAG can store vectors and graphs in a unified database.

#### Acceptance Criteria

1. PostgreSQL 16+ service defined in `docker-compose.yml` with:
   - Named volume for data persistence (`postgres_data`)
   - Port mapping configurable via `.env` (default 5432)
   - Health check configured to verify database readiness

2. Custom Dockerfile or init scripts in `/services/postgres/` that:
   - Install `pgvector` extension (0.5.0+)
   - Install `Apache AGE` extension
   - Create `lightrag_cv` database
   - Enable both extensions on the database

3. PostgreSQL service starts successfully with `docker compose up postgres`

4. Can connect to PostgreSQL from host using credentials from `.env` and verify extensions:
   ```sql
   \dx  -- Shows pgvector and age extensions
   SELECT extname, extversion FROM pg_extension;
   ```

5. PostgreSQL service persists data across container restarts (data volume working correctly)

### Story 1.3: LightRAG Server Integration with PostgreSQL Storage

**As a** developer,
**I want** LightRAG server running with PostgreSQL storage adapters configured,
**so that** I can ingest documents and perform basic retrieval operations.

#### Acceptance Criteria

1. LightRAG service defined in `docker-compose.yml` with:
   - Python runtime environment
   - Dependencies installed (LightRAG from HKUDS/LightRAG, PostgreSQL drivers)
   - Port mapping for REST API (configurable via `.env`, default 9621)
   - Environment variables for PostgreSQL connection and Ollama endpoints
   - Depends on `postgres` service

2. LightRAG configured to use PostgreSQL storage adapters:
   - `PGKVStorage` for key-value store
   - `PGVectorStorage` for embeddings
   - `PGGraphStorage` for graph relationships
   - `PGDocStatusStorage` for document tracking

3. LightRAG service starts successfully and connects to PostgreSQL (no connection errors in logs)

4. LightRAG REST API is accessible from host at configured port

5. Basic health check endpoint returns success status indicating LightRAG is operational

### Story 1.4: Ollama Integration Validation

**As a** developer,
**I want** to validate connectivity to external Ollama service with required models,
**so that** I confirm LLM generation, embeddings, and reranking will work for subsequent epics.

#### Acceptance Criteria

1. Documentation in `README.md` or `/docs/setup.md` instructs users to:
   - Install Ollama on host or separate container
   - Pull required models: `qwen3:8b`, `bge-m3:latest`, `xitao/bge-reranker-v2-m3`
   - Verify Ollama is accessible at `http://host.docker.internal:11434` from containers

2. Simple validation script or manual test procedure that:
   - Calls Ollama API to generate text with `qwen3:8b`
   - Calls Ollama API to generate embeddings with `bge-m3` (verify 1024 dimensions)
   - Confirms models are loaded and responding

3. LightRAG service configuration includes Ollama endpoints:
   - `LLM_BINDING_HOST=http://host.docker.internal:11434`
   - `EMBEDDING_BINDING_HOST=http://host.docker.internal:11434`
   - `RERANK_BINDING_HOST=http://host.docker.internal:11434`

4. LightRAG can successfully call Ollama for test generation and embedding (verified via logs or test request)

5. Documentation notes expected response times and model loading behavior (first request may be slow)

### Story 1.5: Docling Service Scaffold with GPU Profile Support

**As a** developer,
**I want** Docling service defined in Docker Compose with optional GPU acceleration profile,
**so that** subsequent epics can integrate document parsing with flexible performance options.

#### Acceptance Criteria

1. Docling service defined in `docker-compose.yml` with:
   - Python runtime environment
   - Docling library dependencies installed
   - Port mapping for REST API (configurable via `.env`, default 8000)
   - CPU-only configuration as default

2. Docker Compose GPU profile defined that:
   - Adds NVIDIA GPU runtime configuration to Docling service
   - Can be activated with `docker compose --profile gpu up`
   - Includes documentation in `README.md` about GPU requirements (nvidia-docker runtime)

3. Docling service starts successfully in CPU-only mode with `docker compose up docling`

4. If GPU available, Docling service starts successfully with `docker compose --profile gpu up docling`

5. Basic health check endpoint on Docling service returns success status

6. Documentation includes note that GPU acceleration is optional and CPU fallback is fully functional

### Story 1.6: Infrastructure Health Check Endpoint

**As a** developer or operator,
**I want** a consolidated health check endpoint that reports status of all services,
**so that** I can quickly verify the entire stack is operational.

#### Acceptance Criteria

1. Simple health check script or minimal web endpoint (can be part of MCP server scaffold or standalone) that:
   - Checks PostgreSQL connectivity and extension availability
   - Checks LightRAG API responsiveness
   - Checks Docling API responsiveness
   - Checks Ollama connectivity
   - Returns JSON status report with each service's health

2. Health check accessible via HTTP request (e.g., `http://localhost:3000/health`) or via script execution

3. Health check returns success when all services are up and returns partial status with error details when services are down

4. Documentation in `README.md` includes instructions for running health check to verify setup

5. Health check validates that PostgreSQL extensions (pgvector, AGE) are properly installed

### Story 1.7: Development Setup Documentation and Scripts

**As a** developer,
**I want** clear setup documentation and automated setup scripts,
**so that** I can quickly provision the development environment on Windows WSL2.

#### Acceptance Criteria

1. `/docs/setup.md` or expanded `README.md` includes:
   - Prerequisites (Docker Desktop, WSL2, minimum RAM/disk, optional GPU requirements)
   - Step-by-step setup instructions (clone repo, copy `.env.example`, configure `.env`, start services)
   - Troubleshooting section for common issues (port conflicts, PostgreSQL extension errors, Ollama connectivity)
   - Architecture diagram showing service relationships

2. Optional setup script `/scripts/setup.sh` that:
   - Checks prerequisites (Docker, Docker Compose versions)
   - Prompts for `.env` configuration or copies `.env.example` to `.env`
   - Validates required Ollama models are pulled
   - Runs initial `docker compose up` or validation

3. Documentation includes instructions for:
   - Starting all services: `docker compose up -d`
   - Starting with GPU: `docker compose --profile gpu up -d`
   - Viewing logs: `docker compose logs -f [service]`
   - Stopping services: `docker compose down`
   - Resetting database: `docker compose down -v` (removes volumes)

4. Documentation includes expected startup time and first-run behavior (Ollama model loading, PostgreSQL initialization)

5. Quick-start section gets a developer from zero to health check passing in under 15 minutes (assuming prerequisites installed)

---

## Epic 2: Document Processing Pipeline

**Epic Goal**: Implement Docling service REST API for parsing CIGREF profiles and CVs, validate extraction quality on test documents, integrate with LightRAG for knowledge base ingestion, and successfully load the CIGREF English 2024 nomenclature plus a test set of 20-30 IT CVs with verified content quality.

### Story 2.1: Docling REST API Implementation

**As a** developer,
**I want** Docling service exposing REST endpoints for document parsing,
**so that** other services can submit PDFs/DOCX files and receive structured parsed content.

#### Acceptance Criteria

1. Docling service implements REST API with endpoints:
   - `POST /parse` - accepts multipart file upload (PDF or DOCX), returns parsed JSON
   - `GET /health` - returns service health status
   - `GET /status/{job_id}` - optional async processing status (if needed for large docs)

2. `/parse` endpoint uses Docling's `HybridChunker` for intelligent content segmentation

3. Response format includes:
   - Parsed text content organized by document structure (sections, paragraphs)
   - Metadata (document type, page count, processing time)
   - Extracted entities if available (tables, lists, headings)
   - Chunk boundaries and metadata for downstream embedding

4. Error handling returns appropriate HTTP status codes:
   - 400 for invalid file format
   - 413 for file too large
   - 500 for parsing failures with error details

5. Service handles both CPU and GPU modes based on Docker Compose profile (GPU accelerates processing, CPU is functional fallback)

6. API documentation added to `/docs/docling-api.md` with example requests/responses

### Story 2.2: CIGREF English PDF Parsing and Quality Validation

**As a** product manager,
**I want** the CIGREF IT profile nomenclature PDF parsed with validated extraction quality,
**so that** I can confirm structured profile data (missions, skills, deliverables) is accurately captured.

#### Acceptance Criteria

1. CIGREF English 2024 edition PDF downloaded and placed in `/data/cigref/` directory

2. Test script or manual process submits CIGREF PDF to Docling `/parse` endpoint

3. Parsed output is manually inspected and validated for:
   - All IT profile domains identified (e.g., Business, Development, Production, Support)
   - Individual profiles extracted (e.g., Cloud Architect, DevOps Engineer, Data Scientist)
   - Structured sections recognized: Missions, Activities, Deliverables, Performance Indicators, Skills
   - Tables and lists properly parsed (not mangled)
   - French/English mixed content handled appropriately (English edition focus)

4. Quality validation results documented in `/docs/cigref-parsing-validation.md`:
   - Sample profile showing successful extraction
   - Known issues or limitations
   - Assessment: "Meets 85%+ extraction quality threshold" (NFR3) or notes gaps

5. If quality is below threshold, document remediation approach (manual pre-processing, Docling parameter tuning, or supplemental manual data entry)

6. Parsed CIGREF content saved to `/data/cigref/cigref-parsed.json` or similar format for LightRAG ingestion

### Story 2.3: CV Dataset Acquisition and Preprocessing

**As a** developer,
**I want** a curated test set of 20-30 English IT resumes from Hugging Face datasets,
**so that** I have representative data for knowledge base population and testing.

#### Acceptance Criteria

1. Download and sample CVs from specified Hugging Face datasets:
   - `gigswar/cv_files`
   - `d4rk3r/resumes-raw-pdf`

2. Filter for English language IT/technical resumes (software, infrastructure, data, security roles)

3. Curate final test set of 20-30 CVs with diverse characteristics:
   - Multiple experience levels (junior, mid, senior)
   - Various IT domains (development, infrastructure, data, security, management)
   - Different formats (PDF, DOCX if available)
   - Different lengths (1-3 pages typical)

4. CVs organized in `/data/cvs/test-set/` with basic metadata file (`cvs-manifest.json`) listing:
   - Filename
   - Inferred role/domain (manual tagging)
   - Experience level estimate
   - File format

5. Sample of 3-5 CVs manually reviewed for quality and relevance (not gibberish, contains actual technical content)

6. Documentation in `/docs/test-data.md` describes dataset composition and filtering criteria

### Story 2.4: CV Parsing and Quality Validation

**As a** product manager,
**I want** test CVs parsed through Docling with validated extraction quality,
**so that** I can confirm critical resume information (skills, experience, education) is accurately captured.

#### Acceptance Criteria

1. Test script processes all CVs in `/data/cvs/test-set/` through Docling `/parse` endpoint

2. Parsed CV outputs saved to `/data/cvs/parsed/` directory (one JSON per CV)

3. Sample of 5 CVs manually inspected for extraction quality:
   - Skills/technologies identified (e.g., "Python", "Kubernetes", "AWS")
   - Work experience sections recognized (companies, roles, dates, descriptions)
   - Education extracted
   - Projects/accomplishments captured
   - Contact info and personal data handled appropriately

4. Quality metrics documented in `/docs/cv-parsing-validation.md`:
   - Percentage of CVs successfully parsed (target: 90%+ per NFR2)
   - Common extraction issues (e.g., multi-column layouts, graphics-heavy resumes)
   - Assessment of readiness for LightRAG ingestion

5. If quality below threshold (90%), document mitigation:
   - Remove problematic CVs from test set
   - Adjust Docling parameters
   - Note as limitation in POC findings

6. Validated parsed CVs ready for LightRAG ingestion (Story 2.5)

### Story 2.5: LightRAG Knowledge Base Ingestion - CIGREF Profiles

**As a** developer,
**I want** parsed CIGREF profile data ingested into LightRAG with vector embeddings and graph relationships,
**so that** the system understands IT profile structure and competencies.

#### Acceptance Criteria

1. Ingestion script or process that:
   - Reads parsed CIGREF data (`/data/cigref/cigref-parsed.json`)
   - Submits to LightRAG API for document ingestion
   - Handles chunking if CIGREF content exceeds context limits
   - Waits for embedding generation completion

2. LightRAG successfully generates:
   - Vector embeddings for CIGREF content chunks (stored in PGVectorStorage)
   - Knowledge graph entities (profiles, missions, skills, deliverables, domains)
   - Relationships between entities (e.g., "Cloud Architect" → "requires" → "AWS expertise")

3. PostgreSQL validation queries confirm data storage:
   ```sql
   -- Check vector storage
   SELECT COUNT(*) FROM [vector_table];

   -- Check graph storage (AGE)
   SELECT * FROM cypher('[graph_name]', $$
     MATCH (n) RETURN n LIMIT 10
   $$) as (n agtype);
   ```

4. Graph coverage assessed: Can manually identify at least 5 profiles, 10 skills, 5 missions in stored graph

5. Simple LightRAG query test (via API or CLI):
   - Query: "What are the skills required for Cloud Architect?"
   - Response includes relevant CIGREF profile information
   - Demonstrates retrieval is working

6. Ingestion process documented in `/docs/ingestion-process.md` with runtime metrics (time taken, number of entities created)

### Story 2.6: LightRAG Knowledge Base Ingestion - CVs

**As a** developer,
**I want** parsed test CVs ingested into LightRAG alongside CIGREF profiles,
**so that** the unified knowledge base contains both profile references and candidate data.

#### Acceptance Criteria

1. Batch ingestion script processes all validated parsed CVs from `/data/cvs/parsed/`

2. Each CV ingested with metadata tagging:
   - Filename/ID
   - Document type: "CV"
   - Any manual tags from `cvs-manifest.json` (role, experience level)

3. LightRAG generates embeddings and extracts entities from CVs:
   - Skills mentioned
   - Companies/employers
   - Technologies used
   - Roles/titles held
   - Education and certifications

4. Graph relationships created linking CV entities to CIGREF entities where applicable (e.g., CV mentions "Kubernetes" → links to "container orchestration" competency)

5. PostgreSQL validation confirms CV data persisted:
   - Vector count increased by expected amount
   - Graph contains CV-specific entities (can query for candidate skills)

6. Test query validates CV retrieval:
   - Query: "Find candidates with Python experience"
   - Response returns relevant CVs that mention Python
   - Demonstrates CV content is searchable

7. Ingestion metrics documented: Total CVs ingested, processing time, entity count, any failed ingestions

### Story 2.7: Document Processing Performance Baseline

**As a** product manager,
**I want** baseline performance metrics for document processing,
**so that** I can assess whether throughput meets POC requirements and understand GPU acceleration impact.

#### Acceptance Criteria

1. Performance test measures:
   - Docling parsing time per CV (average, min, max) in CPU-only mode
   - Docling parsing time per CV with GPU acceleration (if available)
   - LightRAG ingestion time per document (parsing → embedding → storage)
   - End-to-end time: Upload CV → Available for search

2. Test conducted on sample of 10 CVs with varied characteristics (1-page, 2-page, 3-page resumes)

3. Results documented in `/docs/performance-baseline.md`:
   - CPU-only throughput: X CVs per minute
   - GPU-accelerated throughput: Y CVs per minute (if tested)
   - LightRAG embedding generation time
   - Total pipeline throughput assessment

4. Comparison to requirements:
   - Target: 1-2 CVs per minute acceptable for POC
   - Assessment: "Meets/Exceeds/Below expectations"

5. If performance below expectations, document mitigation strategies for Phase 2 (batch processing, queue system, model optimization)

6. Recommendations for production optimization noted (e.g., "GPU acceleration provides 3x improvement, recommended for scale")

---

## Epic 3: MCP Server & OpenWebUI Integration

**Epic Goal**: Build Model Context Protocol (MCP) server exposing core LightRAG-CV tools, configure OpenWebUI to discover and invoke MCP tools, enable end-to-end natural language querying from chat interface to candidate results, and validate conversational refinement capabilities.

### Story 3.1: MCP Server Scaffold and Protocol Implementation

**As a** developer,
**I want** MCP server skeleton implementing the Model Context Protocol specification,
**so that** I can expose tools and resources to MCP-compatible clients like OpenWebUI.

#### Acceptance Criteria

1. MCP server implementation created in `/services/mcp-server/` using:
   - Python with `mcp` library, OR
   - TypeScript with `@modelcontextprotocol/sdk`
   - Decision based on OpenWebUI compatibility testing (Week 1 technical spike findings)

2. MCP server implements protocol fundamentals:
   - Server initialization and capability negotiation
   - Tool discovery mechanism (list available tools)
   - Tool invocation handler (receive requests, return responses)
   - Resource serving capability (for match explanations)
   - Error handling per MCP specification

3. Docker service definition added to `docker-compose.yml`:
   - Port mapping (default 3000, configurable via `.env`)
   - Environment variables for LightRAG API endpoint
   - Depends on `lightrag` service

4. MCP server starts successfully and exposes protocol endpoint

5. Basic connectivity test using MCP client or curl validates:
   - Server responds to capability negotiation
   - Tool discovery returns empty list (tools added in subsequent stories)
   - Health check endpoint returns success

6. Documentation added to `/docs/mcp-server.md` describing architecture and protocol flow

### Story 3.2: Core Search Tool - Profile Match Query

**As a** recruiter,
**I want** to query for candidates matching a specific CIGREF profile,
**so that** I can find candidates aligned to standardized job requirements.

#### Acceptance Criteria

1. MCP tool implemented: `search_by_profile`
   - Parameters:
     - `profile_name` (string): CIGREF profile name (e.g., "Cloud Architect")
     - `experience_years` (optional number): Minimum years of experience
     - `top_k` (optional number, default 5): Number of results to return
   - Returns: List of candidate matches with IDs and brief summaries

2. Tool implementation:
   - Translates parameters to LightRAG API query
   - Uses LightRAG's "local" or "hybrid" retrieval mode (targets entities directly related to profile)
   - Calls LightRAG REST API with constructed query
   - Parses response and formats as structured JSON for MCP client

3. Tool exposed via MCP protocol (appears in tool discovery list)

4. Manual test validates functionality:
   - Invoke `search_by_profile` with profile_name="Cloud Architect"
   - Returns 5 relevant candidates from knowledge base
   - Response includes candidate IDs and summary text

5. Error handling for edge cases:
   - Profile name not found → returns helpful error message
   - No candidates match criteria → returns empty list with explanation
   - LightRAG API timeout → returns error with retry guidance

6. Tool schema documented with parameter descriptions and example invocations

### Story 3.3: Core Search Tool - Multi-Criteria Skill Search

**As a** recruiter,
**I want** to query for candidates by specific skills and technologies,
**so that** I can find candidates with precise technical expertise regardless of profile classification.

#### Acceptance Criteria

1. MCP tool implemented: `search_by_skills`
   - Parameters:
     - `required_skills` (array of strings): Must-have skills (e.g., ["Kubernetes", "AWS"])
     - `preferred_skills` (optional array of strings): Nice-to-have skills
     - `experience_level` (optional enum: "junior", "mid", "senior")
     - `top_k` (optional number, default 5): Number of results
   - Returns: List of candidate matches with skill overlap details

2. Tool implementation:
   - Constructs natural language query from structured parameters (e.g., "Find candidates with Kubernetes and AWS experience at senior level")
   - Calls LightRAG API with appropriate retrieval mode (likely "hybrid" for multi-criteria)
   - Post-processes results to highlight skill matches
   - Ranks candidates by skill coverage

3. Tool handles semantic similarity:
   - Query for "Kubernetes" should surface candidates mentioning "K8s" or "container orchestration"
   - Relies on LightRAG's embedding-based semantic search

4. Manual test validates:
   - Query: required_skills=["Python", "Machine Learning"], experience_level="senior"
   - Returns candidates with relevant skills
   - Results show which required/preferred skills each candidate possesses

5. Empty results handled gracefully (e.g., "No candidates found with required skill combination. Try broadening criteria.")

6. Tool registered in MCP protocol and documented with usage examples

### Story 3.4: OpenWebUI Configuration and MCP Integration

**As a** recruiter,
**I want** OpenWebUI connected to the MCP server and able to discover LightRAG-CV tools,
**so that** I can interact with the system through a conversational chat interface.

#### Acceptance Criteria

1. OpenWebUI installed and running (external service or Docker container based on Week 1 technical spike)

2. OpenWebUI configured to connect to MCP server:
   - MCP server endpoint configured in OpenWebUI settings
   - Connection protocol/transport validated (stdio, SSE, or HTTP based on compatibility)
   - Authentication handled if required (likely none for POC single-user)

3. OpenWebUI successfully discovers MCP tools:
   - Can see `search_by_profile` tool in available tools list
   - Can see `search_by_skills` tool in available tools list
   - Tool descriptions and parameters visible

4. Manual test of tool invocation from OpenWebUI:
   - Type query in chat that should trigger tool (e.g., "Find Cloud Architects with 5+ years experience")
   - OpenWebUI's LLM interprets query and invokes `search_by_profile` tool
   - Results returned from MCP server and displayed in chat

5. Error messages from MCP server render clearly in OpenWebUI chat interface

6. Documentation in `/docs/openwebui-setup.md`:
   - OpenWebUI installation instructions
   - MCP server configuration steps
   - Screenshots or examples of successful tool invocation
   - Troubleshooting common connection issues

### Story 3.5: Natural Language Query Interpretation

**As a** recruiter,
**I want** to ask questions in plain English without knowing tool names or parameters,
**so that** the system feels conversational and natural.

#### Acceptance Criteria

1. OpenWebUI's LLM (configured to use Ollama qwen3:8b or OpenWebUI's default model) successfully interprets natural language queries and invokes appropriate MCP tools:
   - "Show me senior DevOps engineers with AWS and Terraform" → `search_by_skills` with parsed parameters
   - "Find candidates matching Cloud Architect profile" → `search_by_profile`
   - "Who has Kubernetes experience?" → `search_by_skills` with required_skills=["Kubernetes"]

2. Query interpretation tested with 10 sample natural language queries covering:
   - Profile-based searches
   - Skill-based searches
   - Multi-criteria combinations
   - Varied phrasings (formal vs casual)

3. Success rate documented:
   - Target: 70%+ of test queries invoke correct tool with reasonable parameters
   - Failures analyzed (ambiguous queries, misinterpreted criteria, tool selection errors)

4. Query interpretation limitations documented in `/docs/query-capabilities.md`:
   - Types of queries that work well
   - Query patterns that struggle
   - Tips for users to phrase effective queries

5. If interpretation quality below 70%, mitigation documented:
   - Tool description refinement
   - System prompt tuning for OpenWebUI
   - Consider larger Ollama model (qwen2.5:14b) for better parsing
   - Acceptable limitation for POC if edge cases

6. Successful queries demonstrate end-to-end flow: Chat input → LLM interprets → MCP tool invoked → LightRAG retrieval → Results in chat

### Story 3.6: Conversational Query Refinement

**As a** recruiter,
**I want** to refine my search with follow-up questions in the same chat session,
**so that** I can iteratively narrow results without starting over.

#### Acceptance Criteria

1. Multi-turn conversation support validated:
   - Initial query: "Find senior cloud architects"
   - Follow-up: "Now show only those with AWS certification"
   - Follow-up: "Which have 8+ years experience?"
   - System maintains context and refines results progressively

2. Context handling mechanisms:
   - OpenWebUI maintains conversation history (built-in capability)
   - LLM uses conversation context to interpret follow-up queries
   - MCP tool invocations reflect refined criteria

3. Test scenarios covering:
   - Adding filter criteria (narrowing results)
   - Removing/relaxing criteria (broadening results)
   - Switching focus (e.g., from profile search to skill search mid-conversation)
   - Asking clarifying questions about results

4. Conversational refinement tested with 5 multi-turn scenarios:
   - Each scenario has 3-5 turns
   - Final results correctly reflect cumulative refinements
   - Success: 4 out of 5 scenarios work as expected

5. Limitations documented:
   - How many turns can the system maintain context reliably?
   - When does context window become issue?
   - Known failure modes (e.g., contradictory refinements)

6. User guidance added to documentation: Best practices for conversational search (explicit vs. implicit refinement)

### Story 3.7: Result Rendering and Display in Chat

**As a** recruiter,
**I want** candidate results displayed clearly in the chat interface with key information highlighted,
**so that** I can quickly assess matches without being overwhelmed by data.

#### Acceptance Criteria

1. MCP tool responses formatted for optimal OpenWebUI rendering:
   - Use markdown formatting (headings, bold, lists, tables)
   - Structured layout: Candidate name/ID, key skills, experience summary, match reason
   - Concise (each candidate result: 3-5 lines) with option to expand

2. Result format includes:
   - Candidate identifier (e.g., "Candidate #12" or filename)
   - Top 3-5 matching skills/competencies
   - Experience level or years
   - Brief match explanation (1 sentence: "Matched due to Kubernetes and AWS expertise")
   - Link or reference for viewing full details (Story 3.8 or Epic 4)

3. Multiple results rendered as numbered list or structured cards

4. Empty results display helpful message:
   - "No candidates found matching your criteria. Try broadening your search or adjusting requirements."

5. Long result sets (10+ candidates) handled gracefully:
   - Option to paginate or initially show top 5 with "Show more" capability
   - Or progressive rendering in chat

6. Manual review of 5 different query result renderings:
   - All are readable and scannable
   - Key information stands out visually
   - No information overload or truncation of critical data

7. Example result rendering documented in `/docs/result-format.md` with screenshots or markdown examples

### Story 3.8: Basic Candidate Detail View

**As a** recruiter,
**I want** to view detailed information about a specific candidate from search results,
**so that** I can make informed decisions about candidate suitability.

#### Acceptance Criteria

1. MCP tool implemented: `get_candidate_details`
   - Parameters:
     - `candidate_id` (string): Identifier from search results
   - Returns: Full candidate information including parsed CV content

2. Candidate detail includes:
   - Complete skills list
   - Work history (companies, roles, durations, descriptions)
   - Education and certifications
   - Projects or notable accomplishments
   - Original CV content or parsed structured data

3. Tool callable from OpenWebUI chat:
   - After seeing search results, user can ask: "Show me details for Candidate #3"
   - OpenWebUI interprets and invokes `get_candidate_details`
   - Full details rendered in chat (may be lengthy, uses collapsible sections or markdown formatting)

4. Manual test:
   - Search returns 5 candidates
   - Request details for one candidate
   - Details are comprehensive and readable

5. Detail view uses markdown formatting for structure:
   - Headings for sections (Skills, Experience, Education)
   - Tables for structured data if appropriate
   - Readable on desktop and tablet displays

6. If CV content is very long, truncate with "View full CV" instruction (full details could be added in Phase 2)

---

## Epic 4: Hybrid Retrieval & Match Explanation

**Epic Goal**: Implement intelligent LightRAG retrieval mode selection based on query complexity, enhance candidate ranking with graph-based relationship insights, generate structured match explanations showing CIGREF alignment and skill overlaps, and validate explainability with test users to ensure recommendations are trustworthy and comprehensible.

### Story 4.1: LightRAG Retrieval Mode Strategy Implementation

**As a** developer,
**I want** the MCP server to intelligently select LightRAG retrieval modes based on query characteristics,
**so that** simple queries run fast (naive/local) while complex multi-criteria queries leverage full hybrid capabilities.

#### Acceptance Criteria

1. MCP server implements retrieval mode selection logic:
   - **Naive mode**: Single-entity queries (e.g., "Who has Python experience?") → fast vector-only search
   - **Local mode**: Profile or specific competency queries (e.g., "Cloud Architects") → entity-focused with immediate graph neighborhood
   - **Global mode**: Broad domain queries (e.g., "All infrastructure specialists") → graph traversal across domains
   - **Hybrid mode**: Complex multi-criteria queries (e.g., "Senior DevOps with AWS, Terraform, and leadership") → combines vector similarity + graph relationships

2. Mode selection algorithm considers:
   - Number of criteria in query (1 criterion → naive/local, 3+ criteria → hybrid)
   - Query scope (specific entity vs. broad domain)
   - User-specified mode override if exposed as optional parameter

3. MCP tool implementations updated to pass selected mode to LightRAG API

4. Test suite validates mode selection:
   - 5 test queries per mode type (20 total)
   - Verify correct mode selected based on query characteristics
   - Document rationale for each selection

5. Performance comparison documented:
   - Response time for same query across all 4 modes
   - Quality comparison (are results different? which mode gives best results?)
   - Findings in `/docs/retrieval-modes-analysis.md`

6. Configuration option added to `.env` for default mode or mode selection strategy (allow tuning)

### Story 4.2: Graph-Based Relationship Extraction for Match Ranking

**As a** developer,
**I want** candidate ranking enhanced with graph relationship insights,
**so that** matches reflect not just keyword overlap but semantic and structural relationships between candidate experience and profile requirements.

#### Acceptance Criteria

1. When retrieving candidates, MCP server queries LightRAG for graph relationships:
   - Candidate skill nodes → competency nodes → CIGREF mission nodes
   - Candidate experience → domain entities → profile requirement entities
   - Example: Candidate mentions "Kubernetes" → graph shows "Kubernetes" relates to "container orchestration" → relates to "Cloud Infrastructure" competency → relates to "Cloud Architect" missions

2. Graph relationship scoring incorporated into ranking:
   - Direct relationships (1-hop) score higher than indirect (2-3 hops)
   - Multiple relationship paths increase confidence
   - Rare/specialized relationships weighted appropriately (domain-specific)

3. LightRAG's graph storage (PGGraphStorage via Apache AGE) queried using Cypher-like queries or LightRAG's graph API

4. Test validates graph-enhanced ranking:
   - Compare ranking with pure vector similarity vs. graph-enhanced hybrid
   - Identify cases where graph relationships surface better candidates (e.g., semantic similarity finds "SRE" when query is "DevOps Engineer")
   - Document 3-5 examples showing graph value

5. Graph queries optimized for performance:
   - Response time remains <10s for POC (graph traversal doesn't bottleneck)
   - If slow, limit graph depth (e.g., max 3 hops) or cache common paths

6. Graph relationship data included in tool responses for use in match explanations (Story 4.3)

### Story 4.3: Structured Match Explanation Generation

**As a** recruiter,
**I want** each candidate recommendation accompanied by a clear explanation of why they match,
**so that** I understand and trust the system's recommendations.

#### Acceptance Criteria

1. MCP server generates match explanations for each candidate result including:
   - **CIGREF Profile Alignment**: Which missions, activities, or deliverables align with candidate experience
   - **Skill Matches**: Exact skill overlaps (e.g., "Candidate has AWS, Kubernetes") and semantic matches (e.g., "Docker expertise relates to container orchestration")
   - **Graph Relationships**: Key relationship paths that influenced ranking (e.g., "Candidate's microservices experience connects to distributed systems competency")
   - **Confidence Score**: Numerical score (0-100) or qualitative (High/Medium/Low) indicating match strength

2. Explanation format is structured and consistent:
   - Organized by category (Profile, Skills, Experience, Graph Insights)
   - Concise (3-7 bullet points total per candidate)
   - Non-technical language accessible to recruiters without IT expertise

3. Explanation generation uses:
   - LightRAG's graph query results
   - Vector similarity scores
   - Entity extraction from candidate CV and CIGREF profiles
   - LLM (qwen3:8b via Ollama) to synthesize human-readable summary if needed

4. MCP tool responses include explanations inline with each candidate:
   ```json
   {
     "candidate_id": "candidate_12",
     "summary": "Senior Cloud Engineer, 8 years experience",
     "explanation": {
       "profile_alignment": ["Matches Cloud Architect mission: 'Design cloud infrastructure'"],
       "skill_matches": ["AWS (exact match)", "Kubernetes (exact match)", "Terraform → Infrastructure as Code competency"],
       "graph_insights": ["Microservices experience relates to distributed systems design"],
       "confidence": "High (85%)"
     }
   }
   ```

5. Manual review of explanations for 10 candidates:
   - Explanations are accurate (align with CV content and CIGREF profiles)
   - Explanations are comprehensible to non-technical reviewers
   - Explanations provide actionable insight (not generic statements)

6. Documentation includes explanation generation logic and example outputs

### Story 4.4: Match Explanation Rendering in OpenWebUI

**As a** recruiter,
**I want** match explanations displayed clearly in the chat interface,
**so that** I can quickly understand why each candidate was recommended without information overload.

#### Acceptance Criteria

1. Candidate results in OpenWebUI chat include expandable/collapsible match explanations:
   - Initial view shows candidate summary + confidence score
   - User can expand to see full explanation details
   - Or explanations auto-displayed if result set is small (<3 candidates)

2. Explanation rendering uses markdown formatting:
   - Bold for section headers (Profile Alignment, Skill Matches, etc.)
   - Bullet lists for explanation points
   - Color coding or icons for confidence levels (if OpenWebUI supports)

3. Graph relationship insights rendered understandably:
   - Avoid raw technical terms ("1-hop relation")
   - Use plain language: "Candidate's Docker expertise is related to container orchestration, a key Cloud Architect competency"

4. Manual test with 5 search queries:
   - Each returns 3-5 candidates with explanations
   - Explanations render correctly (no markdown parsing issues)
   - Information hierarchy is clear (most important info visible first)
   - No visual clutter or overwhelming text blocks

5. Test user feedback (if available during sprint):
   - 2-3 recruiters review explanation displays
   - Assess: "Are explanations helpful?" "Do you trust these recommendations?"
   - Iterate on format based on feedback

6. Screenshots or example renderings documented in `/docs/explanation-display.md`

### Story 4.5: Confidence Scoring and Ranking Refinement

**As a** recruiter,
**I want** candidates ranked by match quality with confidence scores,
**so that** I can prioritize reviewing the most promising candidates first.

#### Acceptance Criteria

1. Confidence scoring algorithm implemented combining:
   - Vector similarity score (semantic match strength)
   - Graph relationship count and depth (more/shorter paths = higher confidence)
   - Entity overlap count (number of skills/competencies matched)
   - Weighting: 40% vector similarity, 30% graph relationships, 30% entity overlap (tunable)

2. Confidence score normalized to 0-100 scale or categorized (High/Medium/Low):
   - High: 70-100 (strong match)
   - Medium: 40-69 (partial match, may need gap bridging)
   - Low: 0-39 (weak match, consider only if candidate pool is limited)

3. Candidates ranked by confidence score (highest first) in search results

4. Test validates ranking quality:
   - Manual review of top-5 candidates for 10 different queries
   - Hiring manager or experienced recruiter assesses: "Are these reasonable matches?"
   - Target: 70%+ precision@5 (from NFR4) → at least 3 out of 5 top candidates are genuinely qualified

5. If precision below threshold:
   - Analyze ranking failures (false positives: why ranked high? false negatives: missed qualified candidates?)
   - Tune scoring weights or algorithm
   - Document limitations and Phase 2 improvement strategies

6. Confidence scores included in all search tool responses and displayed to users

### Story 4.6: Query Performance Optimization and Testing

**As a** developer,
**I want** to optimize query performance across all retrieval modes,
**so that** response times meet the <10 second POC target for typical queries.

#### Acceptance Criteria

1. Performance test suite created with 20 representative queries:
   - 5 simple (single skill, naive mode)
   - 5 moderate (profile match, local mode)
   - 5 complex (multi-criteria, hybrid mode)
   - 5 very complex (broad domain + filters, global mode)

2. Each query executed 3 times, response time measured end-to-end:
   - OpenWebUI input → MCP tool invocation → LightRAG retrieval → PostgreSQL queries → Result return
   - Record: p50, p95, p99 response times

3. Performance results documented in `/docs/performance-results.md`:
   - All queries: Comparison to <10s POC target
   - Slowest queries identified with bottleneck analysis (LightRAG retrieval? PostgreSQL query? Embedding generation? Graph traversal?)

4. If queries exceed 10s target:
   - Optimization attempts: Reduce context size, limit graph depth, tune PostgreSQL indices, adjust LightRAG parameters
   - Document optimizations applied and impact
   - If still slow, acceptable for POC with Phase 2 optimization plan

5. GPU acceleration impact measured (if available):
   - Compare query times with/without GPU for Docling processing
   - Embeddings generation time (likely not GPU-accelerated via Ollama unless configured)

6. Performance recommendations for Phase 2:
   - Caching strategies
   - Index optimization
   - Parallel query execution
   - Model optimization or quantization

### Story 4.7: End-to-End User Acceptance Testing

**As a** product manager,
**I want** test users (recruiters/hiring managers) to validate the complete system workflow,
**so that** we confirm the POC meets success criteria before demonstration.

#### Acceptance Criteria

1. User acceptance test conducted with 2-5 test users (recruiters or hiring managers)

2. Test protocol:
   - Each user completes 5 predefined search scenarios (covering profile match, skill search, multi-criteria, conversational refinement)
   - Users rate each result: "Accurate match" / "Mostly accurate" / "Inaccurate"
   - Users assess explanation quality: "Helpful and clear" / "Somewhat helpful" / "Not helpful"
   - Users complete satisfaction survey:
     - "Would you use this system in your daily workflow?" (Yes/No/Maybe)
     - "Does this save time compared to manual screening?" (Yes/No)
     - "Do you trust the recommendations?" (Yes/No/Needs improvement)

3. Success metrics from brief validated:
   - **Match quality**: 70%+ of results rated "Accurate" or "Mostly accurate" (target from brief)
   - **Explainability satisfaction**: Users can articulate why candidates were recommended
   - **Adoption willingness**: 60%+ express willingness to use system (target from brief)
   - **Conversational UX**: Users successfully refine searches iteratively

4. Test results documented in `/docs/uat-results.md`:
   - Quantitative metrics (ratings, completion rates, response times)
   - Qualitative feedback (quotes, pain points, feature requests)
   - Comparison to success criteria from brief

5. If success criteria not met:
   - Root cause analysis (poor ranking? confusing explanations? slow performance? UI issues?)
   - Document gaps and Phase 2 requirements
   - Assessment: "POC demonstrates feasibility despite gaps" or "Critical issues block validation"

6. Test user feedback incorporated into final POC demonstration and Phase 2 recommendations

---

## Checklist Results Report

### Executive Summary

**Overall PRD Completeness**: 92%
**MVP Scope Appropriateness**: Just Right
**Readiness for Architecture Phase**: Ready
**Most Critical Concerns**:
- OpenWebUI MCP integration validation needed early (Week 1 technical spike)
- Apache AGE extension maturity is a medium-high risk
- User acceptance testing (Epic 4, Story 4.7) timeline may be ambitious given 2-5 user availability assumption

### Category Analysis

| Category                         | Status  | Critical Issues |
| -------------------------------- | ------- | --------------- |
| 1. Problem Definition & Context  | PASS    | None - comprehensive problem statement from brief |
| 2. MVP Scope Definition          | PASS    | Clear boundaries, "Out of Scope" well-defined |
| 3. User Experience Requirements  | PASS    | Chat-based UX well articulated, OpenWebUI assumptions documented |
| 4. Functional Requirements       | PASS    | 12 FRs cover all core capabilities; testable and clear |
| 5. Non-Functional Requirements   | PASS    | 12 NFRs with specific metrics (70% precision@5, 10s queries, 90% parsing success) |
| 6. Epic & Story Structure        | PASS    | 4 epics, 28 stories total, logical sequencing, AI-agent-sized |
| 7. Technical Guidance            | PASS    | Detailed tech stack, architecture, rationale for all major decisions |
| 8. Cross-Functional Requirements | PARTIAL | Data schema evolution not explicitly addressed in stories (acceptable for POC) |
| 9. Clarity & Communication       | PASS    | Consistent terminology, clear structure, rationale provided throughout |

### Top Issues by Priority

#### BLOCKERS
*None identified* - PRD is ready for architect to proceed.

#### HIGH
1. **Early Technical Validation Required**: Week 1 spike must validate:
   - OpenWebUI MCP protocol support and transport compatibility (flagged as HIGH risk in brief)
   - Apache AGE installation on Windows WSL2
   - LightRAG PostgreSQL storage adapter quality
   - **Recommendation**: Make this explicit in Epic 1 documentation or add as Story 1.0

2. **Test User Availability**: Epic 4, Story 4.7 assumes 2-5 test users are available for UAT. No user recruitment plan documented.
   - **Recommendation**: Add to Project Plan or defer UAT to post-POC validation if users unavailable

#### MEDIUM
1. **Incremental vs. Full Rebuild**: No story addresses whether LightRAG knowledge base supports incremental CV additions or requires full rebuilds when new data is ingested
   - **Recommendation**: Acceptable for POC (full rebuilds with 20-30 CVs is manageable); document as Phase 2 requirement

2. **Error Handling Strategy**: While individual stories mention error handling, there's no overarching error handling or logging strategy
   - **Recommendation**: Acceptable for POC; Docker logs sufficient per Technical Assumptions

3. **Data Schema Management**: No explicit stories for database migrations or schema versioning
   - **Recommendation**: Acceptable for POC (greenfield setup); Phase 2 would need migration tooling

#### LOW
1. **Batch CV Upload**: Stories assume one-at-a-time CV processing; no batch upload UI
   - **Recommendation**: Already noted as out-of-scope for MVP; Phase 2 feature

2. **Export/Report Generation**: Recruiters may want to export candidate shortlists
   - **Recommendation**: Already noted as out-of-scope; Phase 2 feature

### MVP Scope Assessment

**Just Right for POC objectives**:
- Validates core technical hypothesis (hybrid vector-graph retrieval adds value)
- Delivers end-to-end workflow (document ingestion → query → explainable results)
- Measurable against success criteria (70% precision@5, 60% adoption willingness)
- Realistic for 8-12 week timeline with single developer

### Final Decision

✅ **READY FOR ARCHITECT**

The PRD and epic structure are comprehensive, properly scoped, and ready for architectural design.

---

## Next Steps

### UX Expert Prompt

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

### Architect Prompt

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
