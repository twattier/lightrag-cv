# Coding Standards

**Purpose:** MANDATORY standards for AI-driven development.

## Critical Rules

**RULE 1: Never Extend or Modify LightRAG/Docling Internals**

```python
# ❌ WRONG
class CustomLightRAG(LightRAG):
    pass

# ✅ CORRECT
class LightRAGService:
    def __init__(self):
        self.lightrag = LightRAG(config=self.config)
```

**RULE 2: All Environment Variables via config.py**

```python
# ❌ WRONG
postgres_host = os.environ.get("POSTGRES_HOST")

# ✅ CORRECT
from config import settings
postgres_host = settings.POSTGRES_HOST
```

**RULE 3: All API Responses Use Pydantic Models**

```python
# ❌ WRONG
return {"chunks": chunks}

# ✅ CORRECT
return ParseResponse(chunks=chunks)
```

**RULE 4: Database Queries via Service Layer Only**

```python
# ❌ WRONG - SQL in API layer
@app.get("/candidates")
async def get_candidates():
    result = await conn.execute("SELECT * FROM document_metadata")

# ✅ CORRECT - SQL in service layer
@app.get("/candidates")
async def get_candidates():
    return await metadata_service.get_all_candidates()
```

**RULE 5: Always Use request_id for Tracing**

```python
from fastapi import Request

@app.post("/query")
async def query(request: Request):
    request_id = request.state.request_id
    logger.info("Query received", extra={"request_id": request_id})
```

**RULE 6: All Exceptions Must Use Custom Classes**

```python
# ❌ WRONG
raise ValueError("Invalid input")

# ✅ CORRECT
raise DocumentParsingError(
    message="Invalid input",
    error_code="INVALID_INPUT"
)
```

**RULE 7: Logging Must Include Structured Context**

```python
# ❌ WRONG
logger.info(f"Processing {document_id}")

# ✅ CORRECT
logger.info(
    "Processing document",
    extra={"document_id": document_id, "request_id": request_id}
)
```

**RULE 8: Never Log Sensitive Data**

```python
# ❌ WRONG
logger.info(f"CV content: {cv_content}")

# ✅ CORRECT
logger.info("CV processed", extra={"document_id": doc_id, "length": len(cv_content)})
```

**RULE 9: Async Functions for All I/O**

```python
# ❌ WRONG
def get_data():
    return requests.get(url)

# ✅ CORRECT
async def get_data():
    async with httpx.AsyncClient() as client:
        return await client.get(url)
```

**RULE 10: LightRAG and Docling are Black Boxes**

```python
# ❌ WRONG - Accessing internals
chunks = lightrag_result["_internal_chunks"]

# ✅ CORRECT - Use documented API
candidates = lightrag_result.get("results", [])
```

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Files | snake_case | `lightrag_service.py` |
| Classes | PascalCase | `LightRAGService` |
| Functions | snake_case | `parse_document()` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES` |
| Environment vars | UPPER_SNAKE_CASE | `POSTGRES_HOST` |
| API endpoints | kebab-case | `/search-by-profile` |
| Database tables | snake_case | `document_metadata` |

---
