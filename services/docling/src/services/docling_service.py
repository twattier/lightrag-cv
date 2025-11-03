"""Docling service wrapper using composition pattern."""

import asyncio
import logging
import time
import uuid
from io import BytesIO
from typing import Any, Dict

from docling.chunking import HybridChunker
from docling.datamodel.base_models import DocumentStream, InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    WordFormatOption,
)
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from transformers import AutoTokenizer

from src.config import settings
from src.services.exceptions import DocumentParsingError

logger = logging.getLogger(__name__)


class DoclingService:
    """
    Wrapper service for Docling document parsing.

    Uses COMPOSITION, not inheritance, to integrate Docling.
    Follows RULE 10: Docling is treated as a black box.
    """

    def __init__(self):
        """Initialize Docling service with HybridChunker."""
        self.gpu_available = self._check_gpu_available()

        # Configure PDF pipeline options
        pdf_pipeline_options = PdfPipelineOptions()
        pdf_pipeline_options.do_ocr = True
        pdf_pipeline_options.do_table_structure = True
        pdf_pipeline_options.generate_page_images = False  # Save memory for POC

        # Initialize DocumentConverter with format-specific options
        # Uses composition pattern - NOT extending Docling classes
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_pipeline_options),
                InputFormat.DOCX: WordFormatOption(),
            }
        )

        # Initialize HybridChunker for intelligent content segmentation
        # Using BAAI/bge-m3 tokenizer to match the embedding model (bge-m3:latest from Ollama)
        # Configure tokenizer explicitly with max_tokens to match MAX_CHUNK_SIZE setting
        tokenizer = HuggingFaceTokenizer(
            tokenizer=AutoTokenizer.from_pretrained("BAAI/bge-m3"),
            max_tokens=settings.MAX_CHUNK_SIZE,
        )
        self.chunker = HybridChunker(
            tokenizer=tokenizer,
            merge_peers=True,
        )

        logger.info(
            "Docling service initialized",
            extra={
                "gpu_available": self.gpu_available,
                "max_chunk_size": settings.MAX_CHUNK_SIZE,
                "chunk_overlap": settings.CHUNK_OVERLAP,
            },
        )

    def _check_gpu_available(self) -> bool:
        """Check if GPU is available for Docling."""
        if not settings.GPU_ENABLED:
            return False

        try:
            import torch

            return torch.cuda.is_available()
        except ImportError:
            return False

    async def parse_document(
        self, file_content: bytes, filename: str, options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Parse document and extract chunks using Docling + HybridChunker.

        Args:
            file_content: Binary content of PDF/DOCX file
            filename: Original filename
            options: Optional parsing options (currently unused)

        Returns:
            Parsed document with chunks and metadata

        Raises:
            DocumentParsingError: If document parsing fails
        """
        start_time = time.time()
        document_id = str(uuid.uuid4())
        options = options or {}

        try:
            logger.info(
                "Starting document parsing",
                extra={
                    "document_id": document_id,
                    "document_filename": filename,
                    "size_bytes": len(file_content),
                },
            )

            # Determine file format
            file_format = "PDF" if filename.lower().endswith(".pdf") else "DOCX"

            # Create DocumentStream from bytes
            # Docling API uses streams for in-memory processing
            buf = BytesIO(file_content)
            source = DocumentStream(name=filename, stream=buf)

            # Convert document using Docling (sync operation, run in executor)
            # This is CPU/IO intensive, so we run it in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.converter.convert, source)

            # Check conversion status
            if result.status.name != "SUCCESS":
                raise DocumentParsingError(
                    message=f"Document conversion failed with status: {result.status.name}",
                    error_code="CONVERSION_FAILED",
                    details={"status": result.status.name, "filename": filename},
                )

            doc = result.document

            # Extract basic metadata from Docling document
            page_count = getattr(doc, "page_count", 0) or 0

            # Count tables in document
            tables_extracted = 0
            if hasattr(doc, "tables") and doc.tables:
                tables_extracted = len(doc.tables)

            # Chunk document using HybridChunker
            # Run chunking in executor as it can be CPU intensive
            chunk_iter = await loop.run_in_executor(None, self.chunker.chunk, doc)

            # Process chunks
            chunks = []
            for idx, chunk in enumerate(chunk_iter):
                chunk_data = {
                    "chunk_id": f"chunk_{idx}",
                    "content": chunk.text,
                    "chunk_type": chunk.meta.doc_items[0].label
                    if chunk.meta.doc_items
                    else "paragraph",
                    "metadata": {
                        "section": chunk.meta.headings[0]
                        if chunk.meta.headings
                        else "",
                        "page": chunk.meta.doc_items[0].prov[0].page_no
                        if chunk.meta.doc_items and chunk.meta.doc_items[0].prov
                        else 1,
                        "token_count": self.chunker.tokenizer.count_tokens(chunk.text)
                        if hasattr(self.chunker, "tokenizer")
                        and hasattr(self.chunker.tokenizer, "count_tokens")
                        else len(
                            chunk.text.split()
                        ),  # Fallback: approximate by word count
                    },
                }
                chunks.append(chunk_data)

            processing_time_ms = int((time.time() - start_time) * 1000)

            logger.info(
                "Document parsed successfully",
                extra={
                    "document_id": document_id,
                    "chunk_count": len(chunks),
                    "page_count": page_count,
                    "tables_extracted": tables_extracted,
                    "processing_time_ms": processing_time_ms,
                },
            )

            return {
                "document_id": document_id,
                "chunks": chunks,
                "metadata": {
                    "page_count": page_count,
                    "format": file_format,
                    "tables_extracted": tables_extracted,
                    "processing_time_ms": processing_time_ms,
                },
            }

        except DocumentParsingError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            logger.error(
                "Document parsing failed",
                extra={"document_id": document_id, "error": str(e)},
                exc_info=True,
            )
            raise DocumentParsingError(
                message=f"Failed to parse document: {str(e)}",
                error_code="PARSING_FAILED",
                details={
                    "document_id": document_id,
                    "filename": filename,
                    "error": str(e),
                },
            )

    async def health_check(self) -> Dict[str, Any]:
        """
        Check service health.

        Returns:
            Health status including GPU availability
        """
        try:
            # Verify Docling converter is initialized
            if not hasattr(self, "converter") or self.converter is None:
                return {"status": "unhealthy", "gpu_available": False}

            # Verify chunker is initialized
            if not hasattr(self, "chunker") or self.chunker is None:
                return {"status": "unhealthy", "gpu_available": False}

            status = "healthy"

            return {"status": status, "gpu_available": self.gpu_available}

        except Exception:
            logger.error("Health check failed", exc_info=True)
            return {"status": "unhealthy", "gpu_available": False}
