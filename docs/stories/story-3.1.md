# Story 3.1: MCP Server Scaffold and Protocol Implementation

> 📋 **Epic**: [Epic 3: MCP Server & OpenWebUI Integration](../epics/epic-3.md)
> 📋 **Architecture**: [Components - MCP Server](../architecture/components.md#component-3-mcp-server), [Infrastructure and Deployment](../architecture/infrastructure-and-deployment.md)
>
> ⚠️ **PREREQUISITES**: This story cannot begin until **both technical spikes are complete**:
> - ✅ [Technical Spike: OpenWebUI MCP Integration Validation](../technical-spikes/openwebui-mcp-validation.md)
> - ✅ [Technical Spike: MCP SDK Selection](../technical-spikes/mcp-sdk-selection.md)

## User Story

**As a** developer,
**I want** MCP server skeleton implementing the Model Context Protocol specification,
**so that** I can expose tools and resources to MCP-compatible clients like OpenWebUI.

## Acceptance Criteria

### AC1: MCP Server Implementation with Selected SDK

**Prerequisites:**
- [x] Technical Spike: MCP SDK Selection complete ([link](../technical-spikes/mcp-sdk-selection.md))
- [x] SDK decision documented and rationale clear

**Implementation:**

MCP server implementation created using **SDK selected from technical spike**:
- **If Python `mcp` selected:**
  - Location: `app/mcp_server/` (follows [app/ directory pattern](../architecture/source-tree.md))
  - Uses `app.shared.config` for all configuration ([RULE 2](../architecture/coding-standards.md#rule-2))
  - Can leverage `app.shared.llm_client` if LLM interactions needed
  - Integration with existing Python 3.11 codebase

- **If TypeScript `@modelcontextprotocol/sdk` selected:**
  - Location: `services/mcp-server/`
  - Separate Node.js 20+ runtime
  - Environment variable configuration
  - Separate deployment container

**Validation:**
- SDK installation successful
- Basic server initialization works
- No dependency conflicts with existing project

---

### AC2: MCP Protocol Fundamentals Implemented

MCP server implements core protocol capabilities:

1. **Server Initialization**
   - Server starts and binds to configured port
   - Capability negotiation implemented per MCP spec
   - Protocol version handling

2. **Tool Discovery Mechanism**
   - Endpoint/method for listing available tools
   - Returns tool schemas (name, description, parameters)
   - Initially returns empty list (tools added in Stories 3.2-3.3, 3.8)

3. **Tool Invocation Handler**
   - Endpoint/method for invoking tools
   - Receives tool name and parameters
   - Returns structured responses
   - Handles JSON serialization/deserialization

4. **Resource Serving Capability**
   - Support for serving resources (used in Epic 4 for match explanations)
   - Resource discovery mechanism
   - Resource retrieval handler

5. **Error Handling**
   - MCP-compliant error responses
   - HTTP status codes (if HTTP protocol)
   - Error message formatting
   - Logging with structured context ([RULE 7](../architecture/coding-standards.md#rule-7))

**Validation:**
- Server initialization completes without errors
- Tool discovery endpoint responds correctly
- Invocation handler accepts requests (even if no tools registered yet)
- Error responses follow MCP specification

---

### AC3: Docker Configuration with app.shared.config Integration

**Prerequisites:**
- [x] Protocol selection from OpenWebUI spike ([link](../technical-spikes/openwebui-mcp-validation.md))

Docker service definition added to `docker-compose.yml`:

```yaml
mcp-server:
  build:
    context: ./app/mcp_server  # Or ./services/mcp-server if TypeScript
    dockerfile: Dockerfile
  container_name: lightrag-cv-mcp
  environment:
    # Configuration via app.shared.config (if Python)
    MCP_PORT: ${MCP_PORT:-3000}
    MCP_PROTOCOL: ${MCP_PROTOCOL:-[FROM SPIKE]}  # http | sse | stdio
    LIGHTRAG_HOST: lightrag
    LIGHTRAG_PORT: 9621
    POSTGRES_HOST: postgres
    POSTGRES_PORT: 5432
    POSTGRES_DB: ${POSTGRES_DB:-lightrag_cv}
    POSTGRES_USER: ${POSTGRES_USER:-lightrag}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?error}
    LOG_LEVEL: ${LOG_LEVEL:-INFO}
  ports:
    - "${MCP_PORT:-3000}:3000"
  networks:
    - lightrag-network
  depends_on:
    lightrag:
      condition: service_healthy
  healthcheck:
    test: ["CMD-SHELL", "curl -f http://localhost:3000/health || exit 1"]
    interval: 30s
    timeout: 10s
    retries: 3
  restart: unless-stopped
```

**Environment Variables (.env):**

Add to `.env.example`:
```bash
# ========================================
# MCP Server Configuration
# ========================================
MCP_PORT=3000
MCP_PROTOCOL=[INSERT FROM SPIKE]  # http | sse | stdio
```

**Validation:**
- `docker-compose up mcp-server` starts successfully
- Service depends on `lightrag` service (starts after LightRAG is healthy)
- Environment variables correctly passed to container
- Health check endpoint responds

---

### AC4: MCP Server Starts Successfully

MCP server starts and exposes protocol endpoint:

1. **Startup Sequence:**
   - Configuration loaded from `app.shared.config` (Python) or environment (TypeScript)
   - LightRAG API endpoint configured: `http://lightrag:9621`
   - PostgreSQL connection string available (for future direct queries)
   - Server binds to `0.0.0.0:3000` (Docker internal)
   - Protocol handler initialized (from spike: http | sse | stdio)

2. **Startup Logs:**
   - Structured logging with context ([RULE 7](../architecture/coding-standards.md#rule-7))
   - Log MCP server version, SDK version, protocol
   - Log configuration (sanitized, no secrets - [RULE 8](../architecture/coding-standards.md#rule-8))
   - Log successful startup

3. **Health Check:**
   - `/health` endpoint responds with 200 OK
   - Returns server status, dependencies status

**Example Health Response:**
```json
{
  "status": "healthy",
  "server": "lightrag-cv-mcp",
  "version": "0.1.0",
  "protocol": "http",
  "dependencies": {
    "lightrag": "healthy",
    "postgres": "healthy"
  }
}
```

**Validation:**
- Server starts without errors
- Health check returns 200 OK
- Logs show successful initialization
- Server accessible from host: `curl http://localhost:3000/health`

---

### AC5: Basic Connectivity Test

Validate MCP server connectivity using MCP client or curl:

**Test 1: Health Check**
```bash
curl http://localhost:3000/health
```

Expected: 200 OK with health status JSON

**Test 2: Capability Negotiation** (if HTTP protocol)
```bash
curl -X POST http://localhost:3000/capabilities \
  -H "Content-Type: application/json"
```

Expected: MCP capabilities response

**Test 3: Tool Discovery**
```bash
# Format depends on protocol from spike
curl -X GET http://localhost:3000/tools  # (if HTTP)
```

Expected: Empty list `[]` or `{"tools": []}` (no tools yet)

**Test 4: Server Info/Status**
```bash
curl http://localhost:3000/status
```

Expected: Server information and protocol details

**Validation:**
- All connectivity tests pass
- Responses follow MCP specification format
- No server errors in logs
- Connection protocol works as identified in spike

---

### AC6: Documentation

Documentation added describing MCP server architecture and protocol flow:

**Document Location:**
- Primary: `/docs/architecture/mcp-server-implementation.md`
- (Not `/docs/mcp-server.md` - updated to match architecture docs pattern)

**Required Sections:**

1. **Architecture Overview**
   - MCP server role in LightRAG-CV system
   - Integration with OpenWebUI, LightRAG, PostgreSQL
   - Protocol selected (from spike) and rationale

2. **Technology Stack**
   - SDK selected (Python `mcp` or TypeScript SDK)
   - Dependencies and versions
   - Runtime requirements

3. **Project Structure**
   - Directory layout (`app/mcp_server/` or `services/mcp-server/`)
   - Module organization
   - Configuration management

4. **Protocol Flow**
   - OpenWebUI → MCP Server flow diagram
   - Tool discovery process
   - Tool invocation process
   - Error handling flow

5. **Configuration**
   - Environment variables
   - Using `app.shared.config` (if Python)
   - Docker configuration

6. **API Endpoints**
   - `/health` - Health check
   - `/capabilities` - MCP capabilities (if applicable)
   - `/tools` - Tool discovery
   - Tool invocation endpoint(s)
   - Error response format

7. **Development**
   - Running locally
   - Running in Docker
   - Testing procedures
   - Adding new tools (preview for Stories 3.2-3.3)

8. **Lessons Learned from Epic 2**
   - Use `app.shared.config` for configuration
   - Follow `app/` directory structure
   - Leverage `app.shared.llm_client` if LLM needed
   - Async functions for all I/O ([RULE 9](../architecture/coding-standards.md#rule-9))
   - Structured logging ([RULE 7](../architecture/coding-standards.md#rule-7))

**Validation:**
- Documentation complete and accurate
- Code examples provided
- Diagrams included (flow diagram minimum)
- References to technical spikes

---

## Prerequisites & Dependencies

### Technical Spikes (BLOCKERS)

**Must Complete Before Story 3.1:**

1. **OpenWebUI MCP Integration Validation**
   - Status: ⚠️ NOT STARTED
   - Document: [Technical Spike](../technical-spikes/openwebui-mcp-validation.md)
   - Deliverables:
     - OpenWebUI successfully connected to test MCP server
     - Connection protocol identified (http | sse | stdio)
     - Configuration approach documented

2. **MCP SDK Selection**
   - Status: ⚠️ NOT STARTED
   - Document: [Technical Spike](../technical-spikes/mcp-sdk-selection.md)
   - Deliverables:
     - SDK selected (Python `mcp` OR TypeScript SDK)
     - Decision rationale documented
     - Integration approach defined

**Estimated Spike Effort:** 12-18 hours total

### Story Dependencies

- **Depends On:**
  - ✅ Story 2.6 (LightRAG Knowledge Base Ingestion - CVs) - COMPLETE
  - ⚠️ Technical Spike: OpenWebUI MCP Integration - REQUIRED
  - ⚠️ Technical Spike: MCP SDK Selection - REQUIRED

- **Blocks:**
  - Story 3.2 (Core Search Tool - Profile Match Query)
  - Story 3.3 (Core Search Tool - Multi-Criteria Skill Search)

---

## Lessons Learned from Epic 2

**Apply These Patterns:**

1. **Project Structure** ([Source: Story 2.5, 2.6](story-2.6.md))
   - Use `app/` directory pattern if Python SDK selected
   - Structure: `app/mcp_server/`, `app/mcp_server/tools/`, `app/mcp_server/utils/`
   - Separate concerns: server.py (initialization), tools/ (tool implementations), utils/ (helpers)

2. **Configuration Management** ([RULE 2](../architecture/coding-standards.md#rule-2))
   - Use `app.shared.config` for all environment variables
   - Never hardcode configuration
   - Centralized settings management

3. **LLM Provider Abstraction**
   - If MCP server needs LLM interactions, use `app.shared.llm_client`
   - Supports Ollama, OpenAI, LiteLLM via configuration
   - Example: For query interpretation or tool parameter validation

4. **Async Functions** ([RULE 9](../architecture/coding-standards.md#rule-9))
   - All I/O operations must be async
   - Use `httpx.AsyncClient` for LightRAG API calls
   - Use `asyncpg` or `psycopg[async]` for PostgreSQL queries

5. **Structured Logging** ([RULE 7](../architecture/coding-standards.md#rule-7))
   ```python
   logger.info(
       "MCP server started",
       extra={
           "protocol": MCP_PROTOCOL,
           "port": MCP_PORT,
           "lightrag_api": LIGHTRAG_API_URL
       }
   )
   ```

6. **Error Handling** ([RULE 6](../architecture/coding-standards.md#rule-6))
   - Use custom exception classes
   - Never expose internal errors to clients
   - Log errors with context

7. **Docker Integration**
   - Health checks required
   - Depends on LightRAG service
   - Proper network configuration (`lightrag-network`)

---

## Technical Notes

### LightRAG API Integration

**Actual Endpoints** (from Epic 2 validation):

```python
# Document ingestion (not used in Story 3.1, but FYI for Stories 3.2-3.3)
POST http://lightrag:9621/documents/text

# Query (will be used in Stories 3.2-3.3)
POST http://lightrag:9621/query
{
  "query": "Find candidates with Python experience",
  "mode": "hybrid",  # naive | local | global | hybrid
  "top_k": 5,
  "filters": {"document_type": "CV"}
}

# Pipeline status (used for batch operations)
GET http://lightrag:9621/documents/pipeline_status

# Health
GET http://lightrag:9621/health
```

**Not Implemented in Story 3.1:**
- MCP server doesn't call LightRAG yet
- Tools (Stories 3.2-3.3) will make LightRAG API calls
- This story focuses on MCP protocol scaffolding

### PostgreSQL Access (Optional for Story 3.1)

**If Direct Database Queries Needed:**

```python
from app.shared.config import settings
import psycopg

# Connection string from app.shared.config
conn_string = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

# Example: Query document metadata
# (Not needed in Story 3.1, but available for Stories 3.2-3.3)
```

**Note:** Direct PostgreSQL access may be used in Stories 3.2-3.3, 3.8 for enhanced queries

---

## Story Status

- **Status**: ⚠️ **BLOCKED** - Awaiting Technical Spikes
- **Assigned To**: TBD
- **Estimated Effort**: 8-12 hours (after spikes complete)
- **Spike Effort**: 12-18 hours (must complete first)
- **Dependencies**:
  - ✅ Story 2.6 (LightRAG Knowledge Base Ingestion - CVs) - COMPLETE
  - ⚠️ Technical Spike: OpenWebUI MCP Integration - **REQUIRED**
  - ⚠️ Technical Spike: MCP SDK Selection - **REQUIRED**
- **Blocks**: Story 3.2, Story 3.3

---

## Testing Approach

### Manual Validation Tests

**Test 1: Docker Startup**
```bash
docker-compose up mcp-server
```
Expected: Clean startup, no errors

**Test 2: Health Check**
```bash
curl http://localhost:3000/health
```
Expected: 200 OK, health status JSON

**Test 3: Tool Discovery (Empty)**
```bash
# Command depends on protocol from spike
curl [MCP_TOOLS_ENDPOINT]
```
Expected: Empty tools list

**Test 4: Error Handling**
```bash
# Send invalid request
curl -X POST http://localhost:3000/invalid
```
Expected: MCP-compliant error response

### Integration Validation

- [ ] MCP server starts via docker-compose
- [ ] Health check passes
- [ ] OpenWebUI can connect to MCP server (from spike validation)
- [ ] Tool discovery returns empty list
- [ ] Logs show structured output
- [ ] No errors in startup or during tests

---

## Definition of Done

- [ ] Technical Spike: OpenWebUI MCP Integration - **COMPLETE**
- [ ] Technical Spike: MCP SDK Selection - **COMPLETE**
- [ ] All 6 Acceptance Criteria met
- [ ] MCP server starts successfully in Docker
- [ ] Health check endpoint functional
- [ ] Tool discovery returns empty list
- [ ] All connectivity tests pass
- [ ] Documentation complete ([docs/architecture/mcp-server-implementation.md](../architecture/mcp-server-implementation.md))
- [ ] Code follows [coding standards](../architecture/coding-standards.md) (RULE 1-10)
- [ ] Structured logging implemented (RULE 7)
- [ ] No security issues (RULE 8 - no sensitive data logged)
- [ ] QA assessment complete

---

## QA

- **QA Assessment**: [Story 3.1 Assessment](../qa/assessments/story-3.1-assessment.md)
- **QA Gate**: [Story 3.1 Gate](../qa/gates/story-3.1-gate.md)

---

**Navigation:**
- ← Previous: [Story 2.6](story-2.6.md)
- → Next: [Story 3.2](story-3.2.md)
- ↑ Epic: [Epic 3](../epics/epic-3.md)
