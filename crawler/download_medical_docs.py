"""
Medical Document Downloader for HealthCareAGENT RAG Pipeline
=============================================================
Downloads free, publicly available medical PDFs from official sources
(WHO, NIH/NHLBI, CDC) and saves them to data/documents/.

Usage:
    python scratch/download_medical_docs.py

Sources: All official government / WHO publications — no copyright issues.
"""

import os
import sys
import time
import urllib.request
from pathlib import Path

# ── paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
DOCS_DIR = ROOT / "data" / "documents"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# ── document catalog ───────────────────────────────────────────────────────────
# Format: (filename_to_save, url, description)
DOCUMENTS = [
    (
        "WHO_dsa509.pdf",
        "https://applications.emro.who.int/dsaf/dsa509.pdf",
        "WHO Document 509"
    ),
    (
        "WHO_dsa700.pdf",
        "https://applications.emro.who.int/dsaf/dsa700.pdf",
        "WHO Document 700"
    ),
    (
        "NHLBI_jnc7full.pdf",
        "https://www.nhlbi.nih.gov/files/docs/guidelines/jnc7full.pdf",
        "NHLBI JNC7 Full Report - Hypertension"
    ),
    (
        "NHLBI_atp-3-cholesterol-full-report.pdf",
        "https://www.nhlbi.nih.gov/files/docs/resources/heart/atp-3-cholesterol-full-report.pdf",
        "NHLBI ATP-3 Cholesterol Full Report"
    ),
    (
        "NHLBI_healthyheart.pdf",
        "https://www.nhlbi.nih.gov/files/docs/public/heart/healthyheart.pdf",
        "NHLBI Healthy Heart Guide"
    ),
    (
        "WHO_NCD_guidelines_Green_book.pdf",
        "https://extranet.who.int/ncdccs/Data/COK_D1_NCD%20guidelines%20Green%20book%202013%20final%20no%20cover.pdf",
        "WHO NCD Guidelines Green Book 2013"
    ),
]

# ── downloader ─────────────────────────────────────────────────────────────────

def download(filename: str, url: str, description: str) -> bool:
    dest = DOCS_DIR / filename
    if dest.exists():
        print(f"  [SKIP] {filename} already exists")
        return True

    print(f"  [DOWN] {filename}")
    print(f"         {description}")
    try:
        headers = {"User-Agent": "Mozilla/5.0 HealthCareAGENT-RAG-Downloader"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
        with open(dest, "wb") as f:
            f.write(data)
        size_kb = len(data) // 1024
        print(f"         -> saved ({size_kb} KB)")
        return True
    except Exception as e:
        print(f"         -> FAILED: {e}")
        return False


def main():
    print(f"\nHealthCareAGENT — Medical Document Downloader")
    print(f"Target directory: {DOCS_DIR}\n")

    ok, failed = 0, []
    for filename, url, desc in DOCUMENTS:
        success = download(filename, url, desc)
        if success:
            ok += 1
        else:
            failed.append(filename)
        time.sleep(0.5)  # be polite to servers

    print(f"\n{'='*55}")
    print(f"Downloaded: {ok}/{len(DOCUMENTS)}")
    if failed:
        print(f"\nFailed ({len(failed)}):")
        for f in failed:
            print(f"  - {f}")
        print("\nFor failed files, download manually from the links in")
        print("the MANUAL_DOWNLOADS section of RAG_PIPELINE.md")
    else:
        print("All documents downloaded successfully!")

    print(f"\nNext step — run ingestion:")
    print(f"  python -m backend.rag.ingestion")


if __name__ == "__main__":
    main()
