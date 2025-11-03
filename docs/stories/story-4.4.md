# Story 4.4: Match Explanation Rendering in OpenWebUI

> 📋 **Epic**: [Epic 4: Hybrid Retrieval & Match Explanation](../epics/epic-4.md)
> 📋 **Architecture**: [Components - MCP Server](../architecture/components.md#component-3-mcp-server), [Error Handling Strategy](../architecture/error-handling-strategy.md)

## User Story

**As a** recruiter,
**I want** match explanations displayed clearly in the chat interface,
**so that** I can quickly understand why each candidate was recommended without information overload.

## Acceptance Criteria

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

## Story Status

- **Status**: Not Started
- **Assigned To**: TBD
- **Estimated Effort**: 6-8 hours
- **Dependencies**: Story 4.3 (Structured Match Explanation Generation)
- **Blocks**: Story 4.5, Story 4.7

## QA

- **QA Assessment**: [Story 4.4 Assessment](../qa/assessments/story-4.4-assessment.md)
- **QA Gate**: [Story 4.4 Gate](../qa/gates/story-4.4-gate.md)

---

**Navigation:**
- ← Previous: [Story 4.3](story-4.3.md)
- → Next: [Story 4.5](story-4.5.md)
- ↑ Epic: [Epic 4](../epics/epic-4.md)
