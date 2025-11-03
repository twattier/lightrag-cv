# Error Handling Strategy

**Philosophy:** Fail fast, log comprehensively, surface actionable errors to users while hiding technical complexity.

## General Approach

**Error Model:** Structured error responses with consistent format

```python
class ErrorResponse:
    error_code: str       # Machine-readable (e.g., "OLLAMA_TIMEOUT")
    message: str          # User-friendly message
    details: dict | None  # Additional context
    timestamp: str        # ISO 8601 timestamp
    request_id: str       # Correlation ID
    service: str          # Service that generated error
```

**Exception Hierarchy:**

```python
class LightRAGCVException(Exception):
    """Base exception for all system errors"""
    pass

class DocumentParsingError(LightRAGCVException):
    """Raised when document parsing fails"""
    pass

class IngestionError(LightRAGCVException):
    """Raised when LightRAG ingestion fails"""
    pass

class RetrievalError(LightRAGCVException):
    """Raised when query/retrieval fails"""
    pass

class ExternalServiceError(LightRAGCVException):
    """Raised when external service fails"""
    pass
```

## Error Handling Patterns

**1. External API Errors (Ollama):**

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_ollama(prompt: str):
    try:
        response = await ollama_client.generate(prompt)
        return response
    except httpx.TimeoutException:
        raise ExternalServiceError(
            message="LLM service timeout. Please try again.",
            error_code="OLLAMA_TIMEOUT"
        )
    except httpx.ConnectError:
        raise ExternalServiceError(
            message="LLM service unavailable. Check Ollama is running.",
            error_code="OLLAMA_UNAVAILABLE"
        )
```

**2. Database Errors:**

```python
async def execute_query(query: str, params: tuple):
    try:
        async with db.connection() as conn:
            result = await conn.execute(query, params)
            return result
    except psycopg.OperationalError:
        raise ExternalServiceError(
            message="Database temporarily unavailable.",
            error_code="DB_CONNECTION_FAILED"
        )
```

**3. Input Validation:**

```python
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    mode: str = Field("hybrid", regex=r"^(naive|local|global|hybrid)$")
    top_k: int = Field(5, ge=1, le=50)
```

## Logging Standards

**Log Format:** Structured JSON

```python
logger.info(
    "Document processed",
    extra={
        "request_id": request_id,
        "document_id": document_id,
        "chunk_count": len(chunks),
        "duration_ms": duration
    }
)
```

**Log Levels:**
- **DEBUG:** Detailed diagnostic info
- **INFO:** Normal operations
- **WARNING:** Unexpected but handled
- **ERROR:** Recoverable failures
- **CRITICAL:** System-level failures

---
