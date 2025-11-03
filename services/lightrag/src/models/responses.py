"""Response models for LightRAG API."""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class DocumentIngestResponse(BaseModel):
    """Response after document ingestion starts."""

    document_id: str
    status: Literal["processing", "queued"]
    message: str


class DocumentStatusResponse(BaseModel):
    """Status of a document ingestion."""

    document_id: str
    status: Literal["completed", "processing", "failed", "not_found"]
    chunks_created: int = 0
    entities_extracted: int = 0
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: Literal["healthy", "degraded", "unhealthy"]
    postgres_connected: bool
    ollama_connected: bool
    documents_indexed: int = 0


class QueryResult(BaseModel):
    """Individual query result."""

    document_id: str
    content: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
    entities: List[str] = Field(default_factory=list)
    graph_paths: List[Any] = Field(default_factory=list)


class QueryResponse(BaseModel):
    """Response from query endpoint."""

    results: List[QueryResult]
    retrieval_mode_used: str
    query_time_ms: int
