# QA Gates

This directory contains QA gate documents for each story. Gates are quality checkpoints that must be passed before a story is considered complete and ready for integration.

## Purpose

QA Gates serve as:
- **Quality Checkpoints** - Formal approval points in the development cycle
- **Go/No-Go Decisions** - Clear criteria for story completion
- **Traceability** - Record of quality decisions and rationale
- **Risk Management** - Early identification of quality issues

## Gate Criteria

Each gate evaluates:
1. **Acceptance Criteria Met** - All ACs from story satisfied
2. **QA Assessment Complete** - Testing documented and reviewed
3. **No Critical Issues** - No blocking defects remaining
4. **Architecture Compliance** - Implementation follows architecture
5. **Documentation Complete** - Code, API, user docs as needed

## Gate Template

See [gate-template.md](gate-template.md) for the standard format.

## Gate Lifecycle

1. **Gate Created**: Placeholder created with story
2. **Criteria Defined**: Specific gate criteria documented
3. **Assessment Reviewed**: QA assessment feeds into gate decision
4. **Gate Decision**: Approved, Rejected, or Conditional approval
5. **Action Items**: Any required follow-up documented

## Gate Outcomes

- **✅ APPROVED** - Story complete, ready for integration
- **⚠️ APPROVED WITH CONDITIONS** - Story usable but has minor issues
- **❌ REJECTED** - Rework required before story completion

## File Naming Convention

- Pattern: `story-{epic}.{story}-gate.md`
- Example: `story-1.1-gate.md` for Story 1.1

## Gate Authority

- **Single Story**: PO or Tech Lead can approve
- **Epic Complete**: Requires PO + Tech Lead approval
- **Critical Issues**: Escalate to project stakeholders
