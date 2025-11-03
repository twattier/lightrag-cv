# Project Brief: LightRAG-CV

*Generated with Business Analyst Agent - Mary*

---

## Executive Summary

**LightRAG-CV** is a proof-of-concept application that creates an intelligent knowledge base for matching IT professional CVs against standardized job profile references. The system addresses the challenge of efficiently evaluating candidate qualifications by leveraging LightRAG's hybrid vector-graph retrieval capabilities to analyze resumes against the CIGREF IT job profile nomenclature (English edition, 2024). Target users include HR professionals, recruiters, and hiring managers in IT organizations who need to quickly assess candidate fit for specific technical roles. The key value proposition is automated, context-aware matching accessible through natural language queries in OpenWebUI, providing explainable recommendations that understand both explicit qualifications and relational insights between skills, experiences, and job requirements.

---

## Problem Statement

### Current State

HR professionals and technical recruiters face significant challenges when matching IT candidates to specific role requirements. Traditional keyword-based resume screening systems fail to capture the nuanced relationships between skills, experience domains, and job requirements. Evaluating candidates against standardized competency frameworks like CIGREF's IT profile nomenclature is currently a manual, time-intensive process that requires deep domain expertise.

### Pain Points

- **Time consumption:** Manual review of CVs against multi-dimensional profile criteria (missions, activities, deliverables, performance indicators, skills) takes hours per candidate
- **Inconsistent evaluation:** Different reviewers interpret qualifications differently, leading to missed qualified candidates or false positives
- **Limited context understanding:** Simple keyword matching misses semantic relationships (e.g., a candidate with "microservices architecture" experience may be qualified for roles requiring "distributed systems design")
- **Fragmented information:** Profile requirements exist in dense PDF documentation, making systematic comparison difficult

### Impact

- Increased time-to-hire for technical positions
- Higher risk of mismatched hires due to incomplete evaluation
- Recruiter burnout from repetitive, cognitively demanding screening tasks
- Competitive disadvantage in fast-moving IT talent markets

### Why Existing Solutions Fall Short

Simple ATS (Applicant Tracking Systems) use basic keyword matching without understanding domain relationships. Vector-only semantic search improves contextual understanding but misses the graph-based relationships between skills, domains, and competency hierarchies that are critical for structured profile frameworks.

### Urgency

This is a proof-of-concept to validate whether hybrid vector-graph RAG technology can meaningfully improve matching accuracy and speed before considering production investment. The POC timeline supports rapid validation without over-engineering.

---

## Proposed Solution

### Core Concept

LightRAG-CV creates an intelligent knowledge base that ingests both the CIGREF IT profile reference documentation and candidate CVs, then enables sophisticated querying using LightRAG's hybrid vector-graph retrieval architecture. The solution combines three complementary technologies:

1. **Docling** for intelligent document parsing and chunking of both profile references and CVs
2. **LightRAG** for hybrid storage (vector embeddings + knowledge graphs) and multi-modal retrieval
3. **PostgreSQL** with pgvector and Apache AGE extensions for unified vector and graph persistence

Users interact with the system through **OpenWebUI** via a **Model Context Protocol (MCP) server**, enabling natural language queries like "Find senior cloud architects with 8+ years experience and Kubernetes expertise."

### Key Differentiators

**Hybrid Retrieval Architecture:** Unlike pure vector similarity systems, LightRAG maintains both semantic embeddings and entity relationship graphs. This means the system understands not just that "DevOps Engineer" and "Site Reliability Engineer" are semantically similar, but also the structural relationships between skills (e.g., "Kubernetes" relates to "container orchestration" which connects to "cloud infrastructure" competencies).

**Structured Profile Framework Integration:** The CIGREF nomenclature organizes IT profiles by domains with specific missions, activities, deliverables, performance indicators, and skill taxonomies. By ingesting this as structured knowledge, the system can match candidates across multiple dimensions simultaneously.

**Conversational Search Interface:** MCP server integration with OpenWebUI enables natural language, multi-criteria queries with conversational refinement (e.g., "Now show only candidates with leadership experience").

**Optimized Query Modes:** LightRAG provides multiple retrieval strategies (naive, local, global, hybrid) that can be tuned for different use cases—quick screening vs. deep evaluation.

### Why This Will Succeed

- **Leverages proven open-source components** rather than building custom NLP/graph systems
- **Graph relationships capture domain structure** that pure embedding models miss
- **Dockerized architecture** enables rapid deployment and experimentation
- **PostgreSQL foundation** provides enterprise-grade reliability and familiar tooling
- **MCP standardization** decouples retrieval engine from interface, enabling future extensibility

### High-Level Vision

A recruiter opens OpenWebUI and types: "Find candidates matching Cloud Architect profile with 5+ years AWS experience and team leadership skills." The system returns ranked candidate matches with explainable reasoning showing which missions, skills, and deliverables align, along with gap analysis—all through conversational interaction.

---

## Target Users

### Primary User Segment: Technical Recruiters & HR Specialists

