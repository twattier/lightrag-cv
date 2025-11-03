# Docling API Documentation

**Service**: Docling Document Parsing Service
**Version**: 0.1.0
**Base URL**: `http://localhost:8000` (or `DOCLING_PORT` from `.env`)

## Overview

The Docling service provides REST API endpoints for parsing PDF and DOCX documents into structured chunks using Docling's HybridChunker. The service supports both CPU and optional GPU acceleration.

## Table of Contents

- [Endpoints](#endpoints)
  - [POST /parse](#post-parse)
  - [GET /health](#get-health)
- [Error Handling](#error-handling)
- [Examples](#examples)

---

## Endpoints

### POST /parse

Parse a PDF or DOCX document into structured chunks.

**Endpoint**: `POST /parse`
**Content-Type**: `multipart/form-data`
**Timeout**: Recommended 60s for large documents

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | Yes | PDF or DOCX file to parse (max 50MB) |
| `options` | JSON string | No | Optional parsing options (currently unused) |

#### Response Format (200 OK)

```json
{
  "document_id": "uuid-v4-string",
  "chunks": [
    {
      "chunk_id": "chunk_0",
      "content": "Parsed text content of the chunk...",
      "chunk_type": "paragraph",
      "metadata": {
        "section": "Introduction",
        "page": 1,
        "token_count": 245
      }
    }
  ],
  "metadata": {
    "page_count": 10,
    "format": "PDF",
    "tables_extracted": 3,
    "processing_time_ms": 1500
  }
}
```

#### Response Fields

**Root Level:**
- `document_id` (string): Unique identifier for the processed document
- `chunks` (array): List of document chunks produced by HybridChunker
- `metadata` (object): Document-level metadata

**Chunk Object:**
- `chunk_id` (string): Unique identifier for the chunk (e.g., "chunk_0", "chunk_1")
- `content` (string): The actual text content of the chunk
- `chunk_type` (string): Type of content (e.g., "paragraph", "title", "table", "list_item")
- `metadata` (object): Chunk-specific metadata
  - `section` (string): Section heading for context (may be empty)
  - `page` (number): Page number where chunk appears
  - `token_count` (number): Number of tokens in the chunk

**Document Metadata:**
- `page_count` (number): Total number of pages in document
- `format` (string): Document format ("PDF" or "DOCX")
- `tables_extracted` (number): Number of tables detected
- `processing_time_ms` (number): Processing duration in milliseconds

#### Error Responses

**400 Bad Request - Invalid File Format:**
```json
{
  "error_code": "INVALID_FILE_FORMAT",
  "message": "Only PDF and DOCX files are supported",
  "details": {
    "filename": "document.txt",
    "supported_formats": ["PDF", "DOCX"]
  },
  "timestamp": "2025-11-03T10:30:00.000Z",
  "request_id": "abc123-def456",
  "service": "docling"
}
```

**413 Payload Too Large - File Size Exceeded:**
```json
{
  "error_code": "FILE_TOO_LARGE",
  "message": "File size (51.23MB) exceeds maximum allowed (50MB)",
  "details": {
    "file_size_bytes": 53687091,
    "file_size_mb": 51.23,
    "max_size_mb": 50,
    "filename": "large_document.pdf"
  },
  "timestamp": "2025-11-03T10:30:00.000Z",
  "request_id": "abc123-def456",
  "service": "docling"
}
```

**500 Internal Server Error - Parsing Failed:**
```json
{
  "error_code": "PARSING_FAILED",
  "message": "Failed to parse document: Invalid PDF structure",
  "details": {
    "document_id": "doc-uuid",
    "filename": "corrupted.pdf",
    "error": "Invalid PDF structure"
  },
  "timestamp": "2025-11-03T10:30:00.000Z",
  "request_id": "abc123-def456",
  "service": "docling"
}
```

#### curl Examples

**Parse a PDF document:**
```bash
curl -X POST http://localhost:8000/parse \
  -F "file=@/path/to/document.pdf" \
  -H "Accept: application/json"
```

**Parse a DOCX document:**
```bash
curl -X POST http://localhost:8000/parse \
  -F "file=@/path/to/document.docx" \
  -H "Accept: application/json"
```

**Parse with options (currently unused but supported):**
```bash
curl -X POST http://localhost:8000/parse \
  -F "file=@/path/to/document.pdf" \
  -F 'options={"custom_option": "value"}' \
  -H "Accept: application/json"
```

---

### GET /health

Check service health and GPU availability.

**Endpoint**: `GET /health`

#### Response Format (200 OK)

```json
{
  "status": "healthy",
  "gpu_available": true
}
```

#### Response Fields

- `status` (string): Service health status ("healthy" or "unhealthy")
- `gpu_available` (boolean): Whether GPU acceleration is available

#### curl Example

```bash
curl http://localhost:8000/health
```

**Example Response:**
```json
{
  "status": "healthy",
  "gpu_available": false
}
```

---

## Error Handling

All error responses follow a standardized format defined by the `ErrorResponse` model:

```json
{
  "error_code": "MACHINE_READABLE_CODE",
  "message": "Human-friendly error message",
  "details": {
    "additional": "context",
    "specific": "to error"
  },
  "timestamp": "2025-11-03T10:30:00.000Z",
  "request_id": "unique-request-id",
  "service": "docling"
}
```

### Error Codes

| HTTP Status | Error Code | Description |
|-------------|-----------|-------------|
| 400 | `INVALID_FILE_FORMAT` | File is not PDF or DOCX |
| 400 | `VALIDATION_ERROR` | Request validation failed |
| 413 | `FILE_TOO_LARGE` | File exceeds 50MB limit |
| 500 | `PARSING_FAILED` | Document parsing failed |
| 500 | `CONVERSION_FAILED` | Docling conversion failed |

### Request Tracing

All requests include a `X-Request-ID` header in the response for tracing and debugging:

```bash
curl -i http://localhost:8000/health
# Response headers will include:
# X-Request-ID: abc123-def456-789ghi
```

---

## Examples

### Example 1: Parse a Simple PDF

**Request:**
```bash
curl -X POST http://localhost:8000/parse \
  -F "file=@sample.pdf"
```

**Response (200 OK):**
```json
{
  "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "chunks": [
    {
      "chunk_id": "chunk_0",
      "content": "LightRAG-CV: A Hybrid RAG System for CV Analysis\n\nThis document describes the architecture and implementation of LightRAG-CV, a proof-of-concept system that combines vector and graph-based retrieval for intelligent CV analysis.",
      "chunk_type": "title",
      "metadata": {
        "section": "",
        "page": 1,
        "token_count": 42
      }
    },
    {
      "chunk_id": "chunk_1",
      "content": "The system leverages Docling for document parsing, LightRAG for hybrid retrieval, and provides an MCP interface for integration with AI agents like Claude Code.",
      "chunk_type": "paragraph",
      "metadata": {
        "section": "Introduction",
        "page": 1,
        "token_count": 35
      }
    },
    {
      "chunk_id": "chunk_2",
      "content": "Key Features:\n- PDF and DOCX document parsing\n- Hybrid vector-graph retrieval\n- PostgreSQL with pgvector and Apache AGE\n- MCP protocol integration",
      "chunk_type": "list_item",
      "metadata": {
        "section": "Introduction",
        "page": 1,
        "token_count": 28
      }
    }
  ],
  "metadata": {
    "page_count": 5,
    "format": "PDF",
    "tables_extracted": 2,
    "processing_time_ms": 2340
  }
}
```

### Example 2: Invalid File Format Error

**Request:**
```bash
curl -X POST http://localhost:8000/parse \
  -F "file=@document.txt"
```

**Response (400 Bad Request):**
```json
{
  "error_code": "INVALID_FILE_FORMAT",
  "message": "Only PDF and DOCX files are supported",
  "details": {
    "filename": "document.txt",
    "supported_formats": ["PDF", "DOCX"]
  },
  "timestamp": "2025-11-03T15:30:45.123Z",
  "request_id": "req-12345678-90ab-cdef",
  "service": "docling"
}
```

### Example 3: Chunk Structure Details

The HybridChunker produces intelligent chunks that preserve document structure:

**Table Chunk Example:**
```json
{
  "chunk_id": "chunk_5",
  "content": "| Technology | Version | Purpose |\n|------------|---------|----------|\n| Python | 3.11.x | Service implementation |\n| Docling | 1.16.2 | Document parsing |\n| LightRAG | 0.0.0.post8 | Hybrid RAG engine |",
  "chunk_type": "table",
  "metadata": {
    "section": "Tech Stack",
    "page": 3,
    "token_count": 58
  }
}
```

**Section Title Example:**
```json
{
  "chunk_id": "chunk_10",
  "content": "Architecture Overview",
  "chunk_type": "title",
  "metadata": {
    "section": "",
    "page": 4,
    "token_count": 3
  }
}
```

---

## Notes

- **File Size Limit**: 50MB maximum for POC. Larger files return HTTP 413.
- **GPU Support**: Optional. CPU mode is fully functional. Enable with `--profile gpu` in docker-compose.
- **HybridChunker**: Automatically detects document structure (headings, paragraphs, tables, lists) for intelligent chunking.
- **Async Processing**: All operations are async for optimal performance.
- **Request IDs**: Every request gets a unique ID for tracing through logs.

## OpenAPI Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

**Last Updated**: 2025-11-03
**Story**: [Story 2.1](../stories/story-2.1.md)
