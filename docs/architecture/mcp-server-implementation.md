# MCP Server Implementation

> Implementation reference for Story 3.1: MCP Server Scaffold and Protocol Implementation

## 1. Architecture Overview

### MCP Server Role

The MCP Server bridges LightRAG-CV capabilities with OpenWebUI through the Model Context Protocol (MCP), enabling AI assistants to access candidate search and retrieval tools.

**System Integration:**

```
┌─────────────┐
│  OpenWebUI  │
│  (MCP Client)│
└──────┬──────┘
       │ HTTP/OpenAPI
       ↓
┌─────────────────────────────────────┐
│         mcpo Proxy                  │
│  (HTTP → stdio bridge)              │
└──────┬──────────────────────────────┘
       │ stdio (stdin/stdout)
       ↓
┌─────────────────────────────────────┐
│    MCP Server (Python mcp SDK)      │
│  - Tool discovery                   │
│  - Tool invocation                  │
│  - Resource serving                 │
└──────┬──────────────────────────────┘
       │
       ├─→ LightRAG API (port 9621)
       │   - Query execution
       │   - Document retrieval
       │
       └─→ PostgreSQL (port 5432)
           - Metadata queries
           - Direct database access
```

### Protocol Architecture

**Transport Selection (Story 3.1):**
- **MCP Protocol**: stdio transport (standard input/output)
- **OpenWebUI Integration**: HTTP via mcpo (MCP-to-OpenAPI proxy)
- **Rationale**: OpenWebUI requires HTTP/OpenAPI endpoints, stdio MCP server is simpler to implement

**mcpo Proxy Bridge:**
- Wraps stdio MCP server and exposes HTTP/OpenAPI interface
- Handles protocol translation: HTTP requests → stdio → HTTP responses
- Provides OpenAPI documentation at `/docs`
- No custom HTTP handling needed in MCP server code

---

## 2. Technology Stack

### Core Technologies

