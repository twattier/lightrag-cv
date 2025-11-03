# Epic 4: Hybrid Retrieval & Match Explanation

> 🎯 **Development Artifacts**: [Epic 4 Card](../epics/epic-4.md) | [Stories 4.1-4.7](../stories/README.md#epic-4-hybrid-retrieval--match-explanation-7-stories)
>

> 📋 **Architecture References**:
> - [Data Models](../architecture/data-models.md) - Graph relationships
> - [Core Workflows - Hybrid Retrieval Query](../architecture/core-workflows.md#workflow-3-hybrid-retrieval-query) - Retrieval logic
> - [Test Strategy](../architecture/test-strategy.md) - UAT approach
> - [Error Handling Strategy](../architecture/error-handling-strategy.md) - Response formatting

**Epic Goal**: Implement intelligent LightRAG retrieval mode selection based on query complexity, enhance candidate ranking with graph-based relationship insights, generate structured match explanations showing CIGREF alignment and skill overlaps, and validate explainability with test users to ensure recommendations are trustworthy and comprehensible.

## Story 4.1: LightRAG Retrieval Mode Strategy Implementation

**As a** developer,
**I want** the MCP server to intelligently select LightRAG retrieval modes based on query characteristics,
**so that** simple queries run fast (naive/local) while complex multi-criteria queries leverage full hybrid capabilities.

### Acceptance Criteria

1. MCP server implements retrieval mode selection logic:
   - **Naive mode**: Single-entity queries (e.g., "Who has Python experience?") → fast vector-only search
   - **Local mode**: Profile or specific competency queries (e.g., "Cloud Architects") → entity-focused with immediate graph neighborhood
   - **Global mode**: Broad domain queries (e.g., "All infrastructure specialists") → graph traversal across domains
   - **Hybrid mode**: Complex multi-criteria queries (e.g., "Senior DevOps with AWS, Terraform, and leadership") → combines vector similarity + graph relationships

2. Mode selection algorithm considers:
   - Number of criteria in query (1 criterion → naive/local, 3+ criteria → hybrid)
   - Query scope (specific entity vs. broad domain)
   - User-specified mode override if exposed as optional parameter

3. MCP tool implementations updated to pass selected mode to LightRAG API

4. Test suite validates mode selection:
   - 5 test queries per mode type (20 total)
   - Verify correct mode selected based on query characteristics
   - Document rationale for each selection

5. Performance comparison documented:
   - Response time for same query across all 4 modes
   - Quality comparison (are results different? which mode gives best results?)
   - Findings in `/docs/retrieval-modes-analysis.md`

6. Configuration option added to `.env` for default mode or mode selection strategy (allow tuning)

## Story 4.2: Graph-Based Relationship Extraction for Match Ranking

**As a** developer,
**I want** candidate ranking enhanced with graph relationship insights,
**so that** matches reflect not just keyword overlap but semantic and structural relationships between candidate experience and profile requirements.

### Acceptance Criteria

1. When retrieving candidates, MCP server queries LightRAG for graph relationships:
   - Candidate skill nodes → competency nodes → CIGREF mission nodes
   - Candidate experience → domain entities → profile requirement entities
   - Example: Candidate mentions "Kubernetes" → graph shows "Kubernetes" relates to "container orchestration" → relates to "Cloud Infrastructure" competency → relates to "Cloud Architect" missions

2. Graph relationship scoring incorporated into ranking:
   - Direct relationships (1-hop) score higher than indirect (2-3 hops)
   - Multiple relationship paths increase confidence
   - Rare/specialized relationships weighted appropriately (domain-specific)

3. LightRAG's graph storage (PGGraphStorage via Apache AGE) queried using Cypher-like queries or LightRAG's graph API

4. Test validates graph-enhanced ranking:
   - Compare ranking with pure vector similarity vs. graph-enhanced hybrid
   - Identify cases where graph relationships surface better candidates (e.g., semantic similarity finds "SRE" when query is "DevOps Engineer")
   - Document 3-5 examples showing graph value

5. Graph queries optimized for performance:
   - Response time remains <10s for POC (graph traversal doesn't bottleneck)
   - If slow, limit graph depth (e.g., max 3 hops) or cache common paths

6. Graph relationship data included in tool responses for use in match explanations (Story 4.3)

## Story 4.3: Structured Match Explanation Generation

**As a** recruiter,
**I want** each candidate recommendation accompanied by a clear explanation of why they match,
**so that** I understand and trust the system's recommendations.

### Acceptance Criteria

1. MCP server generates match explanations for each candidate result including:
   - **CIGREF Profile Alignment**: Which missions, activities, or deliverables align with candidate experience
   - **Skill Matches**: Exact skill overlaps (e.g., "Candidate has AWS, Kubernetes") and semantic matches (e.g., "Docker expertise relates to container orchestration")
   - **Graph Relationships**: Key relationship paths that influenced ranking (e.g., "Candidate's microservices experience connects to distributed systems competency")
   - **Confidence Score**: Numerical score (0-100) or qualitative (High/Medium/Low) indicating match strength

2. Explanation format is structured and consistent:
   - Organized by category (Profile, Skills, Experience, Graph Insights)
   - Concise (3-7 bullet points total per candidate)
   - Non-technical language accessible to recruiters without IT expertise

3. Explanation generation uses:
   - LightRAG's graph query results
   - Vector similarity scores
   - Entity extraction from candidate CV and CIGREF profiles
   - LLM (qwen3:8b via Ollama) to synthesize human-readable summary if needed

4. MCP tool responses include explanations inline with each candidate:
   ```json
   {
     "candidate_id": "candidate_12",
     "summary": "Senior Cloud Engineer, 8 years experience",
     "explanation": {
       "profile_alignment": ["Matches Cloud Architect mission: 'Design cloud infrastructure'"],
       "skill_matches": ["AWS (exact match)", "Kubernetes (exact match)", "Terraform → Infrastructure as Code competency"],
       "graph_insights": ["Microservices experience relates to distributed systems design"],
       "confidence": "High (85%)"
     }
   }
   ```

5. Manual review of explanations for 10 candidates:
   - Explanations are accurate (align with CV content and CIGREF profiles)
   - Explanations are comprehensible to non-technical reviewers
   - Explanations provide actionable insight (not generic statements)

6. Documentation includes explanation generation logic and example outputs

## Story 4.4: Match Explanation Rendering in OpenWebUI

**As a** recruiter,
**I want** match explanations displayed clearly in the chat interface,
**so that** I can quickly understand why each candidate was recommended without information overload.

### Acceptance Criteria

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

## Story 4.5: Confidence Scoring and Ranking Refinement

**As a** recruiter,
**I want** candidates ranked by match quality with confidence scores,
**so that** I can prioritize reviewing the most promising candidates first.

### Acceptance Criteria

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

## Story 4.6: Query Performance Optimization and Testing

**As a** developer,
**I want** to optimize query performance across all retrieval modes,
**so that** response times meet the <10 second POC target for typical queries.

### Acceptance Criteria

1. Performance test suite created with 20 representative queries:
   - 5 simple (single skill, naive mode)
   - 5 moderate (profile match, local mode)
   - 5 complex (multi-criteria, hybrid mode)
   - 5 very complex (broad domain + filters, global mode)

2. Each query executed 3 times, response time measured end-to-end:
   - OpenWebUI input → MCP tool invocation → LightRAG retrieval → PostgreSQL queries → Result return
   - Record: p50, p95, p99 response times

3. Performance results documented in `/docs/performance-results.md`:
   - All queries: Comparison to <10s POC target
   - Slowest queries identified with bottleneck analysis (LightRAG retrieval? PostgreSQL query? Embedding generation? Graph traversal?)

4. If queries exceed 10s target:
   - Optimization attempts: Reduce context size, limit graph depth, tune PostgreSQL indices, adjust LightRAG parameters
   - Document optimizations applied and impact
   - If still slow, acceptable for POC with Phase 2 optimization plan

5. GPU acceleration impact measured (if available):
   - Compare query times with/without GPU for Docling processing
   - Embeddings generation time (likely not GPU-accelerated via Ollama unless configured)

6. Performance recommendations for Phase 2:
   - Caching strategies
   - Index optimization
   - Parallel query execution
   - Model optimization or quantization

## Story 4.7: End-to-End User Acceptance Testing

**As a** product manager,
**I want** test users (recruiters/hiring managers) to validate the complete system workflow,
**so that** we confirm the POC meets success criteria before demonstration.

### Acceptance Criteria

1. User acceptance test conducted with 2-5 test users (recruiters or hiring managers)

2. Test protocol:
   - Each user completes 5 predefined search scenarios (covering profile match, skill search, multi-criteria, conversational refinement)
   - Users rate each result: "Accurate match" / "Mostly accurate" / "Inaccurate"
   - Users assess explanation quality: "Helpful and clear" / "Somewhat helpful" / "Not helpful"
   - Users complete satisfaction survey:
     - "Would you use this system in your daily workflow?" (Yes/No/Maybe)
     - "Does this save time compared to manual screening?" (Yes/No)
     - "Do you trust the recommendations?" (Yes/No/Needs improvement)

3. Success metrics from brief validated:
   - **Match quality**: 70%+ of results rated "Accurate" or "Mostly accurate" (target from brief)
   - **Explainability satisfaction**: Users can articulate why candidates were recommended
   - **Adoption willingness**: 60%+ express willingness to use system (target from brief)
   - **Conversational UX**: Users successfully refine searches iteratively

4. Test results documented in `/docs/uat-results.md`:
   - Quantitative metrics (ratings, completion rates, response times)
   - Qualitative feedback (quotes, pain points, feature requests)
   - Comparison to success criteria from brief

5. If success criteria not met:
   - Root cause analysis (poor ranking? confusing explanations? slow performance? UI issues?)
   - Document gaps and Phase 2 requirements
   - Assessment: "POC demonstrates feasibility despite gaps" or "Critical issues block validation"

6. Test user feedback incorporated into final POC demonstration and Phase 2 recommendations

---
