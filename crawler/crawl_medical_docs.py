"""
Medical Document Scraper
========================
Extracts clean, RAG-ready Markdown from medical web pages using
Trafilatura (primary) and BeautifulSoup4 (fallback).

Run:
    python scratch/crawl_medical_docs.py
"""

import os
import re
import time
import requests
from urllib.parse import urlparse
from pathlib import Path
from bs4 import BeautifulSoup
import trafilatura

# Ensure documents directory exists
DOCS_DIR = Path(__file__).parent.parent / "data" / "documents"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# List of URLs to extract
URLS_TO_SCRAPE = [
    "https://medlineplus.gov/type2diabetes.html",
    "https://www.mayoclinic.org/diseases-conditions/type-2-diabetes/symptoms-causes/syc-20351193",
    "https://www.nhs.uk/conditions/type-2-diabetes/",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) HealthCareAGENT-Scraper/1.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# Common error phrases to detect soft 404s or paywalls
ERROR_PHRASES = [
    "page you're looking for was not found",
    "page you were looking for has moved",
    "404 error",
    "not found",
    "access denied",
    "please log in",
    "subscribe to read",
]

def sanitize_filename(url: str) -> str:
    """Convert URL into a clean, safe markdown filename."""
    parsed = urlparse(url)
    name = f"{parsed.netloc}_{parsed.path}"
    name = re.sub(r'[^a-zA-Z0-9]', '_', name)
    name = re.sub(r'_+', '_', name).strip('_')
    if not name:
        name = "scraped_article"
    return f"{name}.md"


def is_error_page(text: str) -> bool:
    """Check if the extracted text looks like an error page."""
    lower_text = text.lower()
    # If the text is very short and contains error phrases
    if len(text) < 1000:
        for phrase in ERROR_PHRASES:
            if phrase in lower_text:
                return True
    return False


def bs4_fallback(html: str) -> str:
    """Fallback extraction using BeautifulSoup4."""
    soup = BeautifulSoup(html, "html.parser")
    
    # Remove junk elements
    for element in soup(["nav", "footer", "script", "style", "header", "aside", "form"]):
        element.decompose()
        
    # Try to find main article content
    main_content = soup.find("main") or soup.find("article")
    if not main_content:
        main_content = soup.find("div", {"class": re.compile("content|article|main")})
        
    if main_content:
        # Extract text, normalize whitespace
        text = main_content.get_text(separator="\n", strip=True)
        return text
    
    # Absolute fallback to body text
    return soup.get_text(separator="\n", strip=True)


def scrape_url(url: str) -> bool:
    print(f"Fetching: {url}")
    
    # 1. Fetch raw HTML
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        html = response.text
    except Exception as e:
        print(f"  [X] HTTP Error: {e}")
        return False
        
    # 2. Extract with Trafilatura
    markdown_text = trafilatura.extract(
        html,
        include_links=False,     # No link spam
        favor_recall=True,       # Capture more content
        output_format="markdown" # RAG ready
    )
    
    # 3. Fallback to BS4 if Trafilatura fails
    if not markdown_text:
        print("  [!] Trafilatura failed, using BS4 fallback...")
        markdown_text = bs4_fallback(html)
        
    if not markdown_text:
        print("  [X] Extraction failed completely.")
        return False
        
    # 4. Error/404 Page Detection
    if is_error_page(markdown_text):
        print("  [X] Soft 404 or Error page detected. Skipping.")
        return False
        
    # 5. Save to data/documents/
    filename = sanitize_filename(url)
    filepath = DOCS_DIR / filename
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown_text)
        size_kb = len(markdown_text.encode("utf-8")) / 1024
        print(f"  [OK] Saved {size_kb:.1f} KB -> {filename}")
        return True
    except Exception as e:
        print(f"  [X] Error saving file: {e}")
        return False


def main():
    print(f"Starting scraper for {len(URLS_TO_SCRAPE)} URLs...")
    print(f"Saving to: {DOCS_DIR}\n")
    
    success_count = 0
    for i, url in enumerate(URLS_TO_SCRAPE):
        if scrape_url(url):
            success_count += 1
            
        # 6. Polite delay
        if i < len(URLS_TO_SCRAPE) - 1:
            time.sleep(1.5)
            
    print(f"\n{'-'*50}")
    print(f"Done! {success_count}/{len(URLS_TO_SCRAPE)} pages saved successfully.")
    print("Next step: python -m backend.rag.ingestion")


if __name__ == "__main__":
    main()