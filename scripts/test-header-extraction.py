#!/usr/bin/env python3
"""
Test pdfplumber header extraction from CIGREF PDF.
Extract headers from page 111 to validate approach.
"""

import pdfplumber
from pathlib import Path

CIGREF_PDF_PATH = Path("/home/wsluser/dev/lightrag-cv/data/cigref/Cigref_Nomenclature_des_profils_metiers_SI_EN_2024.pdf")

def extract_page_header(page, header_height=50):
    """
    Extract text from the top header region of a page.

    Args:
        page: pdfplumber page object
        header_height: Height in points from top to extract (default 50)

    Returns:
        Extracted header text
    """
    # Crop to header region (top portion of page)
    header_bbox = (0, 0, page.width, header_height)
    header = page.crop(header_bbox)

    # Extract text from header region
    header_text = header.extract_text()

    return header_text

def main():
    print(f"📄 Opening CIGREF PDF: {CIGREF_PDF_PATH.name}\n")

    with pdfplumber.open(CIGREF_PDF_PATH) as pdf:
        # Test pages: 111 (known to have headers), plus a few others
        test_pages = [111, 110, 112, 50, 1]

        for page_num in test_pages:
            if page_num > len(pdf.pages):
                continue

            page = pdf.pages[page_num - 1]  # pdfplumber uses 0-indexed

            print(f"{'='*60}")
            print(f"PAGE {page_num}")
            print(f"{'='*60}")

            # Try different header heights
            for height in [30, 50, 80]:
                header_text = extract_page_header(page, header_height=height)

                if header_text:
                    print(f"\nHeader (height={height}px):")
                    print(f"{header_text}")
                    print(f"---")

            # Also show full page text (first 500 chars) for context
            full_text = page.extract_text()
            if full_text:
                print(f"\nFull page (first 500 chars):")
                print(f"{full_text[:500]}")

            print("\n")

if __name__ == "__main__":
    main()
