#!/usr/bin/env python3
"""
LLM-based CV classification for automatic metadata extraction.

Analyzes parsed CV content using Ollama LLM to determine:
- Language/script (latin vs non-latin characters)
- Actual role/job domain
- Real experience level (based on work history, not file size!)
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, List
import httpx

# Import configuration from config.py (RULE 2)
from config import settings

# Ollama configuration from .env
#OLLAMA_URL = settings.OLLAMA_BASE_URL
OLLAMA_URL = "http://localhost:11434"
MODEL = settings.OLLAMA_LLM_MODEL

async def analyze_cv_with_llm(cv_content: str, client: httpx.AsyncClient) -> Dict:
    """
    Use LLM to analyze CV and extract metadata.

    Returns:
        {
            "is_latin_text": bool,
            "role_domain": str,
            "job_title": str,
            "experience_level": "junior" | "mid" | "senior"
        }
    """

    prompt = f"""You are analyzing a CV/resume. Read the content carefully and extract the following information as JSON.

CV CONTENT:
{cv_content[:3000]}

Based on the above CV content, provide a JSON response with these EXACT fields:
{{
  "is_latin_text": true or false (
    - CRITICAL: Classify based ONLY on the language of SECTION LABELS and JOB DESCRIPTIONS
    - COMPLETELY IGNORE: Person's name (even with diacritics like Nguyễn, Tuấn, Vũ), location/city names, company names, technical terms
    - Look at these specific indicators:
      * Section headers: "Full name" vs "Họ tên", "Date of birth" vs "Ngày sinh", "Address" vs "Địa chỉ"
      * Job descriptions: "Communication is an essential skill" vs "Kỹ năng giao tiếp là cần thiết"
      * Responsibilities: "Receive the orders" vs "Nhận đơn hàng"
    - true: These descriptive elements are in English, French, German, or Spanish
    - false: These descriptive elements are in Vietnamese (Họ tên, Ngày sinh, Giới tính, Địa chỉ, kinh nghiệm, công việc, kỹ năng, etc.), Chinese, Japanese, Korean, Arabic, Cyrillic, or other non-Western languages
  ),
  "role_domain": "specific industry" (examples: "Software Development", "IT Account Management", "Pastry Chef & Hospitality", "Construction Management", "Data Analysis", "Digital Marketing", etc.),
  "job_title": "most recent job title from the CV",
  "experience_level": "junior" or "mid" or "senior" (based on years: 0-2=junior, 3-7=mid, 8+=senior)
}}

EXAMPLES:
- "Full name: Nguyễn Văn A. Date of birth: 01/01/1990. I have experience working with Python" → is_latin_text = TRUE (English labels: "Full name", "Date of birth", "I have experience")
- "Họ tên: John Smith. Ngày sinh: 01/01/1990. Tôi có kinh nghiệm làm việc với Python" → is_latin_text = FALSE (Vietnamese labels: "Họ tên", "Ngày sinh", "Tôi có kinh nghiệm")

Return ONLY the JSON object, nothing else."""

    try:
        response = await client.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.1,  # Low temperature for consistent classification
                    "num_predict": 300
                }
            },
            timeout=settings.LLM_TIMEOUT
        )

        result = response.json()
        llm_response = result.get("response", "{}")

        # Debug: Print first analysis to verify LLM is working
        import sys
        if not hasattr(sys, '_debug_printed'):
            print(f"\n📋 DEBUG - LLM Response Sample:\n{llm_response[:500]}\n")
            sys._debug_printed = True

        analysis = json.loads(llm_response)

        # Validate and provide defaults
        return {
            "is_latin_text": analysis.get("is_latin_text", True),
            "role_domain": analysis.get("role_domain", "Unknown"),
            "job_title": analysis.get("job_title", "Unknown"),
            "experience_level": analysis.get("experience_level", "Unknown")
        }

    except json.JSONDecodeError as e:
        print(f"  ⚠️  JSON parsing failed: {e}")
        print(f"  Response was: {llm_response[:200]}")
        return {
            "is_latin_text": True,
            "role_domain": "Unknown",
            "job_title": "Unknown",
            "experience_level": "Unknown"
        }
    except Exception as e:
        print(f"  ⚠️  LLM analysis failed: {e}")
        return {
            "is_latin_text": True,
            "role_domain": "Unknown",
            "job_title": "Unknown",
            "experience_level": "Unknown"
        }


def extract_cv_text(parsed_cv: Dict) -> str:
    """Extract text content from parsed CV chunks."""
    chunks = parsed_cv.get("chunks", [])
    text_parts = [chunk.get("content", "") for chunk in chunks]
    return "\n".join(text_parts)


async def classify_all_cvs():
    """Main execution - classify all parsed CVs."""

    # Paths
    data_dir = Path("/home/wsluser/dev/lightrag-cv/data/cvs")
    parsed_dir = data_dir / "parsed"
    manifest_path = data_dir / "cvs-manifest.json"

    # Load original manifest
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    print("=" * 70)
    print("LLM-BASED CV CLASSIFICATION")
    print("=" * 70)
    print(f"Model: {MODEL}")
    print(f"Total CVs: {len(manifest['cvs'])}")
    print()

    async with httpx.AsyncClient() as client:
        for i, cv_meta in enumerate(manifest['cvs'], 1):
            candidate_label = cv_meta['candidate_label']
            parsed_file = parsed_dir / f"{candidate_label}_parsed.json"

            if not parsed_file.exists():
                print(f"⏭️  {candidate_label}: Skipped (no parsed file)")
                continue

            # Load parsed CV
            with open(parsed_file, 'r') as f:
                parsed_cv = json.load(f)

            # Extract text content
            cv_text = extract_cv_text(parsed_cv)

            # Analyze with LLM
            print(f"🔍 {i}/25 - Analyzing {candidate_label}...")
            analysis = await analyze_cv_with_llm(cv_text, client)

            # Update manifest with LLM analysis
            cv_meta['role_domain'] = analysis['role_domain']
            cv_meta['job_title'] = analysis['job_title']
            cv_meta['experience_level'] = analysis['experience_level']
            cv_meta['is_latin_text'] = analysis['is_latin_text']
            cv_meta['llm_classified'] = True

            # Print results
            lang = "Latin" if analysis['is_latin_text'] else "Non-Latin"
            print(f"   → {analysis['job_title']}")
            print(f"   → {analysis['role_domain']} ({analysis['experience_level']})")
            print(f"   → {lang}")
            print()

    # Update manifest metadata
    latin_count = sum(1 for cv in manifest['cvs'] if cv.get('is_latin_text', True))

    manifest['metadata']['llm_classification'] = {
        "model": MODEL,
        "total_cvs": len(manifest['cvs']),
        "latin_text_cvs": latin_count
    }
    manifest['metadata']['notes'].append(
        f"LLM classification completed using {MODEL} for automated role/domain/experience detection"
    )

    # Save updated manifest
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print("=" * 70)
    print("CLASSIFICATION COMPLETE")
    print("=" * 70)
    print(f"Total CVs classified:  {len(manifest['cvs'])}")
    print(f"Latin text CVs:        {latin_count}/25")
    print()
    print(f"✅ Updated manifest saved to: {manifest_path}")


if __name__ == "__main__":
    asyncio.run(classify_all_cvs())
