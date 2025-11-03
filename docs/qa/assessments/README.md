# QA Assessments

This directory contains QA assessment documents for each story. Assessments are detailed evaluations conducted after story implementation to verify acceptance criteria have been met.

## Purpose

QA Assessments document:
- **Test execution results** - Which acceptance criteria were tested and how
- **Evidence of completion** - Screenshots, logs, test outputs
- **Issues found** - Defects, gaps, or concerns identified
- **Quality metrics** - Performance, reliability, usability measurements
- **Recommendations** - Suggestions for improvement or follow-up

## Assessment Template

See [assessment-template.md](assessment-template.md) for the standard format.

## Assessment Lifecycle

1. **Pre-Implementation**: Assessment file created as placeholder
2. **During Implementation**: Developer updates with test plans
3. **Post-Implementation**: QA executes tests and documents results
4. **Review**: Team reviews assessment before story sign-off
5. **Gate Decision**: Assessment feeds into QA Gate approval

## File Naming Convention

- Pattern: `story-{epic}.{story}-assessment.md`
- Example: `story-1.1-assessment.md` for Story 1.1

## Assessment Status

Assessments can have the following statuses:
- **Not Started** - Story not yet implemented
- **In Progress** - Testing underway
- **Completed** - All tests executed, results documented
- **Passed** - Assessment complete, story meets quality standards
- **Failed** - Quality issues identified, rework required
