# QA Gate: Story {epic}.{story}

> 📋 **Story**: [Story {epic}.{story}: {Title}](../../stories/story-{epic}.{story}.md)
> 📋 **Epic**: [Epic {epic}](../../epics/epic-{epic}.md)
> 📋 **Assessment**: [Story {epic}.{story} Assessment](../assessments/story-{epic}.{story}-assessment.md)

## Gate Metadata

- **Gate Date**: YYYY-MM-DD
- **Gate Reviewers**: [Names/Roles]
- **Gate Decision**: [✅ Approved | ⚠️ Approved with Conditions | ❌ Rejected | 🔄 Pending]
- **Story Iteration**: [1, 2, 3, ...]

---

## Gate Criteria Checklist

### Functional Completeness

- [ ] **All Acceptance Criteria Met** - Every AC from story satisfied
- [ ] **User Story Validated** - "As a/I want/so that" intent fulfilled
- [ ] **Functional Testing Complete** - All functional tests passed
- [ ] **Integration Points Verified** - Works with dependent stories/services

**Status**: ✅ Pass | ❌ Fail | ⚠️ Conditional
**Notes**: {details on functional completeness}

---

### Quality Assurance

- [ ] **QA Assessment Complete** - Assessment document finished and reviewed
- [ ] **No Critical Issues** - No P0/P1 defects remaining
- [ ] **Major Issues Resolved** - P2 issues fixed or have mitigation plan
- [ ] **Test Coverage Adequate** - All critical paths tested

**Status**: ✅ Pass | ❌ Fail | ⚠️ Conditional
**Notes**: {details on QA results}

---

### Architecture & Standards Compliance

- [ ] **Architecture Document Followed** - Implementation matches architecture
- [ ] **Coding Standards Met** - Code follows [Coding Standards](../../architecture/coding-standards.md)
- [ ] **Tech Stack Compliance** - Uses approved technologies from [Tech Stack](../../architecture/tech-stack.md)
- [ ] **Error Handling Implemented** - Follows [Error Handling Strategy](../../architecture/error-handling-strategy.md)

**Status**: ✅ Pass | ❌ Fail | ⚠️ Conditional
**Notes**: {details on compliance}

---

### Documentation

- [ ] **Code Documentation** - Code comments, docstrings complete
- [ ] **API Documentation** - Endpoints, parameters, responses documented
- [ ] **User Documentation** - User-facing docs updated (if applicable)
- [ ] **Architecture Updates** - Architecture doc updated if needed

**Status**: ✅ Pass | ❌ Fail | ⚠️ Conditional
**Notes**: {details on documentation}

---

### Non-Functional Requirements

- [ ] **Performance Acceptable** - Meets performance targets
- [ ] **Security Considerations** - Security requirements addressed
- [ ] **Error Handling Robust** - Edge cases and errors handled gracefully
- [ ] **Logging Implemented** - Appropriate logging for debugging

**Status**: ✅ Pass | ❌ Fail | ⚠️ Conditional
**Notes**: {details on NFRs}

---

## Gate Decision

### Overall Assessment

**Decision**: [✅ APPROVED | ⚠️ APPROVED WITH CONDITIONS | ❌ REJECTED]

**Summary**:
{1-2 paragraph summary of gate decision rationale}

**Quality Score**: [0-10] (from QA Assessment)

---

### Conditions (if applicable)

If **APPROVED WITH CONDITIONS**, list all conditions that must be met:

1. **Condition 1**: {description}
   - **Owner**: [Name]
   - **Due Date**: YYYY-MM-DD
   - **Tracked In**: [Issue/ticket link]

2. **Condition 2**: {description}
   - **Owner**: [Name]
   - **Due Date**: YYYY-MM-DD
   - **Tracked In**: [Issue/ticket link]

---

### Rejection Reasons (if applicable)

If **REJECTED**, list all reasons for rejection:

1. **Reason 1**: {critical issue description}
   - **Required Action**: {what must be fixed}
   - **Owner**: [Name]

2. **Reason 2**: {critical issue description}
   - **Required Action**: {what must be fixed}
   - **Owner**: [Name]

**Re-gate Date**: YYYY-MM-DD (when story will be re-reviewed)

---

## Action Items

### Immediate Actions

1. **[Action 1]**
   - Assigned To: [Name]
   - Due Date: YYYY-MM-DD
   - Priority: High/Medium/Low

2. **[Action 2]**
   - Assigned To: [Name]
   - Due Date: YYYY-MM-DD
   - Priority: High/Medium/Low

### Follow-Up Items

1. **[Follow-up 1]**
   - Assigned To: [Name]
   - Target: Next sprint/Phase 2

---

## Stakeholder Sign-Off

### Product Owner
- **Name**: [PO Name]
- **Date**: YYYY-MM-DD
- **Decision**: ✅ Approve | ❌ Reject | ⚠️ Conditional
- **Comments**: {PO feedback}

### Tech Lead / Architect
- **Name**: [Tech Lead Name]
- **Date**: YYYY-MM-DD
- **Decision**: ✅ Approve | ❌ Reject | ⚠️ Conditional
- **Comments**: {Technical feedback}

### QA Lead (if applicable)
- **Name**: [QA Lead Name]
- **Date**: YYYY-MM-DD
- **Decision**: ✅ Approve | ❌ Reject | ⚠️ Conditional
- **Comments**: {QA feedback}

---

## Gate History

| Date | Decision | Reviewer | Notes |
|------|----------|----------|-------|
| YYYY-MM-DD | [Decision] | [Name] | {brief notes} |

---

## Related Artifacts

- **Story**: [Story {epic}.{story}](../../stories/story-{epic}.{story}.md)
- **QA Assessment**: [Assessment](../assessments/story-{epic}.{story}-assessment.md)
- **Previous Gate**: [Story {prev} Gate](story-{prev}-gate.md)
- **Next Gate**: [Story {next} Gate](story-{next}-gate.md)
- **Epic Gate**: [Epic {epic} Gate](epic-{epic}-gate.md) (when all stories complete)
