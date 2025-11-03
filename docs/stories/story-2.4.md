# Story 2.4: CV Parsing and Quality Validation

> 📋 **Epic**: [Epic 2: Document Processing Pipeline](../epics/epic-2.md)
> 📋 **Architecture**: [Components - Docling Service](../architecture/components.md#component-1-docling-service), [Data Models](../architecture/data-models.md)

## User Story

**As a** product manager,
**I want** test CVs parsed through Docling with validated extraction quality,
**so that** I can confirm critical resume information (skills, experience, education) is accurately captured.

## Acceptance Criteria

1. Test script processes all CVs in `/data/cvs/test-set/` through Docling `/parse` endpoint

2. Parsed CV outputs saved to `/data/cvs/parsed/` directory (one JSON per CV)

3. Sample of 5 CVs manually inspected for extraction quality:
   - Skills/technologies identified (e.g., "Python", "Kubernetes", "AWS")
   - Work experience sections recognized (companies, roles, dates, descriptions)
   - Education extracted
   - Projects/accomplishments captured
   - Contact info and personal data handled appropriately

4. Quality metrics documented in `/docs/cv-parsing-validation.md`:
   - Percentage of CVs successfully parsed (target: 90%+ per NFR2)
   - Common extraction issues (e.g., multi-column layouts, graphics-heavy resumes)
   - Assessment of readiness for LightRAG ingestion

5. If quality below threshold (90%), document mitigation:
   - Remove problematic CVs from test set
   - Adjust Docling parameters
   - Note as limitation in POC findings

6. Validated parsed CVs ready for LightRAG ingestion (Story 2.5)

## Story Status

- **Status**: Not Started
- **Assigned To**: TBD
- **Estimated Effort**: 6-8 hours
- **Dependencies**: Story 2.3 (CV Dataset Acquisition and Preprocessing)
- **Blocks**: Story 2.6

## QA

- **QA Assessment**: [Story 2.4 Assessment](../qa/assessments/story-2.4-assessment.md)
- **QA Gate**: [Story 2.4 Gate](../qa/gates/story-2.4-gate.md)

---

**Navigation:**
- ← Previous: [Story 2.3](story-2.3.md)
- → Next: [Story 2.5](story-2.5.md)
- ↑ Epic: [Epic 2](../epics/epic-2.md)
