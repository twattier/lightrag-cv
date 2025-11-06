#!/usr/bin/env python3
"""
Validate LLM classification results against expected ground truth values.

Part of lightrag-cv application workflows.
Module: app.cv_ingest.validate_classification
"""

import json
from pathlib import Path

def validate_classification():
    """Compare LLM classification results with expected values."""

    data_dir = Path("/home/wsluser/dev/lightrag-cv/data/cvs")
    manifest_path = data_dir / "cvs-manifest.json"
    expected_path = data_dir / "expected-classification.json"

    # Load expected values
    with open(expected_path, 'r') as f:
        expected = json.load(f)

    # Load manifest with LLM results
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    print("=" * 70)
    print("LLM CLASSIFICATION VALIDATION")
    print("=" * 70)
    print()

    # Compare results
    correct = 0
    incorrect = 0
    mismatches = []

    for cv in manifest['cvs']:
        candidate_label = cv['candidate_label']
        llm_result = cv.get('is_latin_text', None)
        expected_result = expected['expected_is_latin_text'].get(candidate_label)

        if llm_result is None:
            print(f"⚠️  {candidate_label}: Not classified yet")
            continue

        if llm_result == expected_result:
            correct += 1
            status = "✓"
        else:
            incorrect += 1
            status = "✗"
            mismatches.append({
                "cv": candidate_label,
                "expected": expected_result,
                "got": llm_result
            })

        print(f"{status} {candidate_label}: Expected={expected_result}, Got={llm_result}")

    print()
    print("=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Total CVs:       {correct + incorrect}")
    print(f"Correct:         {correct}")
    print(f"Incorrect:       {incorrect}")
    print(f"Accuracy:        {correct/(correct+incorrect)*100:.1f}%")

    if mismatches:
        print()
        print("MISMATCHES:")
        for m in mismatches:
            print(f"  {m['cv']}: Expected {m['expected']}, got {m['got']}")

    print()
    if incorrect == 0:
        print("✅ Perfect classification! All results match expected values.")
    elif incorrect <= 2:
        print("⚠️  Minor discrepancies - review mismatches above.")
    else:
        print("❌ Significant discrepancies - LLM prompt may need adjustment.")

if __name__ == "__main__":
    validate_classification()
