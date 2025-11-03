# Story 3.5: Natural Language Query Interpretation

> 📋 **Epic**: [Epic 3: MCP Server & OpenWebUI Integration](../epics/epic-3.md)
> 📋 **Architecture**: [Components - MCP Server](../architecture/components.md#component-3-mcp-server), [External APIs - Ollama](../architecture/external-apis.md)

## User Story

**As a** recruiter,
**I want** to ask questions in plain English without knowing tool names or parameters,
**so that** the system feels conversational and natural.

## Acceptance Criteria

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

## Story Status

- **Status**: Not Started
- **Assigned To**: TBD
- **Estimated Effort**: 6-8 hours
- **Dependencies**: Story 3.4 (OpenWebUI Configuration and MCP Integration)
- **Blocks**: Story 3.6

## QA

- **QA Assessment**: [Story 3.5 Assessment](../qa/assessments/story-3.5-assessment.md)
- **QA Gate**: [Story 3.5 Gate](../qa/gates/story-3.5-gate.md)

---

**Navigation:**
- ← Previous: [Story 3.4](story-3.4.md)
- → Next: [Story 3.6](story-3.6.md)
- ↑ Epic: [Epic 3](../epics/epic-3.md)
