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
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

# Add project root to Python path for direct script execution
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import httpx

from app.cigref_ingest.enrich_cigref_hierarchy import (
    build_page_hierarchy_map,
    enrich_chunks_with_hierarchy,
)
from app.shared.config import settings


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
