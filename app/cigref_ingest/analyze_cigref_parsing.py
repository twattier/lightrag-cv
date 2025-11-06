#!/usr/bin/env python3
"""
Analyze CIGREF parsed output for quality validation.

Part of lightrag-cv application workflows.
Module: app.cigref_ingest.analyze_cigref_parsing

This script performs structured analysis to validate extraction quality:
1. Identify IT profile domains and individual profiles
2. Validate structured sections (Missions, Activities, Deliverables, Skills)
3. Check table extraction quality
4. Generate sample profiles for manual inspection
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Any


# Configuration
INPUT_JSON = Path("/home/wsluser/dev/lightrag-cv/data/cigref/cigref-parsed-raw.json")
OUTPUT_ANALYSIS = Path("/home/wsluser/dev/lightrag-cv/data/cigref/cigref-analysis.json")


# Expected CIGREF structure keywords
DOMAIN_KEYWORDS = ["Business", "Development", "Production", "Support", "Governance"]
SECTION_KEYWORDS = [
    "Mission", "Missions",
    "Activities", "Activités", "Activity",
    "Deliverables", "Livrables",
    "Performance Indicators", "Indicateurs",
    "Skills", "Compétences", "Technical Skills", "Behavioral Skills"
]
PROFILE_INDICATORS = [
    "Architect", "Engineer", "Manager", "Analyst", "Administrator",
    "Developer", "Specialist", "Officer", "Coordinator", "Expert",
    "Data Scientist", "DevOps", "Cloud", "Security", "Network"
]


def load_parsed_data(path: Path) -> Dict[str, Any]:
    """Load parsed CIGREF JSON data."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_domains(chunks: List[Dict]) -> Dict[str, List[int]]:
    """Identify IT profile domain mentions in chunks."""
    domains_found = defaultdict(list)

    for idx, chunk in enumerate(chunks):
        content = chunk.get("content", "")
        for domain in DOMAIN_KEYWORDS:
            if re.search(rf"\b{domain}\b", content, re.IGNORECASE):
                domains_found[domain].append(idx)

    return dict(domains_found)


def find_profiles(chunks: List[Dict]) -> List[Dict[str, Any]]:
    """Identify individual IT profiles in chunks."""
    profiles_found = []

    for idx, chunk in enumerate(chunks):
        content = chunk.get("content", "")

        # Look for profile indicators
        for indicator in PROFILE_INDICATORS:
            if re.search(rf"\b{indicator}\b", content, re.IGNORECASE):
                # Extract potential profile title (first line or heading)
                lines = content.split("\n")
                title = lines[0].strip() if lines else content[:100]

                profiles_found.append({
                    "chunk_id": chunk.get("chunk_id"),
                    "chunk_index": idx,
                    "title": title,
                    "indicator": indicator,
                    "content_preview": content[:200]
                })
                break  # Only count once per chunk

    return profiles_found


def find_sections(chunks: List[Dict]) -> Dict[str, List[int]]:
    """Identify structured section keywords in chunks."""
    sections_found = defaultdict(list)

    for idx, chunk in enumerate(chunks):
        content = chunk.get("content", "")
        for section in SECTION_KEYWORDS:
            if re.search(rf"\b{section}\b", content, re.IGNORECASE):
                sections_found[section].append(idx)

    return dict(sections_found)


def analyze_tables(metadata: Dict) -> Dict[str, Any]:
    """Analyze table extraction from metadata."""
    tables_extracted = metadata.get("tables_extracted", 0)

    return {
        "total_tables": tables_extracted,
        "assessment": "Good" if tables_extracted > 50 else "Limited" if tables_extracted > 0 else "None"
    }


def find_sample_profiles(chunks: List[Dict], count: int = 3) -> List[Dict[str, Any]]:
    """Extract complete sample profiles for manual inspection."""
    samples = []

    # Look for chunks with multiple section keywords (likely complete profiles)
    for idx, chunk in enumerate(chunks):
        content = chunk.get("content", "")
        section_matches = sum(1 for s in SECTION_KEYWORDS if s.lower() in content.lower())

        if section_matches >= 3:  # Has at least 3 structured sections
            samples.append({
                "chunk_id": chunk.get("chunk_id"),
                "chunk_index": idx,
                "section_count": section_matches,
                "content": content
            })

        if len(samples) >= count:
            break

    return samples


