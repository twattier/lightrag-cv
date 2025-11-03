"""Request models for LightRAG API."""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    """Individual document chunk from Docling."""

    chunk_id: str
    content: str
    chunk_type: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentIngestRequest(BaseModel):
    """Request to ingest a document into LightRAG."""

    document_id: str
    chunks: List[DocumentChunk]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class QueryRequest(BaseModel):
    """Request to query LightRAG for candidates."""

    query: str
    mode: Literal["naive", "local", "global", "hybrid"] = "hybrid"
    top_k: int = Field(default=5, ge=1, le=50)
    filters: Optional[Dict[str, Any]] = None
