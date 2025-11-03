# Story 3.4: OpenWebUI Configuration and MCP Integration

> 📋 **Epic**: [Epic 3: MCP Server & OpenWebUI Integration](../epics/epic-3.md)
> 📋 **Architecture**: [Components - MCP Server](../architecture/components.md#component-3-mcp-server), [External APIs](../architecture/external-apis.md)

## User Story

**As a** recruiter,
**I want** OpenWebUI connected to the MCP server and able to discover LightRAG-CV tools,
**so that** I can interact with the system through a conversational chat interface.

## Acceptance Criteria

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

## Story Status

- **Status**: Not Started
- **Assigned To**: TBD
- **Estimated Effort**: 8-12 hours
- **Dependencies**: Story 3.2 (Core Search Tool - Profile Match Query), Story 3.3 (Core Search Tool - Multi-Criteria Skill Search)
- **Blocks**: Story 3.5, Story 3.6

## QA

- **QA Assessment**: [Story 3.4 Assessment](../qa/assessments/story-3.4-assessment.md)
- **QA Gate**: [Story 3.4 Gate](../qa/gates/story-3.4-gate.md)

---

**Navigation:**
- ← Previous: [Story 3.3](story-3.3.md)
- → Next: [Story 3.5](story-3.5.md)
- ↑ Epic: [Epic 3](../epics/epic-3.md)
