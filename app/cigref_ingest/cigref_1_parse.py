#!/usr/bin/env python3
"""
Parse CIGREF PDF and enrich with hierarchical metadata.

Part of lightrag-cv application workflows.
Module: app.cigref_ingest.cigref_1_parse

This script:
1. Parses CIGREF PDF using Docling API (POST /parse)
2. Enriches chunks with hierarchy using enrich_chunks_with_hierarchy()
3. Removes domain_id and job_profile_id from metadata
4. Filters chunks: Keeps only chunks where domain != null OR job_profile != null
5. Groups chunks by domain
6. Adds document-level metadata
7. Saves result to settings.CIGREF_PARSED (clean JSON format)

Usage:
    python3 app/cigref_ingest/cigref_1_parse.py
    python3 app/cigref_ingest/cigref_1_parse.py --output /custom/path/output.json
    python -m app.cigref_ingest.cigref_1_parse
"""

import argparse
import asyncio
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add project root to Python path for direct script execution
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import httpx
import pdfplumber

from app.shared.config import settings


# Header extraction configuration
HEADER_HEIGHT = 50  # pixels from top of page

# Regex patterns for parsing headers
# Domain pattern: "3. APPLICATION LIFE CYCLE" or "1. STEERING, ORGANISING..."
DOMAIN_PATTERN = re.compile(r'^(\d+)\.\s+([A-Z\s,]+?)(?:\s+P\s?AGE|\s*$)', re.MULTILINE)

# Profile pattern: "3.5. SOFTWARE CONFIGURATION OFFICER"
PROFILE_PATTERN = re.compile(r'^(\d+\.\d+)\.\s+([A-Z\s]+?)(?:\s+P\s?AGE|\s*$)', re.MULTILINE)


def extract_page_header(page, header_height: int = HEADER_HEIGHT) -> str:
    """
    Extract text from the top header region of a page.

    Args:
        page: pdfplumber page object
        header_height: Height in points from top to extract

    Returns:
        Extracted header text (stripped)
    """
    header_bbox = (0, 0, page.width, header_height)
    header = page.crop(header_bbox)
    header_text = header.extract_text() or ""
    return header_text.strip()


def parse_domain_from_header(header_text: str) -> Optional[Tuple[str, str]]:
    """
    Parse domain ID and name from header text.

    Args:
        header_text: Header text extracted from page

    Returns:
        Tuple of (domain_id, domain_name) or None if not found

    Example:
        "3. APPLICATION LIFE CYCLE P AGE | 105" → ("3", "APPLICATION LIFE CYCLE")
    """
    match = DOMAIN_PATTERN.search(header_text)
    if match:
        domain_id = match.group(1).strip()
        domain_name = match.group(2).strip()
        return (domain_id, domain_name)
    return None


def parse_profile_from_header(header_text: str) -> Optional[Tuple[str, str]]:
    """
    Parse job profile ID and name from header text.

    Args:
        header_text: Header text extracted from page

    Returns:
        Tuple of (profile_id, profile_name) or None if not found

    Example:
        "3.5. SOFTWARE CONFIGURATION OFFICER" → ("3.5", "SOFTWARE CONFIGURATION OFFICER")
    """
    match = PROFILE_PATTERN.search(header_text)
    if match:
        profile_id = match.group(1).strip()
        profile_name = match.group(2).strip()
        return (profile_id, profile_name)
    return None


