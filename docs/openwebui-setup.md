# OpenWebUI Setup for LightRAG-CV

> **Purpose**: Configure OpenWebUI to connect to the MCP server and enable conversational candidate search.

## Prerequisites

### Required Services

| Service | Version | Status Check | Port |
|---------|---------|--------------|------|
| **OpenWebUI** | v0.6.31+ | `curl -s http://localhost:8080/api/version` | 8080 |
| **MCP Server** | v0.1.0 | `docker ps --filter name=lightrag-cv-mcp` | 3001 |
| **LightRAG** | - | `curl -s http://localhost:9621/health` | 9621 |

### Verify Prerequisites

```bash
# 1. Check OpenWebUI is running
docker ps --filter name=open-webui --format "{{.Names}}\t{{.Status}}"
# Expected: open-webui  Up X minutes (healthy)

# 2. Check OpenWebUI version (requires v0.6.31+)
curl -s http://localhost:8080/api/version
# Expected: {"version":"0.6.34"}

# 3. Verify MCP server and both tools registered
docker-compose logs mcp-server 2>&1 | grep "MCP server initialized" | tail -1
# Expected: tools_registered=['search_by_profile', 'search_by_skills']

# 4. Verify mcpo proxy is accessible
curl -s http://localhost:3001/docs | head -5
# Expected: HTML with Swagger UI

# 5. Verify tools in OpenAPI spec
curl -s http://localhost:3001/openapi.json | python3 -c "import json, sys; data=json.load(sys.stdin); print('Tools:', list(data.get('paths', {}).keys()))"
# Expected: Tools: ['/search_by_profile', '/search_by_skills']
```

---

## Configuration Steps

### Step 1: Access OpenWebUI Admin Settings

1. Navigate to OpenWebUI: **http://localhost:8080**
2. Log in with admin credentials
3. Click **profile icon** (top right corner)
4. Select **Settings** from dropdown menu
5. Navigate to **Admin Settings** section
6. Click on **External Tools** tab

### Step 2: Add MCP Server as External Tool

Click **"+ Add Server"** or **"Add Tool"** button and configure:

#### Configuration Fields

```yaml
Name:
  Value: "LightRAG-CV MCP Server"
  Purpose: Display name in OpenWebUI tools list

Type:
  Value: "OpenAPI"
  Note: mcpo proxy exposes HTTP/OpenAPI interface

URL/Endpoint:
  Primary: "http://host.docker.internal:3001"
  Alternative Options:
    - "http://mcp-server:3000" (if OpenWebUI in same Docker network)
    - "http://localhost:3001" (if OpenWebUI running on host, not in Docker)

Authentication:
  Value: None
  Note: POC mode - no authentication required
  Future: OAuth 2.1 available for production

Description (Optional):
  Value: "Candidate search tools powered by LightRAG-CV knowledge graph"
```

#### Connection URL Selection

Choose the appropriate URL based on your OpenWebUI deployment:

| OpenWebUI Deployment | Recommended URL | Notes |
|---------------------|-----------------|-------|
| Docker container (separate network) | `http://host.docker.internal:3001` | Access host from container |
| Docker container (same network) | `http://mcp-server:3000` | Internal Docker DNS |
| Host (no container) | `http://localhost:3001` | Direct localhost access |

### Step 3: Verify Connection

After clicking **Save**, OpenWebUI will:

1. ✅ Query the OpenAPI specification from mcpo proxy
2. ✅ Discover available MCP tools automatically
3. ✅ Display tools in the External Tools list
4. ✅ Show connection status

**Expected Success Indicators:**
- Connection status shows "Connected" or "Active"
- No error messages displayed
- Tools appear in tools list (see Step 4)

---

## Tool Discovery Verification

### Verify in OpenWebUI UI

**Navigation**: Settings → External Tools → [LightRAG-CV MCP Server]

**Expected Tools List:**

#### 1. search_by_profile

**Description**: "Find candidates matching a CIGREF IT profile"

**Parameters**:
- `profile_name` (string, required) - CIGREF job profile name
- `experience_years` (number, optional) - Minimum years of experience
- `top_k` (number, optional, default: 5) - Number of results to return

**Example Usage**: "Find Cloud Architects with 5+ years experience"

#### 2. search_by_skills

**Description**: "Find candidates with specific technical skills"

**Parameters**:
- `required_skills` (array, required) - Must-have skills
- `preferred_skills` (array, optional) - Nice-to-have skills
- `experience_level` (string, optional) - "junior", "mid", or "senior"
- `top_k` (number, optional, default: 5) - Number of results to return

**Example Usage**: "Show me Python developers with Docker and Kubernetes"

### Verify via Command Line

