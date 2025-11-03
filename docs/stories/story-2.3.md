# Story 2.3: CV Dataset Acquisition and Preprocessing

> 📋 **Epic**: [Epic 2: Document Processing Pipeline](../epics/epic-2.md)
> 📋 **Architecture**: [Data Models](../architecture/data-models.md), [Source Tree](../architecture/source-tree.md)

## User Story

**As a** developer,
**I want** a curated test set of 20-30 English IT resumes from Hugging Face datasets,
**so that** I have representative data for knowledge base population and testing.

## Acceptance Criteria

1. Download and sample CVs from specified Hugging Face datasets:
   - `gigswar/cv_files`
   - `d4rk3r/resumes-raw-pdf`

2. Filter for English language IT/technical resumes (software, infrastructure, data, security roles)

3. Curate final test set of 20-30 CVs with diverse characteristics:
   - Multiple experience levels (junior, mid, senior)
   - Various IT domains (development, infrastructure, data, security, management)
   - Different formats (PDF, DOCX if available)
   - Different lengths (1-3 pages typical)

4. CVs organized in `/data/cvs/test-set/` with basic metadata file (`cvs-manifest.json`) listing:
   - Filename
   - Inferred role/domain (manual tagging)
   - Experience level estimate
   - File format

5. Sample of 3-5 CVs manually reviewed for quality and relevance (not gibberish, contains actual technical content)

6. Documentation in `/docs/test-data.md` describes dataset composition and filtering criteria

## Story Status

- **Status**: Not Started
- **Assigned To**: TBD
- **Estimated Effort**: 4-6 hours
- **Dependencies**: Story 2.1 (Docling REST API Implementation)
- **Blocks**: Story 2.4

## QA

- **QA Assessment**: [Story 2.3 Assessment](../qa/assessments/story-2.3-assessment.md)
- **QA Gate**: [Story 2.3 Gate](../qa/gates/story-2.3-gate.md)

---

**Navigation:**
- ← Previous: [Story 2.2](story-2.2.md)
- → Next: [Story 2.4](story-2.4.md)
- ↑ Epic: [Epic 2](../epics/epic-2.md)