**MCP Server:**
- **Language**: Python 3.11
- **MCP SDK**: `mcp==1.21.0` (Anthropic's official Python SDK)
- **Transport**: stdio (standard input/output communication)
- **HTTP Proxy**: mcpo (MCP-to-OpenAPI proxy)

**Dependencies:**
```python
# From app/requirements.txt
mcp==1.21.0              # MCP SDK for Story 3.1+
httpx==0.26.0            # Async HTTP client (for LightRAG API calls)
psycopg[binary]==3.1.16  # PostgreSQL client (async-capable)
```

**Runtime:**
- Python 3.11-slim base image
- mcpo installed via pip
- Docker containerized deployment

**Integration Points:**
- **LightRAG Service**: HTTP API at `http://lightrag:9621` (for Stories 3.2-3.3)
- **PostgreSQL**: Database connection via `app.shared.config.settings.postgres_dsn`
- **OpenWebUI**: MCP client consuming HTTP/OpenAPI endpoints

---

## 3. Project Structure

### Directory Layout

```
app/
└── mcp_server/
    ├── __init__.py        # Module initialization
    ├── server.py          # Main MCP server implementation
    ├── tools/             # Tool implementations (Stories 3.2-3.3)
    │   └── __init__.py
    └── utils/             # Helper functions and utilities
        └── __init__.py

services/
└── mcp-server/
    └── Dockerfile         # Docker image definition with mcpo
```

### Key Modules

**app/mcp_server/server.py** (Main Server)
- `LightRAGMCPServer` class: Core MCP server implementation
- Protocol handlers: `list_tools()`, `call_tool()`, `list_resources()`, `read_resource()`
- Server initialization and stdio transport setup
- Structured logging with context

**app/mcp_server/tools/** (Future - Stories 3.2-3.3)
- `search_by_profile.py` - Profile-based search tool (Story 3.2)
- `search_by_skills.py` - Multi-criteria skill search (Story 3.3)
- `get_candidate_details.py` - Candidate detail retrieval (Story 3.8)

**app/mcp_server/utils/** (Future)
- Query formatting helpers
- Response formatting and explanation generation
- LightRAG API client utilities

### Configuration Management

**Centralized Configuration** (RULE 2):
```python
from app.shared.config import settings

# All configuration accessed through settings
lightrag_url = settings.lightrag_url  # http://lightrag:9621
postgres_dsn = settings.postgres_dsn  # postgresql://...
```

**Environment Variables** (via app.shared.config):
```python
# Connection Configuration
LIGHTRAG_HOST: str = "lightrag"
LIGHTRAG_PORT: int = 9621
POSTGRES_HOST: str = "postgres"
POSTGRES_PORT: int = 5432
POSTGRES_DB: str = "lightrag_cv"
POSTGRES_USER: str = "lightrag"
POSTGRES_PASSWORD: str  # Required

# LLM Configuration (inherited from LightRAG service)
LLM_BINDING: str = "ollama"
LLM_BINDING_HOST: str
LLM_MODEL: str

# Logging
LOG_LEVEL: str = "INFO"
```

---

## 4. Protocol Flow

### Tool Discovery Flow

```
1. OpenWebUI: GET /tools (HTTP)
   ↓
2. mcpo: Translates to MCP list_tools request (stdio)
   ↓
3. MCP Server: @server.list_tools() handler
   ↓
4. Returns: list[Tool] from tools_registry
   ↓
5. mcpo: Translates to HTTP JSON response
   ↓
6. OpenWebUI: Receives tool schemas
```

**Story 3.1 Behavior:**
- `tools_registry = {}` (empty)
- Returns empty list `[]`
- Tools registered in Stories 3.2-3.3

### Tool Invocation Flow

```
1. OpenWebUI: POST /invoke {tool_name, arguments} (HTTP)
   ↓
2. mcpo: Translates to MCP call_tool request (stdio)
   ↓
3. MCP Server: @server.call_tool(name, arguments)
   ↓
4. Validate: Check tool exists in tools_registry
   ↓
5. Execute: await tool.execute(arguments)
   ↓
6. Format: Return list[TextContent] response
   ↓
7. mcpo: Translates to HTTP JSON response
   ↓
8. OpenWebUI: Receives tool output
```

**Story 3.1 Behavior:**
- No tools registered yet
- Returns error: "Tool not found"
- Execution implemented in Stories 3.2-3.3

### Resource Serving Flow

```
1. OpenWebUI: GET /resources (HTTP)
   ↓
2. mcpo: Translates to MCP list_resources request (stdio)
   ↓
3. MCP Server: @server.list_resources() handler
   ↓
4. Returns: ListResourcesResult with resources list
   ↓
5. mcpo: Translates to HTTP JSON response
   ↓
6. OpenWebUI: Receives resource URIs
```

**Story 3.1 Behavior:**
- `resources_registry = {}` (empty)
- Returns empty list
- Used in Epic 4 for match explanations

### Error Handling Flow

```
1. Error occurs in handler
   ↓
2. MCP Server: Catches exception
   ↓
3. Log error with context (RULE 7)
   ↓
4. Return: TextContent with error message
   ↓
5. mcpo: Translates to HTTP error response
   ↓
6. OpenWebUI: Receives error message
```

**Error Response Format:**
```python
TextContent(
    type="text",
    text=f"Tool '{name}' not found. No tools registered yet."
)
```

---

## 5. Configuration

### Environment Variables

**Docker Compose Configuration:**
```yaml
mcp-server:
  environment:
    # Connection Configuration (Docker internal network)
    LIGHTRAG_HOST: ${LIGHTRAG_HOST_DOCKER:-lightrag}
    LIGHTRAG_PORT: ${LIGHTRAG_PORT_DOCKER:-9621}
    POSTGRES_HOST: ${POSTGRES_HOST_DOCKER:-postgres}
    POSTGRES_PORT: ${POSTGRES_PORT_DOCKER:-5432}
    POSTGRES_DB: ${POSTGRES_DB:-lightrag_cv}
    POSTGRES_USER: ${POSTGRES_USER:-lightrag}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?error}

    # LLM Configuration
    LLM_BINDING: ${LLM_BINDING:-ollama}
    LLM_BINDING_HOST: ${LLM_BINDING_HOST:-http://host.docker.internal:11434}
    LLM_MODEL: ${LLM_MODEL:-qwen2.5:7b-instruct-q4_K_M}
    LLM_BINDING_API_KEY: ${LLM_BINDING_API_KEY:-}

    # Embedding Configuration
    EMBEDDING_BINDING: ${EMBEDDING_BINDING:-ollama}
    EMBEDDING_BINDING_HOST: ${EMBEDDING_BINDING_HOST:-http://host.docker.internal:11434}
    EMBEDDING_MODEL: ${EMBEDDING_MODEL:-bge-m3:latest}
    EMBEDDING_DIM: ${EMBEDDING_DIM:-1024}

    # Logging
    LOG_LEVEL: ${LOG_LEVEL:-INFO}
```

**Host Environment (.env):**
```bash
# MCP Server Configuration
MCP_PORT=3001  # Host port mapping

# Connection defaults (overridden in docker-compose for internal network)
LIGHTRAG_HOST=localhost
LIGHTRAG_PORT=9621
POSTGRES_HOST=localhost
POSTGRES_PORT=5434
```

### Configuration Access Pattern

**Using app.shared.config (RULE 2):**
```python
from app.shared.config import settings

# Configuration loaded automatically from environment
logger.info(
    f"MCP server initialized (lightrag_url={settings.lightrag_url}, "
    f"postgres_host={settings.POSTGRES_HOST})"
)

# LightRAG API calls (Stories 3.2-3.3)
async with httpx.AsyncClient() as client:
    response = await client.post(
        f"{settings.lightrag_url}/query",
        json={"query": query, "mode": "hybrid"}
    )

# PostgreSQL connection (Stories 3.2-3.3)
conn_string = settings.postgres_dsn
async with await psycopg.AsyncConnection.connect(conn_string) as conn:
    # Direct database queries
    pass
```

---

## 6. API Endpoints

### mcpo Proxy Endpoints

**Health Check:**
```bash
GET http://localhost:3000/docs
```
Response: OpenAPI documentation UI (200 OK indicates healthy)

**OpenAPI Specification:**
```bash
GET http://localhost:3000/openapi.json
```
Response: Full OpenAPI 3.x specification for MCP server tools

**Tool Discovery:**
```bash
POST http://localhost:3000/list_tools
```
Response:
```json
{
  "tools": []
}
```

**Tool Invocation:**
```bash
POST http://localhost:3000/call_tool
Content-Type: application/json

{
  "name": "tool_name",
  "arguments": {}
}
```
Response (Story 3.1 - no tools):
```json
{
  "content": [
    {
      "type": "text",
      "text": "Tool 'tool_name' not found. No tools are registered yet (Story 3.1 scaffold)."
    }
  ]
}
```

**Resource Discovery:**
```bash
POST http://localhost:3000/list_resources
```
Response:
```json
{
  "resources": []
}
```

### Internal MCP Protocol

**stdio Transport:**
- Communication via stdin/stdout
- JSON-RPC messages
- Handled automatically by mcp SDK
- mcpo proxy bridges to HTTP

**Example MCP Message (stdio):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

---

## 7. Development

### Running Locally (Development)

**Prerequisites:**
- Python 3.11+
- PostgreSQL running (port 5432 or configured)
- LightRAG service running (port 9621)
- Environment variables set

**Setup:**
```bash
# Install dependencies
pip install -r app/requirements.txt

# Install mcpo for testing
pip install mcpo

# Set environment variables
export LIGHTRAG_HOST=localhost
export LIGHTRAG_PORT=9621
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5434
export POSTGRES_PASSWORD=lightrag_dev_2024
export LOG_LEVEL=INFO
```

**Run MCP Server (stdio mode):**
```bash
# Direct execution (stdio transport)
python3 -m app.mcp_server.server
```

**Run with mcpo Proxy (HTTP mode):**
```bash
# Wrap stdio server with mcpo for HTTP/OpenAPI
mcpo --host localhost --port 3000 -- python3 -m app.mcp_server.server
```

**Test Health:**
```bash
curl http://localhost:3000/docs
# Expected: 200 OK with OpenAPI documentation UI
```

### Running in Docker

**Build and Start:**
```bash
# Build specific service
docker-compose build mcp-server

# Start with dependencies
docker-compose up -d postgres lightrag
docker-compose up mcp-server

# Check logs
docker-compose logs -f mcp-server
```

**Expected Startup Logs:**
```
INFO - MCP server initialized: lightrag-cv-mcp v0.1.0 (transport=stdio, lightrag_url=http://lightrag:9621)
INFO - Initializing LightRAG-CV MCP Server v0.1.0 (transport=stdio, lightrag_url=http://lightrag:9621, postgres=postgres:5432/lightrag_cv)
INFO - MCP server started successfully (transport=stdio, lightrag_url=http://lightrag:9621, postgres_host=postgres)
INFO:     Uvicorn running on http://0.0.0.0:3000 (Press CTRL+C to quit)
```

**Health Check:**
```bash
# From host
curl http://localhost:3001/docs  # MCP_PORT from .env

# From within Docker network
docker exec lightrag-cv-mcp curl http://localhost:3000/docs
```

**Expected Response:**
- HTTP 200 OK
- OpenAPI documentation interface
- Lists available MCP endpoints

### Testing Procedures

**Test 1: Container Startup**
```bash
docker-compose up mcp-server
# Expected: Clean startup, no errors
```

**Test 2: Health Check**
```bash
curl http://localhost:3001/docs
# Expected: 200 OK, OpenAPI UI
```

**Test 3: Tool Discovery**
```bash
curl -X POST http://localhost:3001/list_tools \
  -H "Content-Type: application/json"
# Expected: {"tools": []}
```

**Test 4: Tool Invocation (Error Case)**
```bash
curl -X POST http://localhost:3001/call_tool \
  -H "Content-Type: application/json" \
  -d '{"name": "nonexistent_tool", "arguments": {}}'
# Expected: Error message about tool not found
```

**Test 5: Logs Validation**
```bash
docker-compose logs mcp-server | grep "MCP server started successfully"
# Expected: Startup log with configuration details
```

### Adding New Tools (Preview for Stories 3.2-3.3)

**Tool Implementation Pattern:**

```python
# app/mcp_server/tools/search_by_profile.py
from mcp.types import Tool

# Define tool schema
TOOL_SCHEMA = Tool(
    name="search_by_profile",
    description="Find candidates matching a CIGREF IT profile",
    inputSchema={
        "type": "object",
        "properties": {
            "profile_name": {"type": "string"},
            "top_k": {"type": "integer", "default": 5}
        },
        "required": ["profile_name"]
    }
)

# Tool execution function
async def execute(arguments: dict) -> list[TextContent]:
    # Call LightRAG API
    # Format response
    # Return results
    pass
```

**Register Tool in server.py:**
```python
from app.mcp_server.tools import search_by_profile

class LightRAGMCPServer:
    def __init__(self):
        self.tools_registry = {
            "search_by_profile": search_by_profile.TOOL_SCHEMA
        }
        # Tool execution happens in call_tool() handler
```

---

## 8. Lessons Learned from Epic 2

### Applied Best Practices

**1. Centralized Configuration (RULE 2)**
- ✅ All configuration via `app.shared.config`
- ✅ No hardcoded values
- ✅ Environment variable defaults
- ❌ Avoided: Custom config.py files

**2. Project Structure**
- ✅ Python SDK → `app/mcp_server/` directory
- ✅ Consistent with existing `app/` pattern
- ✅ Modular organization: server, tools, utils
- ✅ Proper `__init__.py` files

**3. Async Functions (RULE 9)**
- ✅ All I/O operations use async/await
- ✅ `async def` for all handlers
- ✅ `httpx.AsyncClient` for HTTP calls
- ✅ `psycopg.AsyncConnection` for database

**4. Structured Logging (RULE 7)**
```python
logger.info(
    f"Tool invocation requested (tool_name={name}, has_arguments={bool(arguments)})"
)

logger.warning(
    f"Tool not found: {name} (available_tools={list(self.tools_registry.keys())})"
)

logger.error(
    f"MCP server error (error_type={type(e).__name__}, error_message={str(e)})",
    exc_info=True
)
```

**5. Security (RULE 8)**
- ✅ No passwords in logs
- ✅ Connection strings sanitized
- ✅ Only log non-sensitive configuration
```python
# Good: Log postgres host without credentials
postgres_info = settings.postgres_dsn.split("@")[1] if "@" in settings.postgres_dsn else "N/A"
logger.info(f"postgres={postgres_info}")
```

**6. Error Handling (RULE 6)**
- ✅ Custom exception classes (future)
- ✅ MCP-compliant error responses
- ✅ Contextual error logging
- ✅ No internal errors exposed to clients

**7. Docker Integration**
- ✅ Health checks implemented
- ✅ Depends on LightRAG service
- ✅ Connected to `lightrag-network`
- ✅ Proper startup ordering

**8. stdio vs HTTP Decision**
- ✅ stdio MCP server (simpler implementation)
- ✅ mcpo proxy for HTTP/OpenAPI (OpenWebUI requirement)
- ✅ Single-process deployment (mcpo wraps server)
- ✅ No custom HTTP handling needed

### Avoided Antipatterns

**From Epic 2 Experience:**
- ❌ Custom config files → Use `app.shared.config`
- ❌ Synchronous I/O → Use async/await
- ❌ Hardcoded URLs → Use environment variables
- ❌ Plain string logging → Use structured context
- ❌ Exposing errors → Use generic messages

---

## Technical Decisions Record

### Decision 1: Python mcp SDK vs TypeScript SDK

**Selected:** Python `mcp==1.21.0`

**Rationale:**
- Consistent with existing Python 3.11 codebase
- Direct access to `app.shared.config` and `app.shared.llm_client`
- No additional Node.js runtime needed
- Simpler deployment (single language stack)

**References:**
- [Technical Spike: MCP SDK Selection](../technical-spikes/mcp-sdk-selection.md)

### Decision 2: stdio Transport with mcpo Proxy

**Selected:** stdio MCP server wrapped with mcpo (HTTP/OpenAPI proxy)

**Rationale:**
- OpenWebUI requires HTTP/OpenAPI endpoints
- stdio transport simplest for MCP SDK
- mcpo handles protocol translation automatically
- Single-process deployment in Docker

**Alternative Considered:**
- Direct HTTP MCP implementation: More complex, requires custom HTTP handling

**References:**
- [Technical Spike: OpenWebUI MCP Validation](../technical-spikes/openwebui-mcp-validation.md)

### Decision 3: Project Structure Location

**Selected:** `app/mcp_server/` directory

**Rationale:**
- Consistent with existing `app/` pattern
- Python code co-located with shared modules
- Direct imports of `app.shared.config` and utilities
- Aligns with lessons from Epic 2

**Alternative Considered:**
- `services/mcp-server/`: Separate service, but unnecessary separation for Python code

---

## Story Implementation Status

**Story 3.1: Complete ✅**

**Implemented:**
- ✅ AC1: MCP Server with Python mcp SDK
- ✅ AC2: Protocol fundamentals (initialization, tool discovery, invocation, resources)
- ✅ AC3: Docker configuration with `services/mcp-server/Dockerfile`
- ✅ AC4: Server startup with health check
- ✅ AC5: Connectivity tests passing
- ✅ AC6: Documentation complete (this file)

**Next Stories:**
- Story 3.2: Implement `search_by_profile` tool
- Story 3.3: Implement `search_by_skills` tool
- Story 3.8: Implement `get_candidate_details` tool

---

## References

- **Technical Spikes:**
  - [MCP SDK Selection](../technical-spikes/mcp-sdk-selection.md)
  - [OpenWebUI MCP Integration Validation](../technical-spikes/openwebui-mcp-validation.md)

- **Architecture Documents:**
  - [Components - MCP Server](components.md#component-3-mcp-server)
  - [Coding Standards](coding-standards.md)
  - [Infrastructure and Deployment](infrastructure-and-deployment.md)

- **Stories:**
  - [Story 3.1: MCP Server Scaffold](../stories/story-3.1.md)
  - [Story 3.2: Core Search Tool - Profile Match](../stories/story-3.2.md)
  - [Story 3.3: Core Search Tool - Multi-Criteria Skills](../stories/story-3.3.md)

- **External Resources:**
  - [Anthropic MCP SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
  - [mcpo (MCP-to-OpenAPI proxy)](https://pypi.org/project/mcpo/)
  - [Model Context Protocol Specification](https://modelcontextprotocol.io/)