def build_page_hierarchy_map(pdf_path: Path) -> Dict[int, Dict[str, Optional[str]]]:
    """
    Build a mapping of page numbers to their hierarchical context.

    Args:
        pdf_path: Path to CIGREF PDF

    Returns:
        Dictionary mapping page_number → {domain_id, domain, job_profile_id, job_profile}

    Example:
        {
            111: {
                "domain_id": "3",
                "domain": "APPLICATION LIFE CYCLE",
                "job_profile_id": "3.5",
                "job_profile": "SOFTWARE CONFIGURATION OFFICER"
            }
        }
    """
    page_hierarchy = {}
    current_domain = None
    current_domain_id = None
    current_profile = None
    current_profile_id = None

    print(f"   Extracting headers from PDF: {pdf_path.name}")

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)

        for page_num in range(1, total_pages + 1):
            page = pdf.pages[page_num - 1]  # pdfplumber is 0-indexed

            # Extract header
            header_text = extract_page_header(page)

            # Parse domain from header
            domain_match = parse_domain_from_header(header_text)
            if domain_match:
                current_domain_id, current_domain = domain_match

            # Parse profile from header
            profile_match = parse_profile_from_header(header_text)
            if profile_match:
                current_profile_id, current_profile = profile_match
            # Note: If no profile in header, keep previous profile (carries over)

            # Store hierarchy for this page
            page_hierarchy[page_num] = {
                "domain_id": current_domain_id,
                "domain": current_domain,
                "job_profile_id": current_profile_id,
                "job_profile": current_profile
            }

            # Progress indicator
            if page_num % 50 == 0:
                print(f"      Processed {page_num}/{total_pages} pages...")

    return page_hierarchy


def enrich_chunks_with_hierarchy(
    chunks: List[Dict[str, Any]],
    page_hierarchy: Dict[int, Dict[str, Optional[str]]]
) -> List[Dict[str, Any]]:
    """
    Enrich chunks with hierarchical metadata from page context.

    Args:
        chunks: List of chunk dictionaries from parsed output
        page_hierarchy: Page number → hierarchy mapping

    Returns:
        Enriched chunks with domain/profile metadata added
    """
    enriched_chunks = []

    for chunk in chunks:
        # Copy chunk
        enriched_chunk = chunk.copy()

        # Get page number from chunk metadata
        page_num = chunk.get("metadata", {}).get("page", 1)

        # Get hierarchy for this page
        hierarchy = page_hierarchy.get(page_num, {})

        # Enrich metadata
        if "metadata" not in enriched_chunk:
            enriched_chunk["metadata"] = {}

        enriched_chunk["metadata"]["domain_id"] = hierarchy.get("domain_id")
        enriched_chunk["metadata"]["domain"] = hierarchy.get("domain")
        enriched_chunk["metadata"]["job_profile_id"] = hierarchy.get("job_profile_id")
        enriched_chunk["metadata"]["job_profile"] = hierarchy.get("job_profile")

        enriched_chunks.append(enriched_chunk)

    return enriched_chunks


async def parse_cigref_with_docling() -> Dict[str, Any]:
    """
    Parse CIGREF PDF using Docling API.

    Returns:
        Parsed data dictionary with chunks array

    Raises:
        httpx.HTTPStatusError: If API call fails
    """
    print(f"📄 Parsing CIGREF PDF: {settings.CIGREF_FILE.name}")
    print(f"   Using Docling service: {settings.docling_url}")

    # Read PDF file content
    with open(settings.CIGREF_FILE, "rb") as f:
        pdf_content = f.read()

    file_size_mb = len(pdf_content) / (1024 * 1024)
    print(f"   File size: {file_size_mb:.2f} MB")

    # Submit to Docling with file upload
    async with httpx.AsyncClient(timeout=settings.DOCLING_TIMEOUT) as client:
        response = await client.post(
            f"{settings.docling_url}/parse",
            files={"file": (settings.CIGREF_FILE.name, pdf_content, "application/pdf")},
        )
        response.raise_for_status()
        parsed_data = response.json()

    chunks = parsed_data.get("chunks", [])
    print(f"   ✓ Parsed {len(chunks)} chunks from Docling")

    return parsed_data