```bash
# Test OpenAPI spec includes both tools
curl -s http://localhost:3001/openapi.json | \
  python3 -c "import json, sys; data=json.load(sys.stdin); print(json.dumps(list(data['paths'].keys()), indent=2))"

# Expected output:
[
  "/search_by_profile",
  "/search_by_skills"
]
```

**Verification Checklist:**
- [ ] Both tools appear in External Tools list
- [ ] Tool descriptions are clear and actionable
- [ ] Parameter types and requirements visible
- [ ] Optional vs required parameters marked correctly

---

## Testing Tool Invocation

### Test Queries

Create a new chat in OpenWebUI and try these queries:

#### Profile-Based Search Tests

```markdown
1. "Find Cloud Architects"
   Expected Tool: search_by_profile
   Expected Params: {profile_name: "Cloud Architect"}

2. "Show me Digital Transformation Managers"
   Expected Tool: search_by_profile
   Expected Params: {profile_name: "Digital Transformation Manager"}

3. "Search for DevOps Engineers with 3+ years experience"
   Expected Tool: search_by_profile
   Expected Params: {profile_name: "DevOps Engineer", experience_years: 3}
```

#### Skill-Based Search Tests

```markdown
4. "Show me Python developers"
   Expected Tool: search_by_skills
   Expected Params: {required_skills: ["Python"]}

5. "Find candidates with Kubernetes and Docker"
   Expected Tool: search_by_skills
   Expected Params: {required_skills: ["Kubernetes", "Docker"]}

6. "Senior engineers with AWS and Terraform experience"
   Expected Tool: search_by_skills
   Expected Params: {required_skills: ["AWS", "Terraform"], experience_level: "senior"}
```

#### Multi-Turn Conversation Test

```markdown
Initial: "Find senior DevOps engineers"
Follow-up: "Who has AWS certification?"
Follow-up: "Show me the top 3"

Expected: Context maintained, refined results at each step
```

#### Error Handling Tests

```markdown
7. "Find candidates for XYZ Profile"
   Expected: Error message about invalid profile

8. "Show me COBOL experts"
   Expected: "No candidates found" with helpful suggestions
```

### Expected Chat Output Format

```
[Tool Call: search_by_profile]
Parameters: {"profile_name": "Cloud Architect", "experience_years": 5}

Results:
1. Candidate cv_013 (Bansi Vasoya) - Match Score: 0.87
   Skills: Python, AWS, Kubernetes, Docker
   Experience: Senior level
   Match Reason: Strong cloud infrastructure expertise...

2. [Additional candidates...]

Found 5 candidates matching Cloud Architect profile.
```

### Success Criteria

- [ ] At least 3 different test queries successful
- [ ] Correct tool selected for each query type
- [ ] Parameters extracted accurately from natural language
- [ ] Results displayed clearly in chat
- [ ] Response time < 5 seconds per query
- [ ] Multi-turn conversation maintains context

### Monitor Tool Invocations

Check MCP server logs to verify tool calls:

```bash
# Monitor tool invocations in real-time
docker-compose logs -f mcp-server | grep "call_tool"

# Expected log entries:
# INFO - Tool invocation requested (tool_name=search_by_profile, has_arguments=True)
# INFO - Tool execution successful (tool_name=search_by_profile, execution_time_ms=450)
```

---

## Troubleshooting

### Problem: Tools Not Appearing in OpenWebUI

**Symptoms**: External Tools list is empty after adding server

**Solutions**:

1. **Verify mcpo proxy is running and accessible**:
   ```bash
   curl http://localhost:3001/docs
   # Should return Swagger UI HTML
   ```

2. **Check OpenWebUI logs for connection errors**:
   ```bash
   docker logs open-webui 2>&1 | grep -i error | tail -20
   ```

3. **Verify URL is correct**:
   - Try alternative URLs: `http://localhost:3001` or `http://mcp-server:3000`
   - Ensure port `:3001` is included in URL

4. **Restart OpenWebUI container**:
   ```bash
   docker restart open-webui
   # Wait 30 seconds, then retry adding server
   ```

---

### Problem: Connection Refused

**Symptoms**: "Failed to connect to server" error when adding tool

**Solutions**:

1. **Check MCP server is running**:
   ```bash
   docker ps | grep mcp
   # Should show lightrag-cv-mcp with status "Up"
   ```

2. **Verify port 3001 is accessible**:
   ```bash
   netstat -an | grep 3001
   # Or: lsof -i :3001
   ```

3. **Check Docker network connectivity**:
   ```bash
   # If OpenWebUI in Docker, test from inside container
   docker exec open-webui curl -s http://host.docker.internal:3001/docs | head -5
   ```

4. **Verify firewall not blocking port**:
   ```bash
   sudo ufw status | grep 3001
   # Ensure port 3001 is allowed
   ```

---

