# Test Strategy

**Testing Philosophy:** Manual testing with stakeholder validation is sufficient for POC scope.

## Testing Approach

**Primary Strategy:** Manual Exploratory Testing

**Testing Responsibilities:**

| Role | Responsibilities |
|------|------------------|
| Developer | Service integration, API testing, data quality |
| Product Manager | UAT, quality threshold validation |
| Hiring Manager | Match quality validation, explanation comprehensibility |

## Test Types

**1. Service Integration Testing**

Manual Python scripts in `services/{service}/tests/`:

```python
#!/usr/bin/env python3
"""Test CIGREF parsing"""

async def test_parse_cigref():
    response = await client.post("/parse", files={"file": cigref_pdf})
    assert response.status_code == 200
    assert len(response.json()["chunks"]) > 50
    print("✅ CIGREF parsing test PASSED")
```

**2. Data Quality Validation**

Manual inspection documented in `docs/testing/`:
- `cigref-parsing-validation.md`
- `cv-parsing-validation.md`
- `performance-baseline.md`

**3. Non-Functional Testing**

Performance test suite validates NFR1 (<10s queries):

```python
async def run_performance_tests():
    for query in TEST_QUERIES:
        start = time.time()
        response = await execute_query(query)
        elapsed = (time.time() - start) * 1000
        assert elapsed < 10000, "Query exceeded 10s"
```

**4. User Acceptance Testing (UAT)**

Epic 4, Story 4.7: 2-5 hiring managers test system with predefined scenarios.

**UAT Success Criteria:**
- ✅ 70%+ match quality
- ✅ Explainability validated
- ✅ 60%+ adoption willingness

## Test Documentation

All results in `docs/testing/`:
- Quality validation reports
- Performance baselines
- UAT survey results

---
