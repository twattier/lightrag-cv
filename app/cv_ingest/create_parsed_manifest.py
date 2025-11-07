#!/usr/bin/env python3
"""
Create parsed CV manifest for LightRAG ingestion (Story 2.4 Task 8).

Part of lightrag-cv application workflows.
Module: app.cv_ingest.create_parsed_manifest

Generates parsed-manifest.json with metadata for all successfully parsed CVs.
"""

import json
from pathlib import Path
from typing import Dict, List

def load_manifest(manifest_path: Path) -> Dict:
    """Load the CV manifest."""
    with open(manifest_path, 'r') as f:
        return json.load(f)

def load_validation_sample(validation_path: Path) -> Dict:
    """Load validation sample with quality ratings."""
    if validation_path.exists():
        with open(validation_path, 'r') as f:
            return json.load(f)
    return {"sample_details": []}

def create_parsed_manifest(
    cvs_manifest: Dict,
    parsed_dir: Path,
    validation_sample: Dict
) -> Dict:
    """Create manifest of parsed CVs."""

    # Create quality ratings lookup from validation sample
    quality_ratings = {}
    for cv in validation_sample.get("sample_details", []):
        label = cv["candidate_label"]
        # Map quality ratings based on manual review
        if label == "cv_004" or label == "cv_013":
            quality_ratings[label] = "Excellent"
        elif label == "cv_005" or label == "cv_012" or label == "cv_021":
            quality_ratings[label] = "Good"

    parsed_cvs = []

    for cv_meta in cvs_manifest["cvs"]:
        candidate_label = cv_meta["candidate_label"]
        parsed_file = parsed_dir / f"{candidate_label}_parsed.json"

        if parsed_file.exists():
            # Load parsed JSON to get chunks count
            with open(parsed_file, 'r') as f:
                parsed_data = json.load(f)

            chunks_count = len(parsed_data.get("chunks", []))

            parsed_cvs.append({
                "candidate_label": candidate_label,
                "source_filename": cv_meta["filename"],
                "parsed_filename": f"{candidate_label}_parsed.json",
                "chunks_count": chunks_count,
                "quality_rating": quality_ratings.get(candidate_label, "Not Validated"),
                "ready_for_ingestion": True,
                "metadata": {
                    "role_domain": cv_meta.get("role_domain"),
                    "experience_level": cv_meta.get("experience_level"),
                    "file_format": cv_meta.get("file_format"),
                    "file_size_kb": cv_meta.get("file_size_kb"),
                    "page_count": cv_meta.get("page_count"),
                    "source_dataset": cv_meta.get("source_dataset")
                }
            })

    return {
        "metadata": {
            "total_parsed_cvs": len(parsed_cvs),
            "ready_for_ingestion": len([cv for cv in parsed_cvs if cv["ready_for_ingestion"]]),
            "total_chunks": sum(cv["chunks_count"] for cv in parsed_cvs),
            "avg_chunks_per_cv": sum(cv["chunks_count"] for cv in parsed_cvs) / len(parsed_cvs) if parsed_cvs else 0,
            "validation_sample_size": len(quality_ratings)            
        },
        "parsed_cvs": parsed_cvs
    }

def main():
    """Main execution."""
    # Paths
    data_dir = Path("/home/wsluser/dev/lightrag-cv/data")
    cvs_dir = data_dir / "cvs"
    manifest_path = cvs_dir / "cvs-manifest.json"
    validation_path = cvs_dir / "validation-sample.json"
    parsed_dir = cvs_dir / "parsed"
    output_path = cvs_dir / "parsed-manifest.json"

    # Load data
    cvs_manifest = load_manifest(manifest_path)
    validation_sample = load_validation_sample(validation_path)

    # Create parsed manifest
    parsed_manifest = create_parsed_manifest(cvs_manifest, parsed_dir, validation_sample)

    # Save
    with open(output_path, 'w') as f:
        json.dump(parsed_manifest, f, indent=2)

    print("="*70)
    print("PARSED CV MANIFEST CREATED")
    print("="*70)
    print(f"Total parsed CVs:      {parsed_manifest['metadata']['total_parsed_cvs']}")
    print(f"Ready for ingestion:   {parsed_manifest['metadata']['ready_for_ingestion']}")
    print(f"Total chunks:          {parsed_manifest['metadata']['total_chunks']}")
    print(f"Avg chunks per CV:     {parsed_manifest['metadata']['avg_chunks_per_cv']:.1f}")
    print(f"Validation sample:     {parsed_manifest['metadata']['validation_sample_size']} CVs")
    print("="*70)
    print(f"\nManifest saved to: {output_path}")
    print("\n✅ CVs ready for LightRAG ingestion (Story 2.6)")

if __name__ == "__main__":
    main()