**Demographic/Firmographic Profile:**
- HR professionals and technical recruiters at IT services firms, software companies, or corporate IT departments
- Global market focus (English CIGREF framework supports international recruitment)
- Range from individual recruiters at agencies to talent acquisition teams at mid-to-large organizations
- Possess varying levels of technical knowledge—some with deep IT expertise, others with general HR backgrounds

**Current Behaviors and Workflows:**
- Manually review 20-50+ CVs per open position
- Reference CIGREF or similar competency frameworks when defining role requirements
- Use basic ATS tools for keyword filtering as initial screen
- Conduct phone screens and technical interviews based on manual CV assessment
- Maintain spreadsheets or notes tracking candidate qualifications against role criteria
- Spend significant time learning domain-specific terminology for specialized roles (cloud, data engineering, security, etc.)

**Specific Needs and Pain Points:**
- Need faster initial screening without sacrificing quality
- Struggle to consistently evaluate multi-dimensional profiles (skills + experience + deliverables + performance indicators)
- Difficulty explaining "why" a candidate is a good match to hiring managers
- Lack visibility into "near-miss" candidates who might fit with training or adjacent roles
- Need confidence in recommendations when presenting candidates

**Goals They're Trying to Achieve:**
- Reduce time-to-fill for open technical positions
- Improve quality of candidate shortlists presented to hiring managers
- Provide data-driven rationale for candidate recommendations
- Identify high-potential candidates that keyword searches might miss
- Build credibility with technical hiring managers through accurate assessments

### Secondary User Segment: Hiring Managers & Technical Leads

**Demographic/Firmographic Profile:**
- Engineering managers, technical directors, or team leads responsible for hiring decisions
- Deep technical expertise in specific domains (infrastructure, development, data, security, etc.)
- Rely on recruiters for initial screening but make final hiring decisions

**Current Behaviors and Workflows:**
- Review pre-screened candidate pools from recruiters
- Conduct technical interviews and assessments
- Often re-review CVs because they don't trust initial screening quality
- Provide feedback to recruiters about mismatched candidates

**Specific Needs and Pain Points:**
- Frustrated when recruiters present poorly matched candidates (wastes interview time)
- Need recruiters to understand nuanced technical requirements
- Want transparency into why candidates were recommended
- Desire better signal-to-noise ratio in candidate pools

**Goals They're Trying to Achieve:**
- Receive qualified candidate shortlists that actually match role requirements
- Minimize time spent interviewing unqualified candidates
- Trust that screening process captures both explicit skills and domain understanding
- Focus interview time on culture fit and advanced technical assessment rather than basic qualification verification

---

## Goals & Success Metrics

### Business Objectives

- **Validate technical feasibility:** Demonstrate that hybrid vector-graph RAG can successfully parse and match CVs against CIGREF profiles with measurable accuracy within 8-12 week POC timeline
- **Proof of value:** Show 40-60% reduction in manual screening time for a test set of 50-100 CVs across 5-10 CIGREF profile types
- **Technology stack validation:** Confirm that Docling, LightRAG, and PostgreSQL (with pgvector + AGE) can integrate effectively in a containerized architecture with MCP server and OpenWebUI
- **Establish baseline metrics:** Create measurement framework for matching quality, retrieval performance, and explainability that can inform production investment decisions

### User Success Metrics

- **Screening efficiency:** Users can evaluate a candidate against a profile in under 3 minutes (vs. 15-20 minutes manual review)
- **Match quality perception:** Users rate match recommendations as "accurate" or "mostly accurate" in 70%+ of cases
- **Explainability satisfaction:** Users can understand and articulate why a candidate was recommended (graph relationships visible and comprehensible)
- **Coverage validation:** System successfully identifies qualified candidates that keyword searches would miss (measure via A/B comparison)
- **Adoption willingness:** 60%+ of test users express willingness to use system in daily workflow based on POC experience
- **Conversational UX value:** Users successfully refine searches iteratively through natural language

### Key Performance Indicators (KPIs)

- **Retrieval Accuracy:** Top-5 candidate rankings include at least 3 genuinely qualified candidates as validated by hiring manager review (target: 70% precision@5)
- **Query Response Time:** Return ranked candidate matches within 5 seconds for typical queries (target: <3 seconds p95 for production)
- **Graph Coverage:** Successfully extract and store entities/relationships from 85%+ of CIGREF profile content (missions, skills, deliverables, etc.)
- **Document Processing Success Rate:** Docling successfully parses and chunks 90%+ of CV formats (PDF, DOCX) without critical information loss
- **Explainability Depth:** Generate at least 3 specific graph-based insights per match (e.g., "Candidate's cloud migration experience connects to Infrastructure Architect mission X")
- **System Stability:** Docker compose environment runs for 48+ hours without crashes or memory issues
- **MCP Integration Reliability:** OpenWebUI successfully discovers and invokes MCP tools with <5% error rate

---

## MVP Scope

### Core Features (Must Have)

- **CIGREF Profile Ingestion:** Parse the CIGREF IT profile nomenclature PDF (English 2024 edition), extract structured data (domains, profiles, missions, activities, deliverables, performance indicators, skills), and store in LightRAG knowledge base with both vector embeddings and graph relationships