def calculate_quality_score(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate quality metrics for NFR3 validation (85% threshold)."""

    # Scoring criteria (out of 100)
    scores = {
        "domains_identified": 0,
        "profiles_identified": 0,
        "sections_recognized": 0,
        "tables_extracted": 0
    }

    # Domain identification (20 points)
    domains_count = len(analysis["domains"])
    if domains_count >= 4:
        scores["domains_identified"] = 20
    elif domains_count >= 2:
        scores["domains_identified"] = 10

    # Profile identification (30 points)
    profiles_count = len(analysis["profiles"])
    if profiles_count >= 20:
        scores["profiles_identified"] = 30
    elif profiles_count >= 10:
        scores["profiles_identified"] = 20
    elif profiles_count >= 5:
        scores["profiles_identified"] = 10

    # Section recognition (30 points)
    sections_count = len(analysis["sections"])
    if sections_count >= 5:
        scores["sections_recognized"] = 30
    elif sections_count >= 3:
        scores["sections_recognized"] = 20
    elif sections_count >= 1:
        scores["sections_recognized"] = 10

    # Table extraction (20 points)
    tables_count = analysis["tables"]["total_tables"]
    if tables_count >= 100:
        scores["tables_extracted"] = 20
    elif tables_count >= 50:
        scores["tables_extracted"] = 15
    elif tables_count >= 10:
        scores["tables_extracted"] = 10

    total_score = sum(scores.values())

    return {
        "scores": scores,
        "total_score": total_score,
        "percentage": total_score,
        "meets_threshold": total_score >= 85,
        "assessment": "PASS" if total_score >= 85 else "NEEDS REVIEW"
    }


def main():
    """Main analysis entry point."""
    print("📊 Analyzing CIGREF Parsing Quality\n")
    print("=" * 60)

    # Load data
    print(f"\n📄 Loading parsed data: {INPUT_JSON.name}")
    data = load_parsed_data(INPUT_JSON)

    chunks = data.get("chunks", [])
    metadata = data.get("metadata", {})

    print(f"   Total chunks: {len(chunks)}")
    print(f"   Document ID: {data.get('document_id')}")
    print(f"   Processing time: {metadata.get('processing_time_ms', 0) / 1000:.2f}s")

    # Perform analysis
    print("\n🔍 Analyzing document structure...\n")

    domains = find_domains(chunks)
    print(f"✓ Domains found: {len(domains)}")
    for domain, chunk_indices in domains.items():
        print(f"  - {domain}: {len(chunk_indices)} mentions")

    profiles = find_profiles(chunks)
    print(f"\n✓ Profiles identified: {len(profiles)}")
    print(f"  (Unique profile indicators found)")

    sections = find_sections(chunks)
    print(f"\n✓ Sections recognized: {len(sections)}")
    for section, chunk_indices in sections.items():
        print(f"  - {section}: {len(chunk_indices)} occurrences")

    tables = analyze_tables(metadata)
    print(f"\n✓ Tables extracted: {tables['total_tables']}")
    print(f"  Assessment: {tables['assessment']}")

    sample_profiles = find_sample_profiles(chunks, count=3)
    print(f"\n✓ Sample profiles extracted: {len(sample_profiles)}")

    # Calculate quality score
    analysis_result = {
        "document_id": data.get("document_id"),
        "total_chunks": len(chunks),
        "domains": domains,
        "profiles": profiles[:20],  # Limit to first 20 for brevity
        "sections": sections,
        "tables": tables,
        "sample_profiles": sample_profiles
    }

    quality_metrics = calculate_quality_score(analysis_result)
    analysis_result["quality_metrics"] = quality_metrics

    print("\n" + "=" * 60)
    print("\n🎯 QUALITY ASSESSMENT (NFR3: 85% Threshold)")
    print("=" * 60)
    print(f"\nScores:")
    for criterion, score in quality_metrics["scores"].items():
        print(f"  {criterion.replace('_', ' ').title()}: {score}/20-30")
    print(f"\n📊 Total Score: {quality_metrics['total_score']}/100 ({quality_metrics['percentage']}%)")
    print(f"🎯 Assessment: {quality_metrics['assessment']}")
    print(f"✅ Meets 85% Threshold: {'YES' if quality_metrics['meets_threshold'] else 'NO'}")

    # Save analysis
    print(f"\n💾 Saving analysis to: {OUTPUT_ANALYSIS.name}")
    with open(OUTPUT_ANALYSIS, "w", encoding="utf-8") as f:
        json.dump(analysis_result, f, indent=2, ensure_ascii=False)

    print("\n✅ Analysis complete!\n")
    print(f"📝 Next steps:")
    print(f"   1. Review sample profiles in: {OUTPUT_ANALYSIS}")
    print(f"   2. Manual inspection of extraction quality")
    print(f"   3. Document findings in validation report")

    return 0 if quality_metrics["meets_threshold"] else 1


if __name__ == "__main__":
    exit(main())
