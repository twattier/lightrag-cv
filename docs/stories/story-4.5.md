# Story 4.5: Confidence Scoring and Ranking Refinement

> 📋 **Epic**: [Epic 4: Hybrid Retrieval & Match Explanation](../epics/epic-4.md)
> 📋 **Architecture**: [Core Workflows - Hybrid Retrieval Query](../architecture/core-workflows.md#workflow-3-hybrid-retrieval-query), [Data Models](../architecture/data-models.md)

## User Story

**As a** recruiter,
**I want** candidates ranked by match quality with confidence scores,
**so that** I can prioritize reviewing the most promising candidates first.

## Acceptance Criteria

1. Confidence scoring algorithm implemented combining:
   - Vector similarity score (semantic match strength)
   - Graph relationship count and depth (more/shorter paths = higher confidence)
   - Entity overlap count (number of skills/competencies matched)
   - Weighting: 40% vector similarity, 30% graph relationships, 30% entity overlap (tunable)

2. Confidence score normalized to 0-100 scale or categorized (High/Medium/Low):
   - High: 70-100 (strong match)
   - Medium: 40-69 (partial match, may need gap bridging)
   - Low: 0-39 (weak match, consider only if candidate pool is limited)

3. Candidates ranked by confidence score (highest first) in search results

4. Test validates ranking quality:
   - Manual review of top-5 candidates for 10 different queries
   - Hiring manager or experienced recruiter assesses: "Are these reasonable matches?"
   - Target: 70%+ precision@5 (from NFR4) → at least 3 out of 5 top candidates are genuinely qualified

5. If precision below threshold:
   - Analyze ranking failures (false positives: why ranked high? false negatives: missed qualified candidates?)
   - Tune scoring weights or algorithm
   - Document limitations and Phase 2 improvement strategies

6. Confidence scores included in all search tool responses and displayed to users

## Story Status

- **Status**: Not Started
- **Assigned To**: TBD
- **Estimated Effort**: 8-12 hours
- **Dependencies**: Story 4.2 (Graph-Based Relationship Extraction for Match Ranking), Story 4.4 (Match Explanation Rendering in OpenWebUI)
- **Blocks**: Story 4.6, Story 4.7

## QA

- **QA Assessment**: [Story 4.5 Assessment](../qa/assessments/story-4.5-assessment.md)
- **QA Gate**: [Story 4.5 Gate](../qa/gates/story-4.5-gate.md)

---

**Navigation:**
- ← Previous: [Story 4.4](story-4.4.md)
- → Next: [Story 4.6](story-4.6.md)
- ↑ Epic: [Epic 4](../epics/epic-4.md)
