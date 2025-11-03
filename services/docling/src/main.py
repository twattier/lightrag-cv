"""FastAPI application for Docling service."""

import logging
import sys
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routes import router, set_service
from src.config import settings
from src.models import ErrorResponse
from src.services import (
    DoclingService,
    DocumentParsingError,
    FileSizeExceededError,
    InvalidFileFormatError,
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Docling service")

    # Initialize Docling service
    service = DoclingService()
    set_service(service)

    logger.info("Docling service ready", extra={"gpu_available": service.gpu_available})

    yield

    # Shutdown
    logger.info("Shutting down Docling service")


# Create FastAPI app
app = FastAPI(
    title="Docling Service",
    description="Document parsing and chunking service with optional GPU acceleration",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(DocumentParsingError)
async def document_parsing_error_handler(request: Request, exc: DocumentParsingError):
    """Handle document parsing errors (500)."""
    error_response = ErrorResponse(
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        request_id=getattr(request.state, "request_id", "unknown"),
    )
    logger.error(
        "Document parsing error",
        extra={
            "request_id": error_response.request_id,
            "error_code": exc.error_code,
            "error": exc.message,
        },
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(),
    )


@app.exception_handler(FileSizeExceededError)
async def file_size_error_handler(request: Request, exc: FileSizeExceededError):
    """Handle file size exceeded errors (413)."""
    error_response = ErrorResponse(
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        request_id=getattr(request.state, "request_id", "unknown"),
    )
    logger.warning(
        "File size exceeded",
        extra={"request_id": error_response.request_id, "error_code": exc.error_code},
    )
    return JSONResponse(
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        content=error_response.model_dump(),
    )


@app.exception_handler(InvalidFileFormatError)
async def invalid_format_error_handler(request: Request, exc: InvalidFileFormatError):
    """Handle invalid file format errors (400)."""
    error_response = ErrorResponse(
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        request_id=getattr(request.state, "request_id", "unknown"),
    )
    logger.warning(
        "Invalid file format",
        extra={"request_id": error_response.request_id, "error_code": exc.error_code},
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content=error_response.model_dump()
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors (400)."""
    error_response = ErrorResponse(
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        details={"validation_errors": exc.errors()},
        request_id=getattr(request.state, "request_id", "unknown"),
    )
    logger.warning(
        "Request validation error",
        extra={"request_id": error_response.request_id, "errors": exc.errors()},
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content=error_response.model_dump()
    )


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """
    Add unique request_id to each request for tracing.

    Required by RULE 5: Always use request_id for tracing.
    """
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # Add to response headers
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response


# Include API routes
app.include_router(router, tags=["Docling"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"service": "Docling", "version": "0.1.0", "status": "operational"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
