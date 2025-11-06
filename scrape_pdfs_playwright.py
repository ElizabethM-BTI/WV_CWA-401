#!/usr/bin/env python3
"""
WV DEP PDF Scraper - Playwright Version
Uses Playwright with a real browser to bypass anti-bot protection.
This is more reliable for sites with strict bot detection.
"""

import os
import re
import time
import argparse
from pathlib import Path
from urllib.parse import urljoin, urlparse
import asyncio

try:
    from playwright.async_api import async_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    print("ERROR: Playwright not installed!")
    print("Install it with: pip install playwright")
    print("Then run: playwright install chromium")
    exit(1)


class WVDEPPlaywrightScraper:
    """Scraper using Playwright for WV DEP document portal."""

    def __init__(self, output_dir="downloaded_pdfs", headless=True):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless

    def sanitize_filename(self, filename):
        """Sanitize filename to remove invalid characters."""
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:200-len(ext)] + ext
        return filename

    async def scrape_and_download(self, url):
        """Main method to scrape page and download all PDFs."""
        print(f"\n{'='*80}")
        print(f"Starting WV DEP PDF Scraper (Playwright)")
        print(f"Target URL: {url}")
        print(f"Output directory: {self.output_dir}")
        print(f"Headless mode: {self.headless}")
        print(f"{'='*80}\n")

        async with async_playwright() as p:
            # Launch browser
            print("Launching browser...")
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = await context.new_page()

            # Navigate to the page
            print(f"Navigating to {url}")
            try:
                await page.goto(url, wait_until='networkidle', timeout=60000)
                print("Page loaded successfully!")
            except Exception as e:
                print(f"Error loading page: {e}")
                print("Trying with longer timeout...")
                try:
                    await page.goto(url, wait_until='domcontentloaded', timeout=90000)
                    await page.wait_for_timeout(5000)  # Wait 5 seconds for dynamic content
                except Exception as e2:
                    print(f"Still failed: {e2}")
                    await browser.close()
                    return []

            # Save screenshot for debugging
            screenshot_path = self.output_dir / "page_screenshot.png"
            await page.screenshot(path=str(screenshot_path))
            print(f"Screenshot saved to: {screenshot_path}")

            # Save HTML for debugging
            html_content = await page.content()
            html_path = self.output_dir / "page_source.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"HTML saved to: {html_path}")

            # Find all PDF links
            print("\nSearching for PDF links and download buttons...")
            pdf_links = []

            # Method 1: Find direct PDF links
            links = await page.locator('a').all()
            for link in links:
                try:
                    href = await link.get_attribute('href')
                    text = await link.inner_text()
                    if href and ('pdf' in href.lower() or 'pdf' in text.lower()):
                        full_url = urljoin(url, href)
                        pdf_links.append({
                            'url': full_url,
                            'text': text.strip() or 'Untitled',
                            'element': link
                        })
                except:
                    continue

            # Method 2: Look for download buttons or elements with data attributes
            download_elements = await page.locator('[data-document-id], [onclick*="pdf"], [onclick*="download"]').all()
            for element in download_elements:
                try:
                    text = await element.inner_text()
                    doc_id = await element.get_attribute('data-document-id')
                    onclick = await element.get_attribute('onclick')

                    if doc_id:
                        pdf_links.append({
                            'url': None,
                            'text': text.strip() or f'Document_{doc_id}',
                            'element': element,
                            'doc_id': doc_id
                        })
                    elif onclick and 'pdf' in onclick.lower():
                        url_match = re.search(r'["\']([^"\']*\.pdf[^"\']*)["\']', onclick, re.IGNORECASE)
                        if url_match:
                            pdf_url = urljoin(url, url_match.group(1))
                            pdf_links.append({
                                'url': pdf_url,
                                'text': text.strip() or 'Untitled',
                                'element': element
                            })
                except:
                    continue

            # Method 3: Look for any clickable elements with "download" or "PDF" in text
            download_texts = await page.locator('text=/download|pdf|view/i').all()
            for element in download_texts:
                try:
                    tag = await element.evaluate('el => el.tagName')
                    if tag.lower() in ['a', 'button', 'div', 'span']:
                        text = await element.inner_text()
                        if len(text.strip()) > 0:
                            pdf_links.append({
                                'url': None,
                                'text': text.strip(),
                                'element': element
                            })
                except:
                    continue

            # Remove duplicates based on text
            seen_texts = set()
            unique_links = []
            for link in pdf_links:
                if link['text'] not in seen_texts:
                    seen_texts.add(link['text'])
                    unique_links.append(link)

            if not unique_links:
                print("\nNo PDF links or download buttons found!")
                print("Please check the screenshot and HTML files for debugging.")
                await browser.close()
                return []

            print(f"\nFound {len(unique_links)} potential PDF link(s)/button(s):")
            for i, link in enumerate(unique_links, 1):
                print(f"{i}. {link['text'][:70]}")
                if link.get('url'):
                    print(f"   URL: {link['url']}")

            # Download PDFs
            print(f"\n{'='*80}")
            print("Starting downloads...\n")

            downloaded_files = []
            for i, link in enumerate(unique_links, 1):
                print(f"\n[{i}/{len(unique_links)}] {link['text'][:60]}")

                try:
                    if link.get('url'):
                        # Direct URL download
                        print(f"  Downloading from URL: {link['url']}")
                        async with page.expect_download(timeout=60000) as download_info:
                            await page.goto(link['url'])
                        download = await download_info.value
                        filename = f"{i:03d}_{self.sanitize_filename(link['text'][:50])}.pdf"
                        filepath = self.output_dir / filename
                        await download.save_as(str(filepath))
                        print(f"  Saved: {filepath}")
                        downloaded_files.append(filepath)
                    else:
                        # Try clicking the element
                        print(f"  Clicking element to trigger download...")
                        element = link['element']

                        async with page.expect_download(timeout=30000) as download_info:
                            await element.click()
                        download = await download_info.value

                        filename = f"{i:03d}_{self.sanitize_filename(link['text'][:50])}.pdf"
                        filepath = self.output_dir / filename
                        await download.save_as(str(filepath))
                        print(f"  Saved: {filepath}")
                        downloaded_files.append(filepath)

                except Exception as e:
                    print(f"  Error: {e}")
                    print(f"  Skipping this item...")

                await page.wait_for_timeout(1000)  # Wait 1 second between downloads

            await browser.close()

            print(f"\n{'='*80}")
            print(f"Download complete!")
            print(f"Successfully downloaded {len(downloaded_files)} PDF(s) to: {self.output_dir}")
            print(f"{'='*80}\n")

            return downloaded_files


async def main_async():
    """Async main entry point."""
    parser = argparse.ArgumentParser(
        description='Download PDFs from WV DEP document portal using Playwright',
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
        '--no-headless',
        action='store_true',
        help='Run browser in visible mode (useful for debugging)'
    )

    args = parser.parse_args()

    scraper = WVDEPPlaywrightScraper(
        output_dir=args.output,
        headless=not args.no_headless
    )
    await scraper.scrape_and_download(args.url)


def main():
    """Main entry point."""
    asyncio.run(main_async())


if __name__ == '__main__':
    main()
