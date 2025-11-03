# Story 3.6: Conversational Query Refinement

> 📋 **Epic**: [Epic 3: MCP Server & OpenWebUI Integration](../epics/epic-3.md)
> 📋 **Architecture**: [Components - MCP Server](../architecture/components.md#component-3-mcp-server), [External APIs - Ollama](../architecture/external-apis.md)

## User Story

**As a** recruiter,
**I want** to refine my search with follow-up questions in the same chat session,
**so that** I can iteratively narrow results without starting over.

## Acceptance Criteria

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

## Story Status

- **Status**: Not Started
- **Assigned To**: TBD
- **Estimated Effort**: 6-8 hours
- **Dependencies**: Story 3.5 (Natural Language Query Interpretation)
- **Blocks**: Story 3.7

## QA

- **QA Assessment**: [Story 3.6 Assessment](../qa/assessments/story-3.6-assessment.md)
- **QA Gate**: [Story 3.6 Gate](../qa/gates/story-3.6-gate.md)

---

**Navigation:**
- ← Previous: [Story 3.5](story-3.5.md)
- → Next: [Story 3.7](story-3.7.md)
- ↑ Epic: [Epic 3](../epics/epic-3.md)
