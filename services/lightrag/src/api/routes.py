"""FastAPI route handlers for LightRAG service."""

import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request, status

from src.models import (
    DocumentIngestRequest,
    DocumentIngestResponse,
    DocumentStatusResponse,
    HealthResponse,
    QueryRequest,
    QueryResponse,
)
from src.services import LightRAGService

logger = logging.getLogger(__name__)

router = APIRouter()

# Global service instance (initialized in main.py)
lightrag_service: LightRAGService = None


def set_service(service: LightRAGService) -> None:
    """Set the global LightRAG service instance."""
    global lightrag_service
    lightrag_service = service


@router.post(
    "/documents",
    response_model=DocumentIngestResponse,
    status_code=status.HTTP_202_ACCEPTED
)
async def ingest_document(
    request: Request,
    payload: DocumentIngestRequest
) -> DocumentIngestResponse:
    """
    Ingest a document into LightRAG.

    Accepts document chunks from Docling and processes them for retrieval.
    """
    request_id = request.state.request_id

    try:
        logger.info(
            "Document ingestion requested",
            extra={
                "request_id": request_id,
                "document_id": payload.document_id,
                "chunk_count": len(payload.chunks)
            }
        )

        # Join chunks into full document text for LightRAG
        document_text = "\n\n".join([chunk.text for chunk in payload.chunks])

        result = await lightrag_service.ingest_document(
            document_text=document_text,
            document_id=payload.document_id,
            metadata=payload.metadata
        )

        return DocumentIngestResponse(**result)

    except Exception as e:
        logger.error(
            "Document ingestion failed",
            extra={"request_id": request_id, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document ingestion failed: {str(e)}"
        )


@router.get(
    "/documents/{document_id}/status",
    response_model=DocumentStatusResponse
)
async def get_document_status(
    request: Request,
    document_id: str
) -> DocumentStatusResponse:
    """Get the processing status of a document."""
    request_id = request.state.request_id

    try:
        logger.info(
            "Document status requested",
            extra={"request_id": request_id, "document_id": document_id}
        )

        status_data = await lightrag_service.get_document_status(document_id)
        return DocumentStatusResponse(**status_data)

    except Exception as e:
        logger.error(
            "Failed to get document status",
            extra={"request_id": request_id, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document status: {str(e)}"
        )


@router.post("/query", response_model=QueryResponse)
async def query(
    request: Request,
    payload: QueryRequest
) -> QueryResponse:
    """
    Query LightRAG for matching candidates.

    Supports multiple retrieval modes: naive, local, global, hybrid.
    """
    request_id = request.state.request_id

    try:
        logger.info(
            "Query requested",
            extra={
                "request_id": request_id,
                "mode": payload.mode,
                "top_k": payload.top_k
            }
        )

        result = await lightrag_service.query(
            query=payload.query,
            mode=payload.mode,
            top_k=payload.top_k,
            filters=payload.filters
        )

        return QueryResponse(**result)

    except Exception as e:
        logger.error(
            "Query failed",
            extra={"request_id": request_id, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    """
    Health check endpoint.

    Verifies PostgreSQL and Ollama connectivity.
    """
    request_id = request.state.request_id

    try:
        health_data = await lightrag_service.health_check()
        return HealthResponse(**health_data)

    except Exception as e:
        logger.error(
            "Health check failed",
            extra={"request_id": request_id, "error": str(e)},
            exc_info=True
        )
        # Return degraded health instead of error
        return HealthResponse(
            status="unhealthy",
            postgres_connected=False,
            ollama_connected=False,
            documents_indexed=0
        )
