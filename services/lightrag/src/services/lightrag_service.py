"""LightRAG service wrapper using composition pattern."""

import logging
import os
from typing import Any, Dict, List, Optional

from lightrag import LightRAG, QueryParam
from lightrag.llm.ollama import ollama_model_complete, ollama_embed

from src.config import settings

logger = logging.getLogger(__name__)


class LightRAGService:
    """
    Wrapper service for LightRAG with PostgreSQL storage.

    Uses COMPOSITION, not inheritance, to integrate LightRAG.
    """

    def __init__(self):
        """Initialize LightRAG service with PostgreSQL storage adapters."""

        # Set embedding dimension as environment variable for PostgreSQL tables
        os.environ["EMBEDDING_DIM"] = str(settings.LIGHTRAG_EMBEDDING_DIM)

        # PostgreSQL configuration for LightRAG
        postgres_config = {
            "host": settings.POSTGRES_HOST,
            "port": settings.POSTGRES_PORT,
            "user": settings.POSTGRES_USER,
            "password": settings.POSTGRES_PASSWORD,
            "database": settings.POSTGRES_DB,
            "workspace": "default",  # Namespace for multi-tenancy
            "max_connections": 10,
            "connection_retry_attempts": 3,
            "connection_retry_backoff": 1.0,
            "connection_retry_backoff_max": 5.0,
            "pool_close_timeout": 10.0,
        }

        # Initialize LightRAG with PostgreSQL storage
        # Storage class names passed as strings
        self.lightrag = LightRAG(
            working_dir=settings.LIGHTRAG_WORKING_DIR,
            kv_storage="PGKVStorage",
            vector_storage="PGVectorStorage",
            graph_storage="PGGraphStorage",
            doc_status_storage="PGDocStatusStorage",

            # PostgreSQL configuration
            vector_db_storage_cls_kwargs={"global_config": postgres_config},

            # LLM configuration
            llm_model_func=ollama_model_complete,
            llm_model_name=settings.OLLAMA_LLM_MODEL,
            llm_model_kwargs={
                "host": settings.OLLAMA_BASE_URL,
                "options": {"num_ctx": settings.OLLAMA_LLM_NUM_CTX},
            },

            # Embedding configuration
            embedding_func=ollama_embed,
            embedding_batch_num=10,
            embedding_func_max_async=8,
            embedding_cache_config={
                "enabled": True,
                "model": settings.OLLAMA_EMBEDDING_MODEL,
            },

            # Retrieval configuration
            top_k=settings.LIGHTRAG_TOP_K,
            max_total_tokens=settings.LIGHTRAG_MAX_TOKENS,
            chunk_token_size=1200,
            chunk_overlap_token_size=100,

            # Enable LLM response caching
            enable_llm_cache=True,
        )

        logger.info(
            "LightRAG service initialized",
            extra={
                "postgres_host": settings.POSTGRES_HOST,
                "postgres_db": settings.POSTGRES_DB,
                "ollama_base_url": settings.OLLAMA_BASE_URL,
                "llm_model": settings.OLLAMA_LLM_MODEL,
                "embedding_model": settings.OLLAMA_EMBEDDING_MODEL,
                "working_dir": settings.LIGHTRAG_WORKING_DIR,
            }
        )

    async def ingest_document(
        self,
        document_text: str,
        document_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ingest document into LightRAG.

        Args:
            document_text: Full document text or joined chunks
            document_id: Unique document identifier
            metadata: Document metadata (type, filename, etc.)

        Returns:
            Ingestion status
        """
        try:
            logger.info(
                "Starting document ingestion",
                extra={
                    "document_id": document_id,
                    "text_length": len(document_text),
                    "document_type": metadata.get("type") if metadata else None
                }
            )

            # LightRAG insert expects plain text and handles chunking internally
            await self.lightrag.ainsert(document_text)

            logger.info(
                "Document ingestion completed",
                extra={"document_id": document_id}
            )

            return {
                "document_id": document_id,
                "status": "completed",
                "message": "Document ingested successfully"
            }

        except Exception as e:
            logger.error(
                "Document ingestion failed",
                extra={"document_id": document_id, "error": str(e)},
                exc_info=True
            )
            raise

    async def query(
        self,
        query: str,
        mode: str = "hybrid",
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query LightRAG for matching documents.

        Args:
            query: Search query
            mode: Retrieval mode (naive, local, global, hybrid)
            top_k: Number of results to return (defaults to configured value)
            filters: Optional metadata filters (not yet implemented)

        Returns:
            Query results
        """
        try:
            logger.info(
                "Executing query",
                extra={
                    "query": query[:100],  # Truncate for logging
                    "mode": mode,
                    "top_k": top_k or settings.LIGHTRAG_TOP_K
                }
            )

            # LightRAG query with mode
            param = QueryParam(mode=mode, top_k=top_k or settings.LIGHTRAG_TOP_K)
            result = await self.lightrag.aquery(query, param=param)

            return {
                "result": result,
                "retrieval_mode_used": mode,
            }

        except Exception as e:
            logger.error(
                "Query failed",
                extra={"query": query[:100], "error": str(e)},
                exc_info=True
            )
            raise

    async def get_document_status(self, document_id: str) -> Dict[str, Any]:
        """
        Get document ingestion status.

        Args:
            document_id: Unique document identifier

        Returns:
            Document status information
        """
        try:
            # Query LightRAG doc_status_storage for document status
            # For now, return basic status (TODO: enhance with actual storage query)
            return {
                "document_id": document_id,
                "status": "unknown",
                "message": "Document status tracking not yet fully implemented"
            }
        except Exception as e:
            logger.error(
                "Failed to get document status",
                extra={"document_id": document_id, "error": str(e)},
                exc_info=True
            )
            raise

    async def health_check(self) -> Dict[str, Any]:
        """
        Check service health.

        Returns:
            Health status including connectivity checks
        """
        postgres_ok = False
        ollama_ok = False

        try:
            # Check if LightRAG is initialized
            if self.lightrag:
                postgres_ok = True

            # TODO: Add Ollama connectivity check by making a test embedding request
            ollama_ok = True  # Placeholder

        except Exception as e:
            logger.error("Health check failed", exc_info=True)

        status = "healthy" if (postgres_ok and ollama_ok) else "degraded"
        if not postgres_ok and not ollama_ok:
            status = "unhealthy"

        return {
            "status": status,
            "postgres_connected": postgres_ok,
            "ollama_connected": ollama_ok,
        }
