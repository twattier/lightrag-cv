"""FastAPI route handlers for Docling service."""

import json
import logging
from typing import Optional

from fastapi import APIRouter, File, Form, Request, UploadFile

from src.config import settings
from src.models import HealthResponse, ParseResponse
from src.services import (
    DoclingService,
    FileSizeExceededError,
    InvalidFileFormatError,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Global service instance (initialized in main.py)
docling_service: DoclingService = None


def set_service(service: DoclingService) -> None:
    """Set the global Docling service instance."""
    global docling_service
    docling_service = service


@router.post("/parse", response_model=ParseResponse)
async def parse_document(
    request: Request, file: UploadFile = File(...), options: Optional[str] = Form(None)
) -> ParseResponse:
    """
    Parse a PDF or DOCX document into chunks.

    Accepts multipart/form-data with a file upload.

    Args:
        request: FastAPI request object (contains request_id in state)
        file: Uploaded file (PDF or DOCX)
        options: Optional JSON string with parsing options

    Returns:
        ParseResponse with document chunks and metadata

    Raises:
        InvalidFileFormatError: If file is not PDF or DOCX (400)
        FileSizeExceededError: If file exceeds configured size limit (413)
        DocumentParsingError: If parsing fails (500)
    """
    request_id = request.state.request_id

    # Validate file type
    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise InvalidFileFormatError(
            message="Only PDF and DOCX files are supported",
            error_code="INVALID_FILE_FORMAT",
            details={"filename": file.filename, "supported_formats": ["PDF", "DOCX"]},
        )

    logger.info(
        "Document parse requested",
        extra={
            "request_id": request_id,
            "document_filename": file.filename,
            "content_type": file.content_type,
        },
    )

    # Read file content
    file_content = await file.read()

    # Validate file size (RULE: File size validation returns 413)
    file_size_mb = len(file_content) / (1024 * 1024)
    max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(file_content) > max_size_bytes:
        raise FileSizeExceededError(
            message=f"File size ({file_size_mb:.2f}MB) exceeds maximum allowed ({settings.MAX_FILE_SIZE_MB}MB)",
            error_code="FILE_TOO_LARGE",
            details={
                "file_size_bytes": len(file_content),
                "file_size_mb": round(file_size_mb, 2),
                "max_size_mb": settings.MAX_FILE_SIZE_MB,
                "filename": file.filename,
            },
        )

    # Parse options (JSON string if provided)
    parse_options = {}
    if options:
        try:
            parse_options = json.loads(options)
        except json.JSONDecodeError:
            logger.warning("Invalid options JSON", extra={"request_id": request_id})

    # Parse document (service layer will raise DocumentParsingError if fails)
    result = await docling_service.parse_document(
        file_content=file_content, filename=file.filename, options=parse_options
    )

    return ParseResponse(**result)


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    """
    Health check endpoint.

    Verifies service is operational and reports GPU availability.

    Args:
        request: FastAPI request object (contains request_id in state)

    Returns:
        HealthResponse with service status and GPU availability
    """
    request_id = request.state.request_id

    try:
        health_data = await docling_service.health_check()
        return HealthResponse(**health_data)

    except Exception as e:
        logger.error(
            "Health check failed",
            extra={"request_id": request_id, "error": str(e)},
            exc_info=True,
        )
        return HealthResponse(status="unhealthy", gpu_available=False)
