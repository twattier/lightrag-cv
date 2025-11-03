# Story 3.8: Basic Candidate Detail View

> 📋 **Epic**: [Epic 3: MCP Server & OpenWebUI Integration](../epics/epic-3.md)
> 📋 **Architecture**: [Components - MCP Server](../architecture/components.md#component-3-mcp-server), [Data Models](../architecture/data-models.md)

## User Story

**As a** recruiter,
**I want** to view detailed information about a specific candidate from search results,
**so that** I can make informed decisions about candidate suitability.

## Acceptance Criteria

1. MCP tool implemented: `get_candidate_details`
   - Parameters:
     - `candidate_id` (string): Identifier from search results
   - Returns: Full candidate information including parsed CV content

2. Candidate detail includes:
   - Complete skills list
   - Work history (companies, roles, durations, descriptions)
   - Education and certifications
   - Projects or notable accomplishments
   - Original CV content or parsed structured data

3. Tool callable from OpenWebUI chat:
   - After seeing search results, user can ask: "Show me details for Candidate #3"
   - OpenWebUI interprets and invokes `get_candidate_details`
   - Full details rendered in chat (may be lengthy, uses collapsible sections or markdown formatting)

4. Manual test:
   - Search returns 5 candidates
   - Request details for one candidate
   - Details are comprehensive and readable

5. Detail view uses markdown formatting for structure:
   - Headings for sections (Skills, Experience, Education)
   - Tables for structured data if appropriate
   - Readable on desktop and tablet displays

6. If CV content is very long, truncate with "View full CV" instruction (full details could be added in Phase 2)

## Story Status

- **Status**: Not Started
- **Assigned To**: TBD
- **Estimated Effort**: 6-8 hours
- **Dependencies**: Story 3.7 (Result Rendering and Display in Chat)
- **Blocks**: None

## QA

- **QA Assessment**: [Story 3.8 Assessment](../qa/assessments/story-3.8-assessment.md)
- **QA Gate**: [Story 3.8 Gate](../qa/gates/story-3.8-gate.md)

---

**Navigation:**
- ← Previous: [Story 3.7](story-3.7.md)
- → Next: [Story 4.1](story-4.1.md)
- ↑ Epic: [Epic 3](../epics/epic-3.md)
