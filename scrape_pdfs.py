#!/usr/bin/env python3
"""
WV DEP PDF Scraper
Downloads PDFs from the West Virginia Department of Environmental Protection document portal.
"""

import os
import re
import time
import argparse
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup

# Try importing cloudscraper first (best for anti-bot)
try:
    import cloudscraper
    HAS_CLOUDSCRAPER = True
except ImportError:
    HAS_CLOUDSCRAPER = False
    import requests

# Try importing selenium as fallback
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False


class WVDEPScraper:
    """Scraper for WV DEP document portal."""

    def __init__(self, output_dir="downloaded_pdfs", use_selenium=False):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.use_selenium = use_selenium
        self.driver = None

        # Choose the best available session type
        if use_selenium and HAS_SELENIUM:
            print("Using Selenium WebDriver for scraping...")
            self.session_type = 'selenium'
            self._init_selenium()
        elif HAS_CLOUDSCRAPER:
            print("Using Cloudscraper for scraping...")
            self.session_type = 'cloudscraper'
            self.session = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                }
            )
        else:
            print("Using requests for scraping...")
            self.session_type = 'requests'
            import requests
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
            })

    def _init_selenium(self):
        """Initialize Selenium WebDriver."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        self.driver = webdriver.Chrome(options=chrome_options)

    def __del__(self):
        """Cleanup Selenium driver if used."""
        if self.driver:
            self.driver.quit()

    def sanitize_filename(self, filename):
        """Sanitize filename to remove invalid characters."""
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limit length
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:200-len(ext)] + ext
        return filename

    def fetch_page(self, url):
        """Fetch a page with retry logic."""
        max_retries = 3

        if self.session_type == 'selenium':
            # Use Selenium to fetch page
            try:
                print(f"Fetching page with Selenium: {url}")
                self.driver.get(url)
                # Wait for page to load
                time.sleep(3)
                # Create a mock response object
                class MockResponse:
                    def __init__(self, text, url):
                        self.text = text
                        self.content = text.encode('utf-8')
                        self.url = url
                        self.status_code = 200
                return MockResponse(self.driver.page_source, url)
            except Exception as e:
                print(f"Selenium fetch failed: {e}")
                raise
        else:
            # Use requests or cloudscraper
            for attempt in range(max_retries):
                try:
                    print(f"Fetching page: {url}")
                    response = self.session.get(url, timeout=30)
                    response.raise_for_status()
                    return response
                except Exception as e:
                    print(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        raise

    def find_pdf_links(self, url):
        """Find all PDF links on the page."""
        response = self.fetch_page(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        pdf_links = []

        # Method 1: Find direct PDF links
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.lower().endswith('.pdf') or 'pdf' in href.lower():
                full_url = urljoin(url, href)
                pdf_links.append({
                    'url': full_url,
                    'text': link.get_text(strip=True) or 'Untitled',
                    'title': link.get('title', '')
                })

        # Method 2: Find links that might trigger PDF downloads
        # Look for onclick handlers or data attributes that might contain PDF URLs
        for element in soup.find_all(['a', 'button', 'div'], href=True):
            onclick = element.get('onclick', '')
            if 'pdf' in onclick.lower():
                # Try to extract URL from onclick
                url_match = re.search(r'["\']([^"\']*\.pdf[^"\']*)["\']', onclick, re.IGNORECASE)
                if url_match:
                    full_url = urljoin(url, url_match.group(1))
                    pdf_links.append({
                        'url': full_url,
                        'text': element.get_text(strip=True) or 'Untitled',
                        'title': element.get('title', '')
                    })

        # Method 3: Look for data-* attributes that might contain document IDs
        for element in soup.find_all(attrs={'data-document-id': True}):
            doc_id = element.get('data-document-id')
            # This is speculative - might need adjustment based on actual site structure
            potential_url = f"https://documents.dep.wv.gov/document/{doc_id}.pdf"
            pdf_links.append({
                'url': potential_url,
                'text': element.get_text(strip=True) or f'Document_{doc_id}',
                'title': element.get('title', '')
            })

        # Remove duplicates
        seen_urls = set()
        unique_links = []
        for link in pdf_links:
            if link['url'] not in seen_urls:
                seen_urls.add(link['url'])
                unique_links.append(link)

        return unique_links

    def download_pdf(self, url, filename=None):
        """Download a PDF file."""
        try:
            print(f"Downloading: {url}")
            response = self.session.get(url, timeout=60, stream=True)
            response.raise_for_status()

            # Check if response is actually a PDF
            content_type = response.headers.get('Content-Type', '')
            if 'pdf' not in content_type.lower() and 'application/octet-stream' not in content_type.lower():
                print(f"  Warning: Content-Type is {content_type}, may not be a PDF")

            # Determine filename
            if not filename:
                # Try to get filename from Content-Disposition header
                content_disp = response.headers.get('Content-Disposition', '')
                if 'filename=' in content_disp:
                    filename = re.findall(r'filename=([^;]+)', content_disp)[0].strip('"\'')
                else:
                    # Generate from URL
                    filename = os.path.basename(urlparse(url).path)
                    if not filename or not filename.endswith('.pdf'):
                        filename = f"document_{hash(url)}.pdf"

            filename = self.sanitize_filename(filename)
            filepath = self.output_dir / filename

            # Download with progress
            total_size = int(response.headers.get('content-length', 0))
            with open(filepath, 'wb') as f:
                if total_size:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        percent = (downloaded / total_size) * 100
                        print(f"  Progress: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='\r')
                    print()  # New line after progress
                else:
                    f.write(response.content)

            print(f"  Saved: {filepath}")
            return filepath

        except Exception as e:
            print(f"  Error downloading {url}: {e}")
            return None

    def scrape_and_download(self, url):
        """Main method to scrape page and download all PDFs."""
        print(f"\n{'='*80}")
        print(f"Starting WV DEP PDF Scraper")
        print(f"Target URL: {url}")
        print(f"Output directory: {self.output_dir}")
        print(f"{'='*80}\n")

        # Find all PDF links
        print("Searching for PDF links...")
        pdf_links = self.find_pdf_links(url)

        if not pdf_links:
            print("No PDF links found on the page.")
            print("\nDebugging: Let me save the page HTML for inspection...")
            response = self.fetch_page(url)
            debug_file = self.output_dir / "page_source.html"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"Page HTML saved to: {debug_file}")
            return []

        print(f"Found {len(pdf_links)} potential PDF link(s)\n")

        # Display found links
        for i, link in enumerate(pdf_links, 1):
            print(f"{i}. {link['text'][:60]}")
            print(f"   URL: {link['url']}")

        print(f"\n{'='*80}")
        print("Starting downloads...\n")

        # Download each PDF
        downloaded_files = []
        for i, link in enumerate(pdf_links, 1):
            print(f"\n[{i}/{len(pdf_links)}]")
            filename = f"{i:03d}_{self.sanitize_filename(link['text'][:50])}.pdf"
            filepath = self.download_pdf(link['url'], filename)
            if filepath:
                downloaded_files.append(filepath)
            time.sleep(1)  # Be polite, don't hammer the server

        print(f"\n{'='*80}")
        print(f"Download complete!")
        print(f"Successfully downloaded {len(downloaded_files)} PDF(s) to: {self.output_dir}")
        print(f"{'='*80}\n")

        return downloaded_files


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Download PDFs from WV DEP document portal',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'url',
        nargs='?',
        default='https://documents.dep.wv.gov/AppEnhancer/datasources/AE/queryResults/%7B5e7eb9cb-3132-4168-bc08-ca9fe3d7cd3b%7D/30/-1?lqid=-1&lqrid=%7B5e7eb9cb-3132-4168-bc08-ca9fe3d7cd3b%7D&lqaid=30',
        help='URL to scrape (default: preset WV DEP URL)'
    )
    parser.add_argument(
        '-o', '--output',
        default='downloaded_pdfs',
        help='Output directory for downloaded PDFs (default: downloaded_pdfs)'
    )
    parser.add_argument(
        '-s', '--selenium',
        action='store_true',
        help='Use Selenium WebDriver (requires Chrome/Chromium installed)'
    )

    args = parser.parse_args()

    scraper = WVDEPScraper(output_dir=args.output, use_selenium=args.selenium)
    scraper.scrape_and_download(args.url)


if __name__ == '__main__':
    main()
