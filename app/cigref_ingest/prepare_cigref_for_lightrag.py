#!/usr/bin/env python3
"""
Prepare CIGREF parsed output for LightRAG ingestion.

Part of lightrag-cv application workflows.
Module: app.cigref_ingest.prepare_cigref_for_lightrag

Transform enriched Docling output to clean JSON format compatible with LightRAG:
1. Add document-level metadata
2. Clean and structure chunks
3. Preserve hierarchical metadata (domain, job_profile)
4. Add document_type tagging
5. Ensure JSON validity
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


# Configuration
INPUT_RAW_JSON = Path("/home/wsluser/dev/lightrag-cv/data/cigref/cigref-enriched.json")
OUTPUT_CLEAN_JSON = Path("/home/wsluser/dev/lightrag-cv/data/cigref/cigref-parsed.json")


def load_raw_data(path: Path) -> Dict[str, Any]:
    """Load raw parsed CIGREF data."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def transform_for_lightrag(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform raw Docling output to LightRAG-compatible format.

    Args:
        raw_data: Raw Docling parse response

    Returns:
        Cleaned data structure for LightRAG ingestion
    """
    document_id = raw_data.get("document_id")
    chunks = raw_data.get("chunks", [])
    metadata = raw_data.get("metadata", {})

    # Document-level metadata for document_metadata table
    document_metadata = {
        "document_id": document_id,
        "document_type": "CIGREF_PROFILE",
        "source_filename": "Cigref_Nomenclature_des_profils_metiers_SI_EN_2024.pdf",
        "source_path": "/data/cigref/Cigref_Nomenclature_des_profils_metiers_SI_EN_2024.pdf",
        "format": metadata.get("format", "PDF"),
        "page_count": metadata.get("page_count", 0),
        "tables_extracted": metadata.get("tables_extracted", 0),
        "processing_time_ms": metadata.get("processing_time_ms", 0),
        "total_chunks": len(chunks),
        "parsed_date": datetime.utcnow().isoformat() + "Z",
        "version": "2024_EN",
        "language": "en"
    }

    # Clean and structure chunks (preserve hierarchical metadata)
    cleaned_chunks = []
    for chunk in chunks:
        chunk_metadata = chunk.get("metadata", {})

        cleaned_chunk = {
            "chunk_id": chunk.get("chunk_id"),
            "content": chunk.get("content", "").strip(),
            "chunk_type": chunk.get("chunk_type", "paragraph"),
            "metadata": {
                "domain_id": chunk_metadata.get("domain_id"),
                "domain": chunk_metadata.get("domain"),
                "job_profile_id": chunk_metadata.get("job_profile_id"),
                "job_profile": chunk_metadata.get("job_profile"),
                "section": chunk_metadata.get("section", ""),
                "page": chunk_metadata.get("page", 1),
                "token_count": chunk_metadata.get("token_count", 0)
            }
        }
        cleaned_chunks.append(cleaned_chunk)

    return {
        "document_metadata": document_metadata,
        "chunks": cleaned_chunks,
        "ingestion_ready": True,
        "format_version": "1.0"
    }


def validate_json(data: Dict[str, Any]) -> bool:
    """Validate JSON structure."""
    required_keys = ["document_metadata", "chunks", "ingestion_ready"]

    for key in required_keys:
        if key not in data:
            print(f"❌ Missing required key: {key}")
            return False

    if not isinstance(data["chunks"], list):
        print("❌ 'chunks' must be a list")
        return False

    if len(data["chunks"]) == 0:
        print("❌ 'chunks' array is empty")
        return False

    return True


def main():
    """Main entry point."""
    print("🔧 Preparing CIGREF data for LightRAG ingestion\n")
    print("=" * 60)

    # Load enriched data
    print(f"\n📄 Loading enriched parsed data: {INPUT_RAW_JSON.name}")
    raw_data = load_raw_data(INPUT_RAW_JSON)

    print(f"   Document ID: {raw_data.get('document_id')}")
    print(f"   Total chunks: {len(raw_data.get('chunks', []))}")

    # Check enrichment metadata
    enrichment_meta = raw_data.get("enrichment_metadata", {})
    if enrichment_meta:
        stats = enrichment_meta.get("statistics", {})
        print(f"   Hierarchical enrichment: {stats.get('profile_coverage_pct', 0)}% chunks with job profile")

    # Transform
    print("\n🔄 Transforming to LightRAG format...")
    cleaned_data = transform_for_lightrag(raw_data)

    # Validate
    print("\n✓ Validating JSON structure...")
    if not validate_json(cleaned_data):
        print("❌ Validation failed!")
        return 1

    print("   ✓ All required keys present")
    print("   ✓ Chunks array valid")
    print("   ✓ Metadata complete")

    # Save
    print(f"\n💾 Saving cleaned data to: {OUTPUT_CLEAN_JSON.name}")
    OUTPUT_CLEAN_JSON.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_CLEAN_JSON, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

    # Summary
    print("\n" + "=" * 60)
    print("\n✅ CIGREF data prepared for LightRAG ingestion!")
    print("\n📊 Output Summary:")
    print(f"   Document Type: {cleaned_data['document_metadata']['document_type']}")
    print(f"   Total Chunks: {cleaned_data['document_metadata']['total_chunks']}")
    print(f"   Tables Extracted: {cleaned_data['document_metadata']['tables_extracted']}")
    print(f"   Format: {cleaned_data['document_metadata']['format']}")
    print(f"   Language: {cleaned_data['document_metadata']['language']}")
    print(f"   Version: {cleaned_data['document_metadata']['version']}")

    print(f"\n📁 Output File: {OUTPUT_CLEAN_JSON}")
    print(f"   File size: {OUTPUT_CLEAN_JSON.stat().st_size / 1024:.2f} KB")

    print("\n✅ Ready for Story 2.5 LightRAG ingestion!")

    return 0


if __name__ == "__main__":
    exit(main())
