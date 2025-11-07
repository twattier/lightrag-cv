# Story 3.1: MCP Server Scaffold and Protocol Implementation

> 📋 **Epic**: [Epic 3: MCP Server & OpenWebUI Integration](../epics/epic-3.md)
> 📋 **Architecture**: [Components - MCP Server](../architecture/components.md#component-3-mcp-server), [Infrastructure and Deployment](../architecture/infrastructure-and-deployment.md)

## User Story

**As a** developer,
**I want** MCP server skeleton implementing the Model Context Protocol specification,
**so that** I can expose tools and resources to MCP-compatible clients like OpenWebUI.

## Acceptance Criteria

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

## Story Status

- **Status**: Not Started
- **Assigned To**: TBD
- **Estimated Effort**: 8-12 hours
- **Dependencies**: Story 2.6 (LightRAG Knowledge Base Ingestion - CVs)
- **Blocks**: Story 3.2, Story 3.3

## QA

- **QA Assessment**: [Story 3.1 Assessment](../qa/assessments/story-3.1-assessment.md)
- **QA Gate**: [Story 3.1 Gate](../qa/gates/story-3.1-gate.md)

---

**Navigation:**
- ← Previous: [Story 2.6](story-2.6.md)
- → Next: [Story 3.2](story-3.2.md)
- ↑ Epic: [Epic 3](../epics/epic-3.md)
