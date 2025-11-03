# Security

**Security Posture:** POC with local-only deployment and single-user access. Security requirements intentionally relaxed per NFR9.

## POC Security Scope

**Implemented:**
- ✅ Input validation (prevent injection)
- ✅ Secrets management (no hardcoded credentials)
- ✅ CV data privacy (local-only processing)
- ✅ Parameterized queries (SQL injection prevention)

**Not Implemented (deferred to Phase 2):**
- ❌ User authentication
- ❌ TLS/HTTPS
- ❌ Rate limiting
- ❌ Audit logging
- ❌ Data encryption at rest

## Input Validation

**Pydantic Models:**

```python
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    mode: str = Field("hybrid", regex=r"^(naive|local|global|hybrid)$")
    top_k: int = Field(5, ge=1, le=50)
```

**File Upload Validation:**

```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@app.post("/parse")
async def parse_document(file: UploadFile):
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large")

    if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(400, "Only PDF and DOCX allowed")
```

## Database Security

**SQL Injection Prevention:**

```python
# ✅ CORRECT - Parameterized
query = "SELECT * FROM document_metadata WHERE document_id = %s"
result = await db.execute(query, (document_id,))
```

## Secrets Management

**`.env` file (not committed):**

```bash
POSTGRES_PASSWORD=ChangeMeToSecurePassword123!
```

**`.gitignore`:**

```gitignore
.env
*.env
!.env.example
```

## Data Protection

**CV Privacy:**
- Anonymized candidate labels (`candidate_001`)
- No PII in logs
- Local-only processing (no cloud APIs)

**Logging Restrictions:**

```python
# ❌ WRONG
logger.info(f"CV for {candidate_name}: {cv_content}")

# ✅ CORRECT
logger.info("CV processed", extra={"candidate_label": "candidate_001"})
```

## Known Security Limitations

**Accepted Risks for POC:**

1. **No User Authentication** - Anyone with network access can use system
   - Mitigation: Local-only deployment, trusted operators

2. **No TLS/HTTPS** - Communications in plaintext
   - Mitigation: Docker internal network, localhost binding

3. **No Audit Logging** - No record of data access
   - Mitigation: Single-user POC, test data only

4. **No Rate Limiting** - Vulnerable to resource exhaustion
   - Mitigation: Single-user, trusted operator

**Phase 2 Security Roadmap:**
- Implement JWT authentication
- Add TLS for all endpoints
- Implement RBAC
- Add audit logging
- Encrypt data at rest
- Add rate limiting
- Security headers
- Automated vulnerability scanning
- Penetration testing
- GDPR compliance

---