- **CV Document Processing:** Accept PDF and DOCX CV uploads, use Docling with HybridChunker to parse and chunk content intelligently, extract key information (skills, experience, education, projects), and index in LightRAG

- **MCP Server Implementation:** Build Model Context Protocol (MCP) server that exposes LightRAG-CV capabilities as tools/resources accessible to LLMs through OpenWebUI

- **Natural Language Query Interface:** Enable users to query in natural language through OpenWebUI (e.g., "Find candidates with 5+ years cloud architecture experience and Kubernetes expertise," "Who has experience with both microservices and team leadership?")

- **Multi-Criteria Search Tools:** MCP tools for:
  - Searching by CIGREF profile match
  - Filtering by specific skills/technologies
  - Experience level and domain filtering
  - Combined criteria queries leveraging LightRAG's hybrid retrieval

- **Hybrid Retrieval Modes:** Leverage LightRAG's query modes (naive, local, global, hybrid) with MCP server intelligently selecting appropriate mode based on query complexity

- **Match Explanation Resources:** MCP resources providing structured explanations for each candidate recommendation:
  - Which profile missions/activities align with candidate experience
  - Key skill matches (exact and semantically similar)
  - Graph relationships influencing ranking (e.g., candidate's "Kubernetes" expertise → container orchestration → cloud infrastructure competency)
  - Confidence scores and reasoning transparency

- **Docker Compose Deployment:** Complete containerized setup:
  - Docling service (document parsing with optional GPU acceleration profile)
  - LightRAG server (RAG engine)
  - PostgreSQL with pgvector + AGE (storage)
  - LightRAG-CV MCP Server (protocol server)
  - All ports configurable via .env
  - Docker Compose profiles for GPU acceleration on Docling service

- **PostgreSQL Persistence:** Configure LightRAG to use PGKVStorage, PGVectorStorage, PGGraphStorage, and PGDocStatusStorage for unified data persistence

- **Ollama LLM Integration:** Connect to external Ollama instance with qwen3:8b for generation, bge-m3 for embeddings, and bge-reranker-v2-m3 for reranking as specified in project requirements

- **OpenWebUI Integration:** Configuration and documentation for connecting the MCP server to external OpenWebUI instance, enabling conversational CV search through chat interface

### Out of Scope for MVP

- Custom web UI (OpenWebUI provides interface)
- User authentication beyond OpenWebUI's existing auth
- Multi-tenancy (single knowledge base for POC)
- Production-grade error handling and logging
- CV data validation or quality scoring
- Automated CV sourcing or scraping
- Integration with ATS systems
- Real-time CV updates or change notifications
- Advanced analytics or reporting dashboards
- Mobile-specific optimizations
- Multi-language support (English only for POC)
- Custom profile creation (CIGREF reference only)
- Candidate ranking persistence or comparison history
- A/B testing infrastructure
- Performance optimization beyond functional requirements
- Complex workflow automation (save searches, alerts, etc.)
- Direct export to ATS or email from results

### MVP Success Criteria

The MVP will be considered successful if:

1. **End-to-end functionality:** Users can ask natural language questions in OpenWebUI and receive relevant candidate recommendations (e.g., "Show me senior DevOps engineers with AWS and Terraform experience")

2. **MCP integration reliability:** MCP server successfully exposes LightRAG-CV tools, OpenWebUI can discover and invoke them, and context/results flow correctly between components

3. **Multi-criteria search capability:** Users can combine multiple filters in natural language (skills + experience level + CIGREF profile alignment) and get coherent results

4. **Deployment reliability:** Docker compose stack (4 containers: Docling, LightRAG, PostgreSQL, MCP Server) launches successfully on Windows WSL2/Docker Desktop and runs stably during test sessions

5. **Retrieval quality:** Manual evaluation of 20 natural language test queries shows 60%+ of top-3 recommendations are reasonable matches as validated by hiring managers

6. **Conversational experience:** Users can refine queries iteratively (e.g., "Now show only candidates with leadership experience," "Which of these has the most Python projects?")

7. **Explainability through chat:** Match explanations render clearly in OpenWebUI chat interface with specific graph relationships and are comprehensible to non-technical recruiters

8. **Performance baseline:** Queries complete within 10 seconds (acceptable for POC; production target <3s)

9. **Technical validation:** Confirms LightRAG + Docling + PostgreSQL + MCP architecture is viable and demonstrates value of hybrid retrieval approach

---

## Post-MVP Vision

### Phase 2 Features

**Enhanced MCP Tool Suite:**
- **Comparative analysis tools:** "Compare these 3 candidates side-by-side for this role"
- **Gap analysis:** "What skills does this candidate lack for Senior Cloud Architect role?"
- **Career trajectory matching:** "Find candidates whose progression suggests they're ready for next-level roles"
- **Batch operations:** "Evaluate these 50 CVs against this job description and rank them"

**Improved Retrieval & Ranking:**
- Fine-tune embedding models on IT recruitment domain data
- Custom reranking models trained on recruiter feedback
- Configurable weighting for different criteria (skills vs. experience vs. education)
- Support for "soft match" queries (candidates who could grow into the role)

**Knowledge Base Enhancements:**
- Ingest multiple profile frameworks (not just CIGREF—add custom organizational competency models)
- Extract project descriptions and accomplishments with more granularity
- Entity resolution for companies, technologies, certifications
- Temporal understanding (recent experience weighted higher than outdated skills)

**User Experience Improvements:**
- Save and recall frequent queries/profiles through MCP resources
- Annotate candidates (mark as interviewed, hired, rejected) and refine future searches
- Export candidate shortlists in recruiter-friendly formats
- Integration with calendar tools for interview scheduling context

**Multi-User Support:**
- Team workspaces with shared knowledge bases
- User-specific search history and preferences
- Collaborative candidate evaluation (multiple recruiters can comment)

### Long-term Vision (1-2 Years)

**Production-Grade Platform:**
Transform from POC to enterprise recruitment intelligence platform accessible through multiple interfaces (OpenWebUI, custom web app, API, Slack/Teams bots via MCP)

**Multi-Modal Understanding:**
- Parse LinkedIn profiles, GitHub contributions, StackOverflow activity
- Video interview analysis (if transcripts available)
- Portfolio and project demonstration understanding
- Reference check synthesis

**Predictive Analytics:**
- Success prediction: "How likely is this candidate to succeed in this role?" (based on historical hire data)
- Retention risk: Identify candidates likely to stay vs. job-hop
- Skill trajectory: Predict candidate growth potential based on learning patterns

**Marketplace & Community:**
- Shared anonymized competency graphs contributed by organizations
- Industry-specific profile frameworks beyond CIGREF
- Community-validated skill taxonomies and relationship graphs

**Advanced Automation:**
- Automatic candidate outreach generation (personalized emails based on CV-profile alignment)
- Interview question generation tailored to candidate strengths/gaps
- Hiring pipeline optimization recommendations

### Expansion Opportunities

**Geographic/Market Expansion:**
- Support international competency frameworks (O*NET, ESCO, SFIA, etc.)
- Multi-language CV processing and matching
- Region-specific labor market insights

**Adjacent Use Cases:**
- **Internal talent mobility:** Match existing employees to new roles
- **Learning & Development:** Identify skill gaps and recommend training
- **Workforce planning:** Analyze organizational competency coverage and gaps
- **Freelancer/contractor matching:** Optimize gig workforce allocation

**Technology Licensing:**
- MCP server framework as standalone product for other document-knowledge-matching use cases (RFP responses, legal discovery, research literature review)
- LightRAG configuration recipes for structured professional document domains

**Data Products:**
- Anonymized skill trend reports for IT market
- Competency benchmark data
- Salary/demand correlation insights

---

## Technical Considerations

### Platform Requirements

- **Target Platform:** Docker Desktop on Windows WSL2 (Ubuntu or compatible distribution)
- **Container Runtime:** Docker Compose v2.x for multi-container orchestration
- **Network Requirements:** All services communicate via Docker internal networking; external access only to MCP server ports
- **Storage Requirements:**
  - PostgreSQL data volumes (estimated 5-10GB for POC with 100 CVs + CIGREF data)
  - LightRAG cache/index storage (estimated 2-5GB)
- **Performance Requirements:**
  - Query response time <10s for POC (target <3s for production)
  - Document ingestion: 1-2 CVs per minute acceptable for POC (GPU acceleration improves throughput)
  - Concurrent users: Single user for POC (design should allow 5-10 concurrent for Phase 2)

### Technology Preferences

**Frontend/Interface:**
- **OpenWebUI:** External service providing user interface for natural language interaction
- **Configuration:** Connect to MCP server endpoint for tool access
- **No custom UI development** for MVP

**Backend Services:**
- **LightRAG Server:** Python-based RAG engine (from HKUDS/LightRAG repo with API support)
- **MCP Server:** Python or TypeScript implementation exposing LightRAG-CV tools
  - Framework options: Python `mcp` library or TypeScript `@modelcontextprotocol/sdk`
  - Protocol: MCP stdio or SSE transport based on OpenWebUI compatibility
- **Docling Service:** Python service wrapping Docling library with REST API for document processing
  - GPU acceleration support via Docker Compose profiles
- **Ollama:** External LLM inference server (running on host or separate container)

**Database:**
- **PostgreSQL 16+** with extensions:
  - `pgvector` 0.5.0+ for vector similarity search
  - `Apache AGE` for graph database capabilities
- **Schema Design:** Leverage LightRAG's PG storage adapters (PGKVStorage, PGVectorStorage, PGGraphStorage, PGDocStatusStorage)
- **Connection Pooling:** Use pgBouncer or equivalent if concurrent query load requires it (Phase 2)

**Hosting/Infrastructure:**
- **Development Environment:** Docker Desktop on Windows WSL2
- **Container Orchestration:** Docker Compose with .env-based configuration
- **Port Management:** All ports configurable via .env to avoid conflicts with existing services
- **Volumes:** Named volumes for PostgreSQL data persistence, bind mounts for configuration files
- **Networking:** Single Docker network for inter-service communication
- **GPU Support:** Docker Compose profiles for optional NVIDIA GPU acceleration (requires nvidia-docker runtime)
- **Future Production:** Could migrate to Kubernetes, cloud-hosted Postgres, managed vector DBs (Phase 2)

### Architecture Considerations

**Repository Structure:**
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
│   └── cvs/              # Test CV files (from Hugging Face)
├── docs/                 # Documentation including this brief
└── scripts/              # Setup and utility scripts
```

**Service Architecture:**
- **Microservices approach:** Each component (Docling, LightRAG, PostgreSQL, MCP Server) runs in isolated container
- **External services:** OpenWebUI and Ollama run externally, connected via network
- **Communication flow:**
  1. User queries OpenWebUI in natural language
  2. OpenWebUI invokes MCP Server tools via MCP protocol
  3. MCP Server translates to LightRAG API calls
  4. LightRAG queries PostgreSQL (vectors + graphs) and generates response via Ollama
  5. MCP Server formats results and returns to OpenWebUI
  6. OpenWebUI renders conversational response with candidate recommendations

**Integration Requirements:**
- **MCP Protocol Compliance:** MCP server must implement tool discovery, invocation, and resource serving per MCP specification
- **LightRAG API:** MCP server integrates with LightRAG's REST API (documented in lightrag/api/README.md)
- **Docling Integration:** Direct API calls from MCP server or LightRAG to Docling service for document processing
- **Ollama Integration:** LightRAG configured to use Ollama-compatible endpoints for LLM, embedding, and reranking
- **OpenWebUI-MCP Connection:** Configuration of MCP server endpoint in OpenWebUI settings

**Security/Compliance:**
- **Data Privacy:** All processing local (no cloud API calls for POC)—important for handling PII in CVs
- **Network Isolation:** Services communicate via internal Docker network; only MCP server port exposed
- **Credential Management:** Database passwords, API keys in .env file (NOT committed to repo)
- **Access Control:** No authentication for POC (single-user assumption); Phase 2 adds user auth via OpenWebUI
- **Compliance:** GDPR considerations deferred to Phase 2 (POC uses test/synthetic data or anonymized CVs)

---

## Constraints & Assumptions

### Constraints

**Budget:**
- **Zero additional software licensing costs** - All components must be open-source
- **Local infrastructure only** - No cloud service expenses (API calls, hosting, managed databases)
- **Development resources:** Assumed single developer or small team for 8-12 week POC timeline
- **No dedicated QA/testing budget** - Manual testing with limited test user pool

**Timeline:**
- **8-12 weeks total** for POC from kickoff to demonstration
- **Quick results priority** per project directive
- **No time for custom model training** - Must use pre-trained Ollama models as-is
- **Limited iteration cycles** - Prioritize "good enough" over "perfect"

**Resources:**
- **Single Windows WSL2 development environment** - No dedicated servers or multi-environment setup
- **Test data availability:**
  - CIGREF English PDF available (2024 edition)
  - Test CVs: Hugging Face datasets available (gigswar/cv_files, d4rk3r/resumes-raw-pdf)
  - No access to production ATS data or real candidate pipelines
- **No dedicated UX/design resources** - Rely on OpenWebUI's existing interface
- **Limited recruiter availability** for user testing (estimated 2-5 test users for feedback)

**Technical:**
- **Must run on Windows WSL2 + Docker Desktop** - No Linux server or cloud deployment option
- **Network port conflicts** - Many standard ports already in use; all services must be .env-configurable
- **Memory constraints** - PostgreSQL + services must fit in available RAM (estimated 16-32GB available)
- **Optional GPU acceleration** - CPU-only fallback required; GPU acceleration available via Docker profiles if NVIDIA runtime present
- **Single language support** - English CIGREF framework + English CVs only
- **No integration with existing systems** - Standalone POC, no ATS/HRIS connectivity

### Key Assumptions

**Technical Assumptions:**
- **LightRAG PostgreSQL storage adapters** (PGKVStorage, PGVectorStorage, PGGraphStorage) are stable and well-documented
- **Apache AGE extension** is compatible with PostgreSQL 16+ and supports required graph operations
- **Docling HybridChunker** can effectively parse both CIGREF PDF and typical CV formats (PDF, DOCX)
- **OpenWebUI supports MCP protocol** or can be configured to communicate with MCP servers
- **qwen3:8b model** (8B parameters) is capable enough to parse complex multi-criteria recruitment queries accurately
- **bge-m3 embeddings** (1024-dimensional) capture sufficient semantic nuance for IT domain matching
- **LightRAG's hybrid retrieval** provides measurable advantage over vector-only approaches

**Data Assumptions:**
- **CIGREF English PDF structure** (2024 edition) is consistent and parseable (profiles organized by domains with clear mission/skill/deliverable sections)
- **Hugging Face CV datasets** contain sufficient English IT/technical resumes for POC validation
- **50-100 CVs provide sufficient diversity** for meaningful POC validation
- **Public CV datasets** are acceptable for POC (no access to real candidate data required)
- **Profile-to-CV mapping is feasible** (CVs contain enough information to match against CIGREF criteria)

**User Assumptions:**
- **Target users (recruiters) are comfortable with chat interfaces** and conversational query paradigms
- **Natural language queries will be reasonable** (not adversarial or edge-case testing during POC)
- **2-5 test users provide sufficient feedback** for POC validation
- **Users understand POC limitations** (incomplete data, slower performance, rough edges)
- **English-only interface** acceptable for global IT recruitment use cases

**Business Assumptions:**
- **POC success leads to Phase 2 funding** - Demonstration of technical feasibility justifies production investment
- **70% matching accuracy is "good enough"** to prove value proposition
- **Explainability is valued** by users (not just accuracy scores)
- **8-12 week timeline is acceptable** to stakeholders (no pressure for faster delivery)
- **Single-user POC demonstrates multi-user potential** (scalability can be inferred)

**Process Assumptions:**
- **No formal user research required** - Can infer recruiter needs from domain knowledge
- **Manual evaluation is acceptable** for POC metrics (no automated testing infrastructure)
- **Iterative refinement possible** within timeline (feedback loops with test users)
- **Documentation can be minimal** for POC (focus on working code over comprehensive docs)

---

## Risks & Open Questions

### Key Risks

- **OpenWebUI MCP Compatibility (HIGH):** OpenWebUI may not support MCP protocol or require specific configuration that's undocumented. If incompatible, would need to build custom web interface or use alternative MCP-compatible client (Claude Desktop, Continue.dev), significantly impacting timeline.
  - *Mitigation:* Early spike to validate OpenWebUI MCP integration; have fallback to basic web API + simple UI

- **CIGREF PDF Parsing Quality (HIGH):** Docling may struggle to extract structured information from CIGREF English PDF if formatting is complex (tables, multi-column layouts, nested hierarchies). Poor extraction quality undermines entire matching capability.
  - *Mitigation:* Manual inspection of parsed output early; potentially pre-process PDF or supplement with manual CIGREF data structuring

- **PostgreSQL AGE Extension Maturity (MEDIUM-HIGH):** Apache AGE is relatively new compared to pgvector. Installation complexity, bugs, or performance issues could derail graph storage approach. LightRAG's PGGraphStorage adapter may be incomplete or poorly tested.
  - *Mitigation:* Test PostgreSQL + AGE + pgvector setup in first week; fallback to Neo4j + Qdrant if PostgreSQL approach fails

- **qwen3:8b Query Parsing Capability (MEDIUM):** 8B parameter model may lack sophistication to reliably parse complex multi-criteria queries (e.g., "Find senior architects with 8+ years cloud experience, Kubernetes certification, and team leadership skills"). Incorrect parsing leads to poor search results regardless of retrieval quality.
  - *Mitigation:* Test with larger Ollama models (qwen2.5:14b or qwen2.5:32b) if query parsing fails; simplify to structured query inputs as fallback

- **LightRAG Production Readiness (MEDIUM):** LightRAG is an academic/research project. API stability, error handling, documentation quality, and PostgreSQL adapter completeness are unknown. May encounter bugs or missing features during integration.
  - *Mitigation:* Budget time for LightRAG bug fixes/contributions; consider forking repo if modifications needed; evaluate alternative RAG frameworks (LlamaIndex, LangChain) as fallback

- **Embedding Model Domain Fit (MEDIUM):** bge-m3 is general-purpose multilingual model. May not capture nuanced IT domain semantics (e.g., "Kubernetes" vs "K8s" vs "container orchestration"). Could lead to missed matches or false positives.
  - *Mitigation:* Test retrieval quality early; consider domain-specific embeddings (e.g., CodeBERT for technical content) if results poor

- **Test Data Quality (MEDIUM):** Hugging Face CV datasets may not contain sufficient English IT-focused resumes or may have quality/format inconsistencies. Limited diversity impacts validation quality.
  - *Mitigation:* Manually filter datasets for IT/technical resumes; supplement with synthetic CVs generated using LLMs if needed; start with 20-30 high-quality CVs minimum

- **Performance/Scalability (LOW-MEDIUM):** CPU-only inference with qwen3:8b + embedding generation + graph traversal may exceed 10s query time target, especially with 100+ CVs in knowledge base. Slow queries hurt user experience.
  - *Mitigation:* Optimize LightRAG retrieval parameters; reduce context size; use GPU acceleration via Docker profiles if available; acceptable for POC if <15s

- **User Adoption Resistance (LOW-MEDIUM):** Recruiters may prefer traditional keyword search or distrust AI recommendations. Chat interface may feel unfamiliar for professional recruitment workflows.
  - *Mitigation:* Clear explainability; allow users to see "why" recommendations made; emphasize augmentation (not replacement) of recruiter judgment

### Open Questions

**Technical:**
- Does OpenWebUI natively support MCP protocol, or does it require plugin/extension?
- What MCP transport does OpenWebUI support (stdio, SSE, HTTP)?
- What is LightRAG's actual PostgreSQL storage adapter implementation quality and documentation state?
- Can Apache AGE handle expected graph complexity (thousands of entities, tens of thousands of relationships)?
- How long does Docling take to process typical 2-page CV with/without GPU acceleration?
- What is realistic embedding generation throughput on CPU vs GPU (CVs/minute)?
- Does LightRAG support incremental index updates, or require full rebuild when adding CVs?

**Data & Content:**
- What is exact structure of CIGREF English PDF (2024 version)? How many profiles? How organized?
- Are CIGREF profile skill taxonomies hierarchical or flat?
- What percentage of Hugging Face datasets (gigswar, d4rk3r) contain IT/technical resumes?
- What CV formats are most common in datasets (PDF, DOCX, other)?
- Should we include education, certifications, projects in matching, or focus only on experience/skills?
- How important is recency weighting (recent experience > old experience)?

**User Experience:**
- What are actual recruiter query patterns? (Do they search by profile, by skills, by combined criteria?)
- How important is ranking explanation vs. just seeing top matches?
- Should system return 5, 10, or 20 candidates per query?
- Do users want "strict match" vs "potential match with training"?
- Is conversational refinement (follow-up questions) valuable or distracting?

**Business & Product:**
- What accuracy threshold (precision@5) would make recruiters trust the system?
- Is POC success measured by technical validation, user satisfaction, or both equally?
- Who are the decision-makers for Phase 2 funding? What metrics do they care about?
- Should POC focus on breadth (multiple use cases) or depth (one use case done well)?
- Is candidate ranking sufficient, or do users need scoring/confidence levels?

**Integration & Deployment:**
- Should MCP server run as container or host process?
- How should users load CVs into system (upload via OpenWebUI, file system watch, API, Hugging Face dataset ingestion)?
- Is there existing infrastructure/tooling preference we should align with?
- What logging/observability is needed for POC vs deferred to Phase 2?

### Areas Needing Further Research

**Before Development Begins:**
- **Validate OpenWebUI MCP support:** Install OpenWebUI, review documentation, test MCP server connection
- **Inspect CIGREF English PDF structure:** Download 2024 edition and manually review to understand parsing requirements
- **Test PostgreSQL AGE installation:** Verify Windows WSL2 compatibility and setup complexity
- **Review LightRAG PostgreSQL adapters:** Examine source code for PGKVStorage, PGVectorStorage, PGGraphStorage implementation quality
- **Evaluate Hugging Face datasets:** Sample CVs from both datasets to assess IT resume coverage and quality

**During First Sprint:**
- **Docling CIGREF parsing quality:** Run Docling on CIGREF English PDF and evaluate structured extraction accuracy
- **LightRAG API capabilities:** Test query modes (naive, local, global, hybrid) and understand parameter tuning
- **qwen3:8b query parsing:** Prototype natural language query interpretation and assess reliability
- **Embedding quality baseline:** Test bge-m3 semantic similarity for IT terms (e.g., "DevOps" vs "SRE" vs "Platform Engineer")
- **GPU acceleration impact:** Measure Docling throughput with CPU-only vs GPU profiles

**User Research:**
- **Recruiter workflow observation:** Shadow 1-2 recruiters to understand actual CV screening process
- **Query pattern collection:** Gather examples of how recruiters currently search/filter candidates
- **Pain point validation:** Confirm assumptions about time consumption, inconsistency, and keyword search limitations

---

## Appendices

### A. References

**Primary Source Documents:**
- **CIGREF IT Profile Nomenclature (English, 2024):** https://www.cigref.fr/wp/wp-content/uploads/2024/12/Cigref_Nomenclature_des_profils_metiers_SI_EN_2024.pdf
- **LightRAG GitHub Repository:** https://github.com/HKUDS/LightRAG
- **LightRAG API Documentation:** https://github.com/HKUDS/LightRAG/blob/main/lightrag/api/README.md
- **Docling Project:** https://github.com/docling-project/docling
- **PostgreSQL Docker:** https://github.com/docker-library/postgres

**Test Data Sources:**
- **CV Dataset 1 (gigswar):** https://huggingface.co/datasets/gigswar/cv_files
- **CV Dataset 2 (d4rk3r):** https://huggingface.co/datasets/d4rk3r/resumes-raw-pdf

**Technology Stack References:**
- **pgvector Extension:** https://github.com/pgvector/pgvector
- **Apache AGE (Graph Extension):** https://age.apache.org/
- **Model Context Protocol (MCP):** https://modelcontextprotocol.io/
- **OpenWebUI:** https://github.com/open-webui/open-webui
- **Ollama:** https://ollama.ai/

**LLM Models (External Ollama):**
- **qwen3:8b** (Generation)
- **bge-m3:latest** (Embeddings, 1024-dimensional)
- **xitao/bge-reranker-v2-m3** (Reranking)

### B. Initial Project Setup Reference

**Environment Requirements:**
- Windows WSL2 (Ubuntu recommended)
- Docker Desktop
- Docker Compose v2.x
- Minimum 16GB RAM (32GB recommended)
- 20GB free disk space
- Optional: NVIDIA GPU with nvidia-docker runtime for Docling acceleration

**Configuration Template (.env):**
```bash
# LLM Configuration (External Ollama Service)
LLM_BINDING=ollama
LLM_MODEL=qwen3:8b
LLM_BINDING_HOST=http://host.docker.internal:11434
OLLAMA_LLM_NUM_CTX=40960

# Embedding Configuration
EMBEDDING_BINDING=ollama
EMBEDDING_BINDING_HOST=http://host.docker.internal:11434
EMBEDDING_MODEL=bge-m3:latest
EMBEDDING_DIM=1024

# Reranking Configuration
RERANK_BINDING=ollama
RERANK_BINDING_HOST=http://host.docker.internal:11434
RERANK_MODEL=xitao/bge-reranker-v2-m3

# Storage Configuration
LIGHTRAG_KV_STORAGE=PGKVStorage
LIGHTRAG_VECTOR_STORAGE=PGVectorStorage
LIGHTRAG_GRAPH_STORAGE=PGGraphStorage
LIGHTRAG_DOC_STATUS_STORAGE=PGDocStatusStorage

# PostgreSQL Configuration
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=lightrag_cv
POSTGRES_USER=lightrag
POSTGRES_PASSWORD=<changeme>

# Service Ports (configurable to avoid conflicts)
MCP_SERVER_PORT=3000
LIGHTRAG_API_PORT=9621
DOCLING_API_PORT=8000
POSTGRES_PORT=5432
```

**Docker Compose Profiles:**
- **Default profile:** CPU-only operation for all services
- **GPU profile:** Enable GPU acceleration for Docling service (requires nvidia-docker runtime)
  ```bash
  # Run with GPU acceleration
  docker compose --profile gpu up

  # Run without GPU (CPU only)
  docker compose up
  ```

---

## Next Steps

### Immediate Actions

1. **Validate Critical Assumptions (Week 1):**
   - Install OpenWebUI and verify MCP protocol support/configuration
   - Download CIGREF English PDF (2024 edition) and manually inspect structure
   - Set up PostgreSQL with pgvector + AGE extensions on WSL2 test environment
   - Clone LightRAG repository and review PostgreSQL storage adapter code quality
   - Sample Hugging Face CV datasets to assess IT resume coverage

2. **Technical Spike - Core Integration (Week 1-2):**
   - Build minimal MCP server exposing single test tool
   - Connect MCP server to OpenWebUI and verify end-to-end communication
   - Test Docling parsing on CIGREF PDF and 2-3 sample CVs from Hugging Face datasets
   - Deploy LightRAG with PostgreSQL storage and confirm basic ingestion/query works
   - Test GPU acceleration profile for Docling if available

3. **Data Preparation (Week 2):**
   - Download CV datasets from Hugging Face (gigswar and d4rk3r)
   - Filter for English IT/technical resumes (target 50-100 CVs)
   - Process CIGREF English PDF through Docling and validate structured extraction quality
   - Create test query set (20 natural language queries covering different criteria)

4. **MVP Development (Week 3-6):**
   - Implement complete MCP server with all planned tools (profile search, multi-criteria, explanations)
   - Integrate Docling, LightRAG, and PostgreSQL in Docker Compose environment
   - Ingest CIGREF profiles and test CV corpus into knowledge base
   - Develop match explanation generation logic using graph relationships
   - Configure Docker Compose profiles for optional GPU acceleration

5. **Testing & Refinement (Week 7-9):**
   - Manual quality evaluation on test query set (measure precision@5, response time)
   - User testing with 2-5 recruiters/hiring managers
   - Iterate on query parsing, retrieval parameters, and explanation clarity
   - Document findings and metrics

6. **POC Demonstration (Week 10):**
   - Prepare demo scenarios showcasing multi-criteria natural language search
   - Present results to stakeholders with metrics and user feedback
   - Discuss Phase 2 decision based on outcomes

### PM Handoff

This Project Brief provides comprehensive context for **LightRAG-CV**, a proof-of-concept demonstrating hybrid vector-graph RAG for intelligent CV-to-profile matching through conversational search via MCP and OpenWebUI.

**Key Handoff Notes:**
- **Architecture Decision:** MCP server + OpenWebUI approach requires early validation (Week 1 spike)
- **Critical Path:** CIGREF PDF parsing quality and OpenWebUI MCP compatibility are make-or-break
- **Scope Management:** POC is intentionally minimal—resist feature creep; defer polish/optimization to Phase 2
- **Success Metrics:** Focus on retrieval quality (70% precision@5) and explainability, not performance optimization
- **Timeline:** 8-12 weeks is aggressive—prioritize working end-to-end over perfection in any component
- **Test Data:** Hugging Face datasets provide CV sources; validate IT resume coverage early

**Next Artifact:** Product Requirements Document (PRD) should detail:
- MCP tool specifications (tool names, parameters, response schemas)
- LightRAG configuration and query mode selection logic
- Match explanation format and data model
- User stories for natural language query patterns
- Acceptance criteria for each MVP feature
- Docker Compose configuration including GPU profiles

Please review this brief thoroughly, validate assumptions (especially OpenWebUI MCP support and CIGREF parsing), and work with the development team to create the detailed PRD for implementation.

---

*Document generated by Business Analyst Agent - Mary*
*Based on: docs/INITIAL.md*
*Date: 2025-11-03*
