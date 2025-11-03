"""FastAPI route handlers for Docling service."""

import logging
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status

from src.models import HealthResponse, ParseResponse
from src.services import DoclingService

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
    request: Request,
    file: UploadFile = File(...),
    options: Optional[str] = Form(None)
) -> ParseResponse:
    """
    Parse a PDF or DOCX document into chunks.

    Accepts multipart/form-data with a file upload.
    """
    request_id = request.state.request_id

    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.docx')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF and DOCX files are supported"
            )

        logger.info(
            "Document parse requested",
            extra={
                "request_id": request_id,
                "filename": file.filename,
                "content_type": file.content_type
            }
        )

        # Read file content
        file_content = await file.read()

        # Parse options (JSON string if provided)
        parse_options = {}
        if options:
            import json
            try:
                parse_options = json.loads(options)
            except json.JSONDecodeError:
                logger.warning("Invalid options JSON", extra={"request_id": request_id})

        # Parse document
        result = await docling_service.parse_document(
            file_content=file_content,
            filename=file.filename,
            options=parse_options
        )

        return ParseResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Document parsing failed",
            extra={"request_id": request_id, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document parsing failed: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    """
    Health check endpoint.

    Verifies service is operational and reports GPU availability.
    """
    request_id = request.state.request_id

    try:
        health_data = await docling_service.health_check()
        return HealthResponse(**health_data)

    except Exception as e:
        logger.error(
            "Health check failed",
            extra={"request_id": request_id, "error": str(e)},
            exc_info=True
        )
        return HealthResponse(
            status="unhealthy",
            gpu_available=False
        )
