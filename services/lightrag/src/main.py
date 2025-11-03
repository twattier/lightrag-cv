"""FastAPI application for LightRAG service."""

import logging
import sys
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router, set_service
from src.config import settings
from src.services import LightRAGService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting LightRAG service")
    logger.info(
        "Configuration loaded",
        extra={
            "postgres_host": settings.POSTGRES_HOST,
            "ollama_base_url": settings.OLLAMA_BASE_URL,
            "llm_model": settings.OLLAMA_LLM_MODEL
        }
    )

    # Initialize LightRAG service
    service = LightRAGService()
    set_service(service)

    logger.info("LightRAG service ready")

    yield

    # Shutdown
    logger.info("Shutting down LightRAG service")


# Create FastAPI app
app = FastAPI(
    title="LightRAG Service",
    description="Hybrid RAG with PostgreSQL storage for CV candidate search",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(router, tags=["LightRAG"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "LightRAG",
        "version": "0.1.0",
        "status": "operational"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9621)