### Problem: Tool Invocation Fails

**Symptoms**: Error in chat after query, tool doesn't execute

**Solutions**:

1. **Check LightRAG service is healthy**:
   ```bash
   docker-compose ps lightrag
   curl -s http://localhost:9621/health
   ```

2. **Review mcpo proxy logs**:
   ```bash
   docker logs lightrag-cv-mcp --tail 50
   # Look for error messages or stack traces
   ```

3. **Test tool directly via mcpo**:
   ```bash
   curl -X POST http://localhost:3001/search_by_profile \
     -H "Content-Type: application/json" \
     -d '{"profile_name": "Cloud Architect", "top_k": 3}'
   ```

4. **Restart MCP server**:
   ```bash
   docker-compose restart mcp-server
   # Wait for "MCP server initialized" in logs
   ```

---

### Problem: Poor Query Interpretation

**Symptoms**: Wrong tool selected or incorrect parameters extracted

**Solutions**:

1. **Use more explicit queries**:
   - Instead of: "Show me architects"
   - Try: "Find Cloud Architects" (mentions specific profile)

2. **Check LLM model version**:
   ```bash
   # Verify OpenWebUI is using qwen2.5:7b-instruct-q4_K_M or better
   # Navigate to: Settings → Models → Chat Model
   ```

3. **Configure system prompt** (Optional):

   Navigate to: Settings → Models → [Your Model] → System Prompt

   Add the following:
   ```markdown
   You are a helpful recruitment assistant with access to candidate search tools.

   Available Tools:
   1. search_by_profile - Use for job role queries (e.g., "Cloud Architect", "DevOps Engineer")
   2. search_by_skills - Use for technology/skill queries (e.g., "Python", "Kubernetes")

   When a user asks about candidates:
   - For job roles/profiles: Use search_by_profile
   - For specific skills/technologies: Use search_by_skills

   Always invoke the appropriate tool and format results clearly with:
   - Candidate names/IDs
   - Relevant skills
   - Experience level
   - Match explanation
   ```

4. **Review tool descriptions**:
   - Ensure tool descriptions in MCP server are clear
   - Check `/app/mcp_server/tools/*.py` files

---

### Problem: Timeout Errors

**Symptoms**: Query hangs or times out without results

**Solutions**:

1. **Check LightRAG query performance**:
   ```bash
   # Monitor LightRAG logs for slow queries
   docker-compose logs lightrag --tail 50 | grep "query_time_ms"
   ```

2. **Verify Ollama models are loaded**:
   ```bash
   curl -s http://localhost:11434/api/tags
   # Should show qwen2.5:7b-instruct-q4_K_M and bge-m3
   ```

3. **Increase timeout if needed**:
   - Edit `/app/mcp_server/tools/*.py`
   - Increase `self.timeout = httpx.Timeout(60.0)` to higher value

4. **Check database performance**:
   ```bash
   docker-compose ps postgres
   docker stats lightrag-cv-postgres --no-stream
   ```

---

## Architecture Diagram

### Integration Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Query (OpenWebUI Chat)                  │
│                  "Find Cloud Architects with 5+ years"          │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│              OpenWebUI LLM (qwen2.5:7b-instruct-q4_K_M)         │
│              Interprets query, selects tool, extracts params    │
└────────────────────────────────┬────────────────────────────────┘
                                 │ HTTP POST
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                  mcpo Proxy (port 3001)                         │
│                  Translates OpenAPI ↔ MCP Protocol              │
└────────────────────────────────┬────────────────────────────────┘
                                 │ stdio (stdin/stdout)
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│              MCP Server (app/mcp_server/server.py)              │
│              Executes tool logic, formats response              │
└────────────────────────────────┬────────────────────────────────┘
                                 │ HTTP POST
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│              LightRAG API (port 9621)                           │
│              Performs hybrid retrieval (vector + graph)         │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│          PostgreSQL + pgvector + Apache AGE                     │
│          Knowledge graph + vector embeddings                    │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ↓ Results
┌─────────────────────────────────────────────────────────────────┐
│              Results formatted and returned via chain           │
│         MCP → mcpo → OpenWebUI → Displayed in Chat             │
└─────────────────────────────────────────────────────────────────┘
```

### Component Details

| Component | Technology | Port | Protocol | Purpose |
|-----------|-----------|------|----------|---------|
| **OpenWebUI** | Docker | 8080 | HTTP | User interface, LLM orchestration |
| **mcpo Proxy** | Python | 3001 | HTTP/OpenAPI | Protocol bridge (OpenAPI ↔ MCP) |
| **MCP Server** | Python mcp SDK | - | stdio | Tool execution, response formatting |
| **LightRAG** | FastAPI | 9621 | HTTP | Hybrid RAG retrieval |
| **PostgreSQL** | PostgreSQL 16 | 5432 | PostgreSQL | Data storage (vectors + graph) |
| **Ollama** | Ollama | 11434 | HTTP | LLM inference (embeddings + generation) |

---

## Example Queries and Expected Results

### Example 1: Profile-Based Search

**Query**: "Find Cloud Architects with 5+ years experience"

**Tool Selected**: `search_by_profile`

**Parameters**:
```json
{
  "profile_name": "Cloud Architect",
  "experience_years": 5,
  "top_k": 5
}
```

**Expected Result**: 3-5 candidates with cloud architecture experience, senior level, 5+ years

---

### Example 2: Skill-Based Search

**Query**: "Show me Python developers with Docker and Kubernetes"

**Tool Selected**: `search_by_skills`

**Parameters**:
```json
{
  "required_skills": ["Python", "Docker", "Kubernetes"],
  "top_k": 5
}
```

**Expected Result**: Candidates with Python + Docker + Kubernetes skills, semantic matching applied

---

### Example 3: Multi-Criteria Search

**Query**: "Senior engineers with AWS and Terraform experience"

**Tool Selected**: `search_by_skills`

**Parameters**:
```json
{
  "required_skills": ["AWS", "Terraform"],
  "experience_level": "senior",
  "top_k": 5
}
```

**Expected Result**: Senior-level candidates with AWS + Terraform expertise

---

## System Prompt Configuration (Optional)

### Purpose

Improve query interpretation accuracy by giving the LLM explicit instructions about tool selection.

### Location

Settings → Models → [Select Model] → System Prompt

### Recommended Prompt

```markdown
You are a helpful recruitment assistant with access to candidate search tools.

