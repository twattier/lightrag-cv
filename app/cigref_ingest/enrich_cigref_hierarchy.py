#!/usr/bin/env python3
"""
Enrich CIGREF parsed output with hierarchical content tree metadata.

Part of lightrag-cv application workflows.
Module: app.cigref_ingest.enrich_cigref_hierarchy

This script:
1. Extracts page headers from CIGREF PDF using pdfplumber
2. Parses domain and job profile information from headers
3. Maps page numbers to their domain/profile context
4. Enriches chunk metadata with hierarchical information
5. Outputs cigref-enriched.json with complete metadata

Usage:
    python -m app.cigref_ingest.enrich_cigref_hierarchy
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import pdfplumber


# Configuration
CIGREF_PDF_PATH = Path("/home/wsluser/dev/lightrag-cv/data/cigref/Cigref_Nomenclature_des_profils_metiers_SI_EN_2024.pdf")
INPUT_PARSED_JSON = Path("/home/wsluser/dev/lightrag-cv/data/cigref/cigref-parsed-raw.json")
OUTPUT_ENRICHED_JSON = Path("/home/wsluser/dev/lightrag-cv/data/cigref/cigref-enriched.json")

# Header extraction height (pixels from top of page)
HEADER_HEIGHT = 50

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

    print(f"📄 Extracting headers from PDF: {pdf_path.name}")

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
                print(f"   Processed {page_num}/{total_pages} pages...")

    print(f"   ✓ Extracted headers from {total_pages} pages")

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


def validate_enrichment(
    enriched_chunks: List[Dict[str, Any]],
    page_hierarchy: Dict[int, Dict[str, Optional[str]]]
) -> Dict[str, Any]:
    """
    Validate enrichment quality and generate statistics.

    Args:
        enriched_chunks: Enriched chunks
        page_hierarchy: Page hierarchy map

    Returns:
        Validation statistics dictionary
    """
    total_chunks = len(enriched_chunks)
    chunks_with_domain = 0
    chunks_with_profile = 0
    unique_domains = set()
    unique_profiles = set()

    for chunk in enriched_chunks:
        metadata = chunk.get("metadata", {})

        if metadata.get("domain"):
            chunks_with_domain += 1
            unique_domains.add(metadata["domain"])

        if metadata.get("job_profile"):
            chunks_with_profile += 1
            unique_profiles.add(metadata["job_profile"])

    # Count pages with hierarchy
    pages_with_domain = sum(1 for h in page_hierarchy.values() if h.get("domain"))
    pages_with_profile = sum(1 for h in page_hierarchy.values() if h.get("job_profile"))

    return {
        "total_chunks": total_chunks,
        "chunks_with_domain": chunks_with_domain,
        "chunks_with_profile": chunks_with_profile,
        "unique_domains": len(unique_domains),
        "unique_profiles": len(unique_profiles),
        "pages_with_domain": pages_with_domain,
        "pages_with_profile": pages_with_profile,
        "domain_coverage_pct": round(chunks_with_domain / total_chunks * 100, 2),
        "profile_coverage_pct": round(chunks_with_profile / total_chunks * 100, 2)
    }


def main():
    """Main entry point."""
    print("🔧 CIGREF Hierarchical Metadata Enrichment")
    print("=" * 60)

    # Load parsed chunks
    print(f"\n📂 Loading parsed chunks: {INPUT_PARSED_JSON.name}")
    with open(INPUT_PARSED_JSON, "r", encoding="utf-8") as f:
        parsed_data = json.load(f)

    chunks = parsed_data.get("chunks", [])
    print(f"   ✓ Loaded {len(chunks)} chunks")

    # Build page hierarchy map
    print(f"\n🔍 Building page hierarchy map...")
    page_hierarchy = build_page_hierarchy_map(CIGREF_PDF_PATH)

    # Sample verification - check page 111
    page_111_hierarchy = page_hierarchy.get(111, {})
    print(f"\n✓ Sample verification (Page 111):")
    print(f"   Domain: {page_111_hierarchy.get('domain_id')}. {page_111_hierarchy.get('domain')}")
    print(f"   Profile: {page_111_hierarchy.get('job_profile_id')}. {page_111_hierarchy.get('job_profile')}")

    # Enrich chunks
    print(f"\n🔄 Enriching {len(chunks)} chunks with hierarchy...")
    enriched_chunks = enrich_chunks_with_hierarchy(chunks, page_hierarchy)
    print(f"   ✓ Enrichment complete")

    # Validate enrichment
    print(f"\n📊 Validating enrichment quality...")
    stats = validate_enrichment(enriched_chunks, page_hierarchy)

    print(f"\n   Total chunks: {stats['total_chunks']}")
    print(f"   Chunks with domain: {stats['chunks_with_domain']} ({stats['domain_coverage_pct']}%)")
    print(f"   Chunks with profile: {stats['chunks_with_profile']} ({stats['profile_coverage_pct']}%)")
    print(f"   Unique domains: {stats['unique_domains']}")
    print(f"   Unique profiles: {stats['unique_profiles']}")

    # Save enriched output
    print(f"\n💾 Saving enriched data: {OUTPUT_ENRICHED_JSON.name}")
    enriched_data = parsed_data.copy()
    enriched_data["chunks"] = enriched_chunks
    enriched_data["enrichment_metadata"] = {
        "enrichment_version": "1.0",
        "hierarchy_source": "pdf_header_extraction",
        "statistics": stats
    }

    OUTPUT_ENRICHED_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_ENRICHED_JSON, "w", encoding="utf-8") as f:
        json.dump(enriched_data, f, indent=2, ensure_ascii=False)

    file_size_kb = OUTPUT_ENRICHED_JSON.stat().st_size / 1024

    print(f"   ✓ Saved to {OUTPUT_ENRICHED_JSON}")
    print(f"   File size: {file_size_kb:.2f} KB")

    # Summary
    print("\n" + "=" * 60)
    print("✅ ENRICHMENT COMPLETE!")
    print(f"\n📁 Output: {OUTPUT_ENRICHED_JSON}")
    print(f"📊 Coverage: {stats['profile_coverage_pct']}% chunks with job profile")
    print(f"🎯 Profiles identified: {stats['unique_profiles']}")

    return 0


if __name__ == "__main__":
    exit(main())
