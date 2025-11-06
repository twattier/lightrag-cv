#!/usr/bin/env python3
"""
Test CIGREF PDF parsing via Docling REST API.

Part of lightrag-cv application workflows.
Module: app.cigref_ingest.test_cigref_parsing

This script:
1. Reads the CIGREF IT Profile Nomenclature PDF (English 2024 edition)
2. Submits it to the Docling /parse endpoint
3. Validates the response structure
4. Saves raw output to /data/cigref/cigref-parsed-raw.json for manual inspection
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any

import httpx


# Configuration
DOCLING_URL = "http://localhost:8001/parse"
CIGREF_PDF_PATH = Path("/home/wsluser/dev/lightrag-cv/data/cigref/Cigref_Nomenclature_des_profils_metiers_SI_EN_2024.pdf")
OUTPUT_RAW_JSON = Path("/home/wsluser/dev/lightrag-cv/data/cigref/cigref-parsed-raw.json")
REQUEST_TIMEOUT = 900.0  # 15 minutes for large PDF (4.8MB, ~14min observed)


async def test_parse_cigref() -> Dict[str, Any]:
    """
    Parse CIGREF PDF and validate response.

    Returns:
        Parsed response data as dictionary

    Raises:
        FileNotFoundError: If CIGREF PDF not found
        httpx.HTTPStatusError: If Docling returns non-200 status
        ValueError: If response structure is invalid
    """
    # Validate PDF exists
    if not CIGREF_PDF_PATH.exists():
        raise FileNotFoundError(f"CIGREF PDF not found: {CIGREF_PDF_PATH}")

    print(f"📄 Reading CIGREF PDF: {CIGREF_PDF_PATH.name}")
    print(f"   File size: {CIGREF_PDF_PATH.stat().st_size / (1024*1024):.2f} MB")

    # Submit to Docling
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        with open(CIGREF_PDF_PATH, "rb") as f:
            print(f"\n🚀 Submitting to Docling: {DOCLING_URL}")

            response = await client.post(
                DOCLING_URL,
                files={"file": (CIGREF_PDF_PATH.name, f, "application/pdf")}
            )

    # Validate status code
    print(f"   Response status: {response.status_code}")
    response.raise_for_status()

    # Parse JSON response
    data = response.json()

    # Validate response structure
    print(f"\n✅ Validating response structure...")
    assert "document_id" in data, "Missing 'document_id' in response"
    assert "chunks" in data, "Missing 'chunks' in response"
    assert "metadata" in data, "Missing 'metadata' in response"
    assert isinstance(data["chunks"], list), "'chunks' must be a list"
    assert len(data["chunks"]) > 0, "'chunks' array is empty"

    # Extract metrics
    chunk_count = len(data["chunks"])
    page_count = data["metadata"].get("page_count", "N/A")
    processing_time = data["metadata"].get("processing_time_ms", "N/A")
    tables_extracted = data["metadata"].get("tables_extracted", 0)

    print(f"   Document ID: {data['document_id']}")
    print(f"   Total chunks: {chunk_count}")
    print(f"   Page count: {page_count}")
    print(f"   Processing time: {processing_time} ms")
    print(f"   Tables extracted: {tables_extracted}")

    # Save raw output
    print(f"\n💾 Saving raw output to: {OUTPUT_RAW_JSON}")
    OUTPUT_RAW_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_RAW_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ CIGREF parsing test PASSED")
    print(f"\n📊 Summary:")
    print(f"   ✓ Response structure valid")
    print(f"   ✓ {chunk_count} chunks extracted")
    print(f"   ✓ {page_count} pages processed")
    print(f"   ✓ Raw output saved to {OUTPUT_RAW_JSON.name}")

    return data


async def main():
    """Main entry point for test script."""
    try:
        await test_parse_cigref()
    except FileNotFoundError as e:
        print(f"\n❌ ERROR: {e}")
        return 1
    except httpx.HTTPStatusError as e:
        print(f"\n❌ HTTP ERROR: {e.response.status_code}")
        print(f"   Response: {e.response.text}")
        return 1
    except ValueError as e:
        print(f"\n❌ VALIDATION ERROR: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {type(e).__name__}: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