## Available Tools

1. **search_by_profile** - Find candidates matching specific job roles
   - Use when user mentions job titles or roles
   - Examples: "Cloud Architect", "DevOps Engineer", "Data Scientist"
   - Parameters: profile_name (required), experience_years (optional)

2. **search_by_skills** - Find candidates with specific technical skills
   - Use when user asks about technologies or skill combinations
   - Examples: "Python", "Kubernetes", "AWS", "Machine Learning"
   - Parameters: required_skills (array), preferred_skills (array), experience_level (optional)

## Query Interpretation Guidelines

- Profile queries: "Find [JobTitle]" → use search_by_profile
- Skill queries: "Developers with [Technology]" → use search_by_skills
- Multi-criteria: "Senior [Skills]" → use search_by_skills with experience_level
- Always extract parameters accurately from natural language
- If ambiguous, prefer search_by_skills (broader matching)

## Response Guidelines

- Display candidate results with clear formatting
- Include match scores and reasons when available
- If no results, suggest broadening search criteria
- For multi-turn conversations, maintain context and refine searches
```

---

## Health Check Script

Save this script to verify all components are healthy:

```bash
#!/bin/bash
# File: scripts/check-openwebui-integration.sh

echo "=== OpenWebUI Integration Health Check ==="
echo

echo "1. OpenWebUI Status:"
curl -s http://localhost:8080/api/version && echo " ✓ OpenWebUI running"
echo

echo "2. MCP Server Status:"
docker ps --filter name=lightrag-cv-mcp --format "{{.Status}}" | grep -q "Up" && echo " ✓ MCP server running"
echo

echo "3. mcpo Proxy Status:"
curl -s http://localhost:3001/docs > /dev/null && echo " ✓ mcpo proxy accessible"
echo

echo "4. Tools Registered:"
docker-compose logs mcp-server 2>&1 | grep "MCP server initialized" | tail -1
echo

echo "5. OpenAPI Endpoints:"
curl -s http://localhost:3001/openapi.json | python3 -c "import json, sys; data=json.load(sys.stdin); print('Tools:', list(data['paths'].keys()))"
echo

echo "6. LightRAG API:"
curl -s http://localhost:9621/health > /dev/null && echo " ✓ LightRAG API healthy"
echo

echo "=== Health Check Complete ==="
```

**Usage**:
```bash
chmod +x scripts/check-openwebui-integration.sh
./scripts/check-openwebui-integration.sh
```

---

## Additional Resources

- **Technical Spike**: [OpenWebUI MCP Validation](technical-spikes/openwebui-mcp-validation.md)
- **MCP Server Implementation**: [docs/architecture/mcp-server-implementation.md](architecture/mcp-server-implementation.md)
- **Story 3.4**: [docs/stories/story-3.4.md](stories/story-3.4.md)
- **Epic 3**: [docs/epics/epic-3.md](epics/epic-3.md)

---

**Document Version**: 1.0
**Last Updated**: 2025-11-09
**Author**: James (Developer Agent)
**Status**: Story 3.4 - OpenWebUI Configuration Complete
