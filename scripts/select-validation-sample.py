#!/usr/bin/env python3
"""
Select 5 CVs for manual quality validation (Story 2.4 Task 3).

Randomly selects 5 CVs from successfully parsed outputs ensuring diversity
in experience levels and file sizes.
"""

import json
import random
from pathlib import Path
from typing import List, Dict

def load_manifest(manifest_path: Path) -> Dict:
    """Load the CV manifest."""
    with open(manifest_path, 'r') as f:
        return json.load(f)

def get_successfully_parsed_cvs(parsed_dir: Path, manifest: Dict) -> List[Dict]:
    """
    Get list of successfully parsed CVs suitable for validation.

    Filters for:
    - Successfully parsed (file exists)
    - Latin text (is_latin_text=true from LLM classification) for readability
    """
    parsed_files = {f.stem.replace('_parsed', '') for f in parsed_dir.glob('*.json')}

    successful_cvs = []
    for cv in manifest['cvs']:
        if (cv['candidate_label'] in parsed_files and
            cv.get('is_latin_text', True)):      # Only Latin text
            successful_cvs.append(cv)

    return successful_cvs

def select_diverse_sample(cvs: List[Dict], sample_size: int = 5) -> List[Dict]:
    """
    Select diverse sample ensuring different experience levels and file sizes.

    Strategy:
    - Try to get mix of junior/mid/senior
    - Try to get mix of file sizes (small/medium/large)
    """
    # Group by experience level
    by_exp_level = {}
    for cv in cvs:
        level = cv['experience_level']
        if level not in by_exp_level:
            by_exp_level[level] = []
        by_exp_level[level].append(cv)

    # Try to select at least one from each experience level
    selected = []

    # Select one from each level first (up to 3)
    for level in ['junior', 'mid', 'senior']:
        if level in by_exp_level and by_exp_level[level]:
            selected.append(random.choice(by_exp_level[level]))

    # Fill remaining slots with random selection
    remaining = [cv for cv in cvs if cv not in selected]
    additional_needed = sample_size - len(selected)

    if additional_needed > 0 and remaining:
        selected.extend(random.sample(remaining, min(additional_needed, len(remaining))))

    return selected

def main():
    """Main execution."""
    random.seed(42)  # For reproducibility

    # Paths
    data_dir = Path("/home/wsluser/dev/lightrag-cv/data")
    manifest_path = data_dir / "cvs" / "cvs-manifest.json"
    parsed_dir = data_dir / "cvs" / "parsed"

    # Load data
    manifest = load_manifest(manifest_path)
    successful_cvs = get_successfully_parsed_cvs(parsed_dir, manifest)

    print(f"Total successfully parsed CVs: {len(successful_cvs)}")
    print()

    # Select sample
    #sample = select_diverse_sample(successful_cvs, sample_size=5)
    sample = successful_cvs

    print("="*70)
    print("SELECTED VALIDATION SAMPLE (5 CVs)")
    print("="*70)

    for i, cv in enumerate(sample, 1):
        print(f"\n{i}. {cv['candidate_label']}")
        print(f"   Filename:         {cv['filename']}")
        print(f"   Experience Level: {cv['experience_level']}")
        print(f"   File Size:        {cv['file_size_kb']:.2f} KB")
        print(f"   Page Count:       {cv['page_count']}")
        print(f"   Source:           {cv['source_dataset']}")

    print("\n" + "="*70)
    print()

    # Save selection for later reference
    output_path = data_dir / "cvs" / "validation-sample.json"
    with open(output_path, 'w') as f:
        json.dump({
            "selected_cvs": [cv['candidate_label'] for cv in sample],
            "sample_details": sample
        }, f, indent=2)

    print(f"Selection saved to: {output_path}")

    # Print instructions for manual review
    print("\nMANUAL REVIEW INSTRUCTIONS:")
    print("For each CV above:")
    print("1. Open original PDF: data/cvs/test-set/{filename}")
    print("2. Open parsed JSON: data/cvs/parsed/{candidate_label}_parsed.json")
    print("3. Compare and validate:")
    print("   - Skills/Technologies extracted")
    print("   - Work Experience (companies, roles, dates)")
    print("   - Education (degrees, institutions)")
    print("   - Projects/Accomplishments")
    print("4. Rate quality: Excellent (90%+), Good (70-89%), Fair (50-69%), Poor (<50%)")

if __name__ == "__main__":
    main()
