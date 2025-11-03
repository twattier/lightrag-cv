# Epic 4: Hybrid Retrieval & Match Explanation

> 📋 **Architecture References**:
> - [Data Models](../architecture/data-models.md) - Graph relationships
> - [Core Workflows - Hybrid Retrieval Query](../architecture/core-workflows.md#workflow-3-hybrid-retrieval-query) - Retrieval logic
> - [Test Strategy](../architecture/test-strategy.md) - UAT approach
> - [Error Handling Strategy](../architecture/error-handling-strategy.md) - Response formatting

**Epic Goal**: Implement intelligent LightRAG retrieval mode selection based on query complexity, enhance candidate ranking with graph-based relationship insights, generate structured match explanations showing CIGREF alignment and skill overlaps, and validate explainability with test users to ensure recommendations are trustworthy and comprehensible.

## Stories

1. [Story 4.1: LightRAG Retrieval Mode Strategy Implementation](../stories/story-4.1.md)
2. [Story 4.2: Graph-Based Relationship Extraction for Match Ranking](../stories/story-4.2.md)
3. [Story 4.3: Structured Match Explanation Generation](../stories/story-4.3.md)
4. [Story 4.4: Match Explanation Rendering in OpenWebUI](../stories/story-4.4.md)
5. [Story 4.5: Confidence Scoring and Ranking Refinement](../stories/story-4.5.md)
6. [Story 4.6: Query Performance Optimization and Testing](../stories/story-4.6.md)
7. [Story 4.7: End-to-End User Acceptance Testing](../stories/story-4.7.md)

## Epic Status

- **Status**: Not Started
- **Story Count**: 7
- **Dependencies**: Epic 3 (MCP Server & OpenWebUI Integration)
- **Blocked By**: None

---

**Related Documentation:**
- [PRD Epic 4 (Full)](../prd/epic-4-hybrid-retrieval-match-explanation.md)
- [Epic List](../prd/epic-list.md)
