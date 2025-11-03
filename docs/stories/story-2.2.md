# Story 2.2: CIGREF English PDF Parsing and Quality Validation

> 📋 **Epic**: [Epic 2: Document Processing Pipeline](../epics/epic-2.md)
> 📋 **Architecture**: [Components - Docling Service](../architecture/components.md#component-1-docling-service), [Data Models](../architecture/data-models.md)

## User Story

**As a** product manager,
**I want** the CIGREF IT profile nomenclature PDF parsed with validated extraction quality,
**so that** I can confirm structured profile data (missions, skills, deliverables) is accurately captured.

## Acceptance Criteria

1. CIGREF English 2024 edition PDF downloaded and placed in `/data/cigref/` directory

2. Test script or manual process submits CIGREF PDF to Docling `/parse` endpoint

3. Parsed output is manually inspected and validated for:
   - All IT profile domains identified (e.g., Business, Development, Production, Support)
   - Individual profiles extracted (e.g., Cloud Architect, DevOps Engineer, Data Scientist)
   - Structured sections recognized: Missions, Activities, Deliverables, Performance Indicators, Skills
   - Tables and lists properly parsed (not mangled)
   - French/English mixed content handled appropriately (English edition focus)

4. Quality validation results documented in `/docs/cigref-parsing-validation.md`:
   - Sample profile showing successful extraction
   - Known issues or limitations
   - Assessment: "Meets 85%+ extraction quality threshold" (NFR3) or notes gaps

5. If quality is below threshold, document remediation approach (manual pre-processing, Docling parameter tuning, or supplemental manual data entry)

6. Parsed CIGREF content saved to `/data/cigref/cigref-parsed.json` or similar format for LightRAG ingestion

## Story Status

- **Status**: Ready to Start
- **Assigned To**: TBD
- **Estimated Effort**: 6-8 hours
- **Dependencies**: Story 2.1 (Docling REST API Implementation) ✅ Complete
- **Blocks**: Story 2.5
- **Test Data**: ✅ CIGREF PDF downloaded (4.8 MB, 2024 English edition)

## QA

- **QA Assessment**: [Story 2.2 Assessment](../qa/assessments/story-2.2-assessment.md)
- **QA Gate**: [Story 2.2 Gate](../qa/gates/story-2.2-gate.md)

---

**Navigation:**
- ← Previous: [Story 2.1](story-2.1.md)
- → Next: [Story 2.3](story-2.3.md)
- ↑ Epic: [Epic 2](../epics/epic-2.md)
