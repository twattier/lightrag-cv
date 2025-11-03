"""Response models for Docling API."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class ChunkData(BaseModel):
    """Individual document chunk."""

    chunk_id: str
    content: str
    chunk_type: str = "paragraph"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ParseMetadata(BaseModel):
    """Document parsing metadata."""

    page_count: int = 0
    format: str
    tables_extracted: int = 0
    processing_time_ms: int


class ParseResponse(BaseModel):
    """Response from document parsing."""

    document_id: str
    chunks: List[ChunkData]
    metadata: ParseMetadata


class HealthResponse(BaseModel):
    """Health check response."""

    status: Literal["healthy", "unhealthy"]
    gpu_available: bool = False


class ErrorResponse(BaseModel):
    """Standardized error response."""

    error_code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="User-friendly error message")
    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional error context"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO 8601 timestamp",
    )
    request_id: str = Field(..., description="Request correlation ID")
    service: str = Field(default="docling", description="Service name")
