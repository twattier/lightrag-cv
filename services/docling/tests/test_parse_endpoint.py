#!/usr/bin/env python3
"""
Test script for Docling parse endpoint.

Tests:
- POST /parse with valid PDF (200 OK, chunks present)
- POST /parse with valid DOCX (200 OK, chunks present)
- POST /parse with invalid file format (400 Bad Request)
- POST /parse with oversized file (413 Payload Too Large)
- GET /health endpoint (200 OK)
- Verify HybridChunker produces structured chunks

Usage:
    pytest services/docling/tests/test_parse_endpoint.py
    # or
    python services/docling/tests/test_parse_endpoint.py
"""

import asyncio
import io
import sys
from pathlib import Path

import httpx
import pytest

# Test configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 60.0  # Increased for document processing


class TestDoclingAPI:
    """Test suite for Docling API endpoints."""

    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Test GET /health endpoint returns 200 OK."""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(f"{BASE_URL}/health")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert "status" in data, "Response missing 'status' field"
        assert "gpu_available" in data, "Response missing 'gpu_available' field"
        assert data["status"] in ["healthy", "unhealthy"], (
            f"Invalid status: {data['status']}"
        )

        print(f"✅ Health check passed: {data}")

    @pytest.mark.asyncio
    async def test_parse_valid_pdf(self):
        """
        Test POST /parse with valid PDF file.

        Expected: 200 OK with chunks and metadata.
        """
        # Create a minimal test PDF (you can replace with actual test file)
        # For now, we'll test with a sample PDF from data directory
        test_pdf_path = Path("data/cigref/cigref_referentiel.pdf")

        if not test_pdf_path.exists():
            pytest.skip(f"Test PDF not found at {test_pdf_path}")

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            with open(test_pdf_path, "rb") as f:
                files = {"file": (test_pdf_path.name, f, "application/pdf")}
                response = await client.post(f"{BASE_URL}/parse", files=files)

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()

        # Validate response structure
        assert "document_id" in data, "Missing document_id"
        assert "chunks" in data, "Missing chunks"
        assert "metadata" in data, "Missing metadata"

        # Validate chunks
        assert isinstance(data["chunks"], list), "Chunks should be a list"
        assert len(data["chunks"]) > 0, "Should have at least one chunk"

        # Validate chunk structure
        first_chunk = data["chunks"][0]
        assert "chunk_id" in first_chunk, "Chunk missing chunk_id"
        assert "content" in first_chunk, "Chunk missing content"
        assert "chunk_type" in first_chunk, "Chunk missing chunk_type"
        assert "metadata" in first_chunk, "Chunk missing metadata"

        # Validate metadata
        metadata = data["metadata"]
        assert "page_count" in metadata, "Missing page_count in metadata"
        assert "format" in metadata, "Missing format in metadata"
        assert "tables_extracted" in metadata, "Missing tables_extracted in metadata"
        assert "processing_time_ms" in metadata, (
            "Missing processing_time_ms in metadata"
        )
        assert metadata["format"] == "PDF", (
            f"Expected format 'PDF', got {metadata['format']}"
        )

        print("✅ PDF parsing test passed:")
        print(f"   - Document ID: {data['document_id']}")
        print(f"   - Chunks: {len(data['chunks'])}")
        print(f"   - Pages: {metadata['page_count']}")
        print(f"   - Tables: {metadata['tables_extracted']}")
        print(f"   - Processing time: {metadata['processing_time_ms']}ms")

    @pytest.mark.asyncio
    async def test_parse_valid_docx(self):
        """
        Test POST /parse with valid DOCX file.

        Expected: 200 OK with chunks and metadata.
        """
        # Create minimal DOCX-like test file
        # For real testing, use actual DOCX from test data
        test_docx_path = Path("data/cvs/sample.docx")

        if not test_docx_path.exists():
            pytest.skip(f"Test DOCX not found at {test_docx_path}")

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            with open(test_docx_path, "rb") as f:
                files = {
                    "file": (
                        "test.docx",
                        f,
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )
                }
                response = await client.post(f"{BASE_URL}/parse", files=files)

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert "chunks" in data, "Missing chunks in response"
        assert len(data["chunks"]) > 0, "Should have at least one chunk"
        assert data["metadata"]["format"] == "DOCX", (
            f"Expected format 'DOCX', got {data['metadata']['format']}"
        )

        print(f"✅ DOCX parsing test passed: {len(data['chunks'])} chunks")

    @pytest.mark.asyncio
    async def test_parse_invalid_format(self):
        """
        Test POST /parse with invalid file format (e.g., .txt).

        Expected: 400 Bad Request with error details.
        """
        # Create a fake text file
        fake_txt_content = b"This is a plain text file, not a PDF or DOCX."

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            files = {"file": ("test.txt", io.BytesIO(fake_txt_content), "text/plain")}
            response = await client.post(f"{BASE_URL}/parse", files=files)

        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

        data = response.json()
        assert "error_code" in data, "Missing error_code in error response"
        assert data["error_code"] == "INVALID_FILE_FORMAT", (
            f"Expected INVALID_FILE_FORMAT, got {data['error_code']}"
        )
        assert "message" in data, "Missing message in error response"
        assert "request_id" in data, "Missing request_id for tracing"

        print(f"✅ Invalid format test passed: {data['error_code']}")

    @pytest.mark.asyncio
    async def test_parse_oversized_file(self):
        """
        Test POST /parse with file exceeding 50MB limit.

        Expected: 413 Payload Too Large with error details.
        """
        # Create a fake oversized PDF (51MB of zeros)
        oversized_content = b"\x00" * (51 * 1024 * 1024)

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            files = {
                "file": ("huge.pdf", io.BytesIO(oversized_content), "application/pdf")
            }
            response = await client.post(f"{BASE_URL}/parse", files=files)

        assert response.status_code == 413, f"Expected 413, got {response.status_code}"

        data = response.json()
        assert "error_code" in data, "Missing error_code in error response"
        assert data["error_code"] == "FILE_TOO_LARGE", (
            f"Expected FILE_TOO_LARGE, got {data['error_code']}"
        )
        assert "message" in data, "Missing message in error response"
        assert "details" in data, "Missing details in error response"

        # Verify details include file size info
        details = data["details"]
        assert "file_size_mb" in details, "Missing file_size_mb in details"
        assert "max_size_mb" in details, "Missing max_size_mb in details"

        print(f"✅ Oversized file test passed: {data['error_code']}")
        print(f"   - File size: {details['file_size_mb']}MB")
        print(f"   - Max allowed: {details['max_size_mb']}MB")

    @pytest.mark.asyncio
    async def test_hybrid_chunker_structure(self):
        """
        Verify HybridChunker produces structured chunks with metadata.

        Expected: Chunks contain section, page, and token count metadata.
        """
        test_pdf_path = Path("data/cigref/cigref_referentiel.pdf")

        if not test_pdf_path.exists():
            pytest.skip(f"Test PDF not found at {test_pdf_path}")

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            with open(test_pdf_path, "rb") as f:
                files = {"file": (test_pdf_path.name, f, "application/pdf")}
                response = await client.post(f"{BASE_URL}/parse", files=files)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        chunks = data["chunks"]

        # Verify chunk metadata structure
        for i, chunk in enumerate(chunks[:5]):  # Check first 5 chunks
            assert "metadata" in chunk, f"Chunk {i} missing metadata"
            chunk_meta = chunk["metadata"]

            # Verify metadata fields (may be empty but should exist)
            assert "section" in chunk_meta, f"Chunk {i} missing section in metadata"
            assert "page" in chunk_meta, f"Chunk {i} missing page in metadata"

            # Verify chunk has meaningful content
            assert len(chunk["content"]) > 0, f"Chunk {i} has empty content"

            print(
                f"   Chunk {i}: type={chunk['chunk_type']}, page={chunk_meta.get('page', 'N/A')}, len={len(chunk['content'])}"
            )

        print(
            f"✅ HybridChunker structure test passed: verified {min(5, len(chunks))} chunks"
        )


async def run_tests():
    """Run all tests manually (without pytest)."""
    test_suite = TestDoclingAPI()

    tests = [
        ("Health check", test_suite.test_health_endpoint),
        ("Parse valid PDF", test_suite.test_parse_valid_pdf),
        ("Parse valid DOCX", test_suite.test_parse_valid_docx),
        ("Invalid file format", test_suite.test_parse_invalid_format),
        ("Oversized file", test_suite.test_parse_oversized_file),
        ("HybridChunker structure", test_suite.test_hybrid_chunker_structure),
    ]

    print("=" * 60)
    print("Running Docling API Tests")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}\n")

    passed = 0
    failed = 0
    skipped = 0

    for test_name, test_func in tests:
        try:
            print(f"\n▶ Running: {test_name}")
            await test_func()
            passed += 1
        except pytest.skip.Exception as e:
            print(f"⚠ Skipped: {e}")
            skipped += 1
        except AssertionError as e:
            print(f"❌ Failed: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ Error: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    # Allow running directly without pytest
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
