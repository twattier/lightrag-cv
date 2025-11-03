# Story 3.7: Result Rendering and Display in Chat

> 📋 **Epic**: [Epic 3: MCP Server & OpenWebUI Integration](../epics/epic-3.md)
> 📋 **Architecture**: [Components - MCP Server](../architecture/components.md#component-3-mcp-server), [Error Handling Strategy](../architecture/error-handling-strategy.md)

## User Story

**As a** recruiter,
**I want** candidate results displayed clearly in the chat interface with key information highlighted,
**so that** I can quickly assess matches without being overwhelmed by data.

## Acceptance Criteria

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

## Story Status

- **Status**: Not Started
- **Assigned To**: TBD
- **Estimated Effort**: 4-6 hours
- **Dependencies**: Story 3.6 (Conversational Query Refinement)
- **Blocks**: Story 3.8

## QA

- **QA Assessment**: [Story 3.7 Assessment](../qa/assessments/story-3.7-assessment.md)
- **QA Gate**: [Story 3.7 Gate](../qa/gates/story-3.7-gate.md)

---

**Navigation:**
- ← Previous: [Story 3.6](story-3.6.md)
- → Next: [Story 3.8](story-3.8.md)
- ↑ Epic: [Epic 3](../epics/epic-3.md)
