# Story 4.3: Structured Match Explanation Generation

> 📋 **Epic**: [Epic 4: Hybrid Retrieval & Match Explanation](../epics/epic-4.md)
> 📋 **Architecture**: [Data Models](../architecture/data-models.md), [Components - MCP Server](../architecture/components.md#component-3-mcp-server), [External APIs - Ollama](../architecture/external-apis.md)

## User Story

**As a** recruiter,
**I want** each candidate recommendation accompanied by a clear explanation of why they match,
**so that** I understand and trust the system's recommendations.

## Acceptance Criteria

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

## Story Status

- **Status**: Not Started
- **Assigned To**: TBD
- **Estimated Effort**: 10-14 hours
- **Dependencies**: Story 4.2 (Graph-Based Relationship Extraction for Match Ranking)
- **Blocks**: Story 4.4

## QA

- **QA Assessment**: [Story 4.3 Assessment](../qa/assessments/story-4.3-assessment.md)
- **QA Gate**: [Story 4.3 Gate](../qa/gates/story-4.3-gate.md)

---

**Navigation:**
- ← Previous: [Story 4.2](story-4.2.md)
- → Next: [Story 4.4](story-4.4.md)
- ↑ Epic: [Epic 4](../epics/epic-4.md)