def remove_id_fields(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove domain_id and job_profile_id from chunk metadata.

    Args:
        chunks: List of enriched chunks

    Returns:
        Chunks with ID fields removed
    """
    for chunk in chunks:
        metadata = chunk.get("metadata", {})
        metadata.pop("domain_id", None)
        metadata.pop("job_profile_id", None)

    return chunks


def filter_relevant_chunks(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter chunks: Keep only where domain != null OR job_profile != null.

    Args:
        chunks: List of chunks

    Returns:
        Filtered chunks
    """
    filtered = [
        chunk
        for chunk in chunks
        if chunk.get("metadata", {}).get("domain")
        or chunk.get("metadata", {}).get("job_profile")
    ]

    print(f"   ✓ Filtered {len(chunks)} → {len(filtered)} chunks (removed chunks without domain/profile)")

    return filtered


def group_chunks_by_domain(chunks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group chunks by domain.

    Args:
        chunks: List of filtered chunks

    Returns:
        Dictionary mapping domain → list of chunks
    """
    groups = defaultdict(list)

    for chunk in chunks:
        domain = chunk.get("metadata", {}).get("domain", "UNKNOWN")
        groups[domain].append(chunk)

    print(f"\n📊 Grouped chunks into {len(groups)} domains:")
    for domain, domain_chunks in sorted(groups.items()):
        print(f"   • {domain}: {len(domain_chunks)} chunks")

    return dict(groups)


def add_document_metadata(grouped_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Add document-level metadata to grouped data.

    Args:
        grouped_data: Grouped chunks by domain

    Returns:
        Complete data structure with metadata
    """
    total_chunks = sum(len(chunks) for chunks in grouped_data.values())

    output_data = {
        "document_metadata": {
            "document_type": "cigref_nomenclature",
            "source_filename": settings.CIGREF_FILE.name,
            "source_path": str(settings.CIGREF_FILE),
            "total_domains": len(grouped_data),
            "total_chunks": total_chunks,
            "parsing_version": "1.0",
        },
        "domains": grouped_data,
    }

    return output_data


async def main_async(output_path: Path) -> int:
    """
    Main async entry point.

    Args:
        output_path: Path to save output JSON

    Returns:
        Exit code (0 for success)
    """
    print("🔧 CIGREF Parsing and Enrichment Workflow")
    print("=" * 60)

    # Step 1: Parse with Docling
    print("\n📡 Step 1: Parsing PDF with Docling API...")
    parsed_data = await parse_cigref_with_docling()
    chunks = parsed_data.get("chunks", [])

    # Step 2: Build page hierarchy
    print("\n🔍 Step 2: Building page hierarchy map...")
    page_hierarchy = build_page_hierarchy_map(settings.CIGREF_FILE)
    print(f"   ✓ Built hierarchy for {len(page_hierarchy)} pages")

    # Step 3: Enrich chunks
    print(f"\n🔄 Step 3: Enriching {len(chunks)} chunks with hierarchy...")
    enriched_chunks = enrich_chunks_with_hierarchy(chunks, page_hierarchy)
    print(f"   ✓ Enrichment complete")

    # Step 4: Remove ID fields
    print("\n🧹 Step 4: Removing domain_id and job_profile_id fields...")
    enriched_chunks = remove_id_fields(enriched_chunks)
    print(f"   ✓ ID fields removed")

    # Step 5: Filter relevant chunks
    print("\n🔍 Step 5: Filtering chunks...")
    filtered_chunks = filter_relevant_chunks(enriched_chunks)

    # Step 6: Group by domain
    print("\n📦 Step 6: Grouping chunks by domain...")
    grouped_data = group_chunks_by_domain(filtered_chunks)

    # Step 7: Add document metadata
    print("\n📋 Step 7: Adding document-level metadata...")
    output_data = add_document_metadata(grouped_data)
    print(f"   ✓ Metadata added")

    # Step 8: Save output
    print(f"\n💾 Step 8: Saving output to {output_path.name}...")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    file_size_kb = output_path.stat().st_size / 1024
    print(f"   ✓ Saved to {output_path}")
    print(f"   File size: {file_size_kb:.2f} KB")

    # Summary
    print("\n" + "=" * 60)
    print("✅ PARSING COMPLETE!")
    print(f"\n📁 Output: {output_path}")
    print(f"📊 Total domains: {output_data['document_metadata']['total_domains']}")
    print(f"📄 Total chunks: {output_data['document_metadata']['total_chunks']}")

    return 0


def main() -> int:
    """
    Main entry point with CLI argument parsing.

    Returns:
        Exit code (0 for success)
    """
    parser = argparse.ArgumentParser(
        description="Parse CIGREF PDF and enrich with hierarchical metadata"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=settings.CIGREF_PARSED,
        help=f"Output JSON file path (default: {settings.CIGREF_PARSED})",
    )

    args = parser.parse_args()

    try:
        return asyncio.run(main_async(args.output))
    except Exception as e:
        print(f"\n❌ ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
