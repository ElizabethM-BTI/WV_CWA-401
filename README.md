# WV DEP PDF Scraper

Python scripts to download PDFs from the West Virginia Department of Environmental Protection (WV DEP) document portal.

## ⚠️ Important Note About Anti-Bot Protection

The WV DEP website has strict anti-bot protection that blocks automated requests. This repository provides **two different approaches**:

1. **`scrape_pdfs_playwright.py`** ✅ **RECOMMENDED** - Uses Playwright with a real browser to bypass protection
2. **`scrape_pdfs.py`** - Traditional approach with requests/cloudscraper (may be blocked by the website)

## Features

- Multiple scraping methods to handle anti-bot protection
- Downloads PDFs from WV DEP query results pages
- Automatic retry logic with exponential backoff
- Progress tracking and screenshots for debugging
- Sanitizes filenames for cross-platform compatibility
- Saves page HTML and screenshots for debugging

## Quick Start (Playwright - Recommended)

1. Install Python 3.7 or higher

2. Install Playwright and dependencies:
```bash
pip install playwright beautifulsoup4
playwright install chromium
```

3. Run the scraper:
```bash
python scrape_pdfs_playwright.py
```

## Installation Options

### Option 1: Playwright (Recommended)

Best for sites with anti-bot protection:

```bash
pip install playwright beautifulsoup4
playwright install chromium
```

### Option 2: Requests/Cloudscraper

Simpler but may be blocked:

```bash
pip install requests beautifulsoup4 lxml cloudscraper
```

### Option 3: Install All Dependencies

```bash
pip install -r requirements.txt
playwright install chromium  # Only needed if using Playwright
```

## Usage

### Using Playwright (Recommended)

#### Basic Usage

Run with the default URL:
```bash
python scrape_pdfs_playwright.py
```

#### Custom URL and Options

```bash
python scrape_pdfs_playwright.py "YOUR_URL_HERE" -o my_pdfs
```

#### Debug Mode (See Browser)

Run with visible browser to see what's happening:
```bash
python scrape_pdfs_playwright.py --no-headless
```

#### Complete Example

```bash
python scrape_pdfs_playwright.py \
  "https://documents.dep.wv.gov/AppEnhancer/datasources/AE/queryResults/%7B5e7eb9cb-3132-4168-bc08-ca9fe3d7cd3b%7D/30/-1?lqid=-1&lqrid=%7B5e7eb9cb-3132-4168-bc08-ca9fe3d7cd3b%7D&lqaid=30" \
  --output downloaded_pdfs \
  --no-headless
```

### Using Requests/Cloudscraper (Alternative)

**Note:** This method may be blocked by the website's anti-bot protection.

#### Basic Usage

```bash
python scrape_pdfs.py
```

#### With Selenium

If cloudscraper is blocked, try Selenium:
```bash
python scrape_pdfs.py --selenium
```

#### Custom Options

```bash
python scrape_pdfs.py "YOUR_URL_HERE" -o my_pdfs
```

## How It Works

### Playwright Version (scrape_pdfs_playwright.py)

1. **Launch real browser**: Uses Chromium to act like a real user
2. **Navigate to page**: Loads the page with full JavaScript support
3. **Find PDFs**: Searches for PDF links, download buttons, and clickable elements
4. **Download files**: Handles downloads through the browser
5. **Save files**: Saves PDFs with sanitized, numbered filenames
6. **Screenshots**: Saves screenshots and HTML for debugging

### Traditional Version (scrape_pdfs.py)

1. **Fetch the page**: Uses cloudscraper/requests with browser-like headers
2. **Parse HTML**: Uses BeautifulSoup to find all PDF links
3. **Download PDFs**: Downloads each PDF with progress tracking
4. **Save files**: Saves PDFs with sanitized, numbered filenames

## Output

Downloaded PDFs will be saved in the specified output directory (default: `downloaded_pdfs/`) with filenames like:
- `001_Document_Name.pdf`
- `002_Another_Document.pdf`
- etc.

If no PDFs are found, the script will save the page HTML as `page_source.html` for debugging.

## Troubleshooting

### 403 Forbidden errors (scrape_pdfs.py)

If you get 403 errors with the traditional script:
1. **Use Playwright instead**: Run `python scrape_pdfs_playwright.py`
2. The website has strict anti-bot protection that blocks automated HTTP requests
3. Playwright uses a real browser which is much more effective

### No PDFs found

If the script reports no PDFs found:
1. **Check the screenshot** (Playwright only): `downloaded_pdfs/page_screenshot.png`
2. **Check the HTML**: Look at `page_source.html` in the output directory
3. The website structure may have changed
4. The URL may be session-specific and expired
5. Try running with `--no-headless` to see what the browser sees

### Session/Authentication Issues

If the URL requires authentication or session cookies:
1. The URLs may be temporary or session-specific
2. You may need to login first in a browser
3. Consider using browser developer tools to inspect the actual download URLs
4. You might need to manually extract cookies and add them to the script

### Playwright Installation Issues

If you get errors about Playwright or Chromium:
```bash
# Reinstall Playwright
pip uninstall playwright
pip install playwright
playwright install chromium

# Or install specific browser
playwright install --help
```

### Download failures

If downloads fail:
1. Check your internet connection
2. The server may be rate-limiting (script includes 1-second delays)
3. The PDF URLs may have expired
4. Try running in debug mode with `--no-headless` to see what's happening

## Advanced Usage

### Programmatic Usage (Playwright)

```python
import asyncio
from scrape_pdfs_playwright import WVDEPPlaywrightScraper

async def main():
    scraper = WVDEPPlaywrightScraper(output_dir="my_pdfs", headless=True)
    downloaded_files = await scraper.scrape_and_download("YOUR_URL")

    for file in downloaded_files:
        print(f"Downloaded: {file}")

asyncio.run(main())
```

### Programmatic Usage (Traditional)

```python
from scrape_pdfs import WVDEPScraper

scraper = WVDEPScraper(output_dir="my_pdfs")
downloaded_files = scraper.scrape_and_download("YOUR_URL")

for file in downloaded_files:
    print(f"Downloaded: {file}")
```

### Add Authentication/Cookies

For Playwright, you can add cookies or login:

```python
# In scrape_pdfs_playwright.py, after creating context:
await context.add_cookies([
    {
        'name': 'session_id',
        'value': 'your_session_value',
        'domain': 'documents.dep.wv.gov',
        'path': '/'
    }
])
```

For traditional approach:

```python
# In scrape_pdfs.py, in __init__ method:
self.session.cookies.update({
    'session_id': 'your_session_cookie',
    # Add other cookies as needed
})
```

## Requirements

### Playwright Version (Recommended)
- Python 3.7+
- playwright >= 1.40.0
- beautifulsoup4 >= 4.12.0

### Traditional Version
- Python 3.7+
- requests >= 2.31.0
- beautifulsoup4 >= 4.12.0
- lxml >= 4.9.0
- cloudscraper >= 1.2.71
- selenium >= 4.15.0 (optional, for --selenium flag)

## What to Expect

When you run the Playwright version, you should see:
1. Browser launch message
2. Page navigation
3. Screenshot saved (for debugging)
4. List of found PDF links/buttons
5. Download progress for each PDF
6. Final summary with count of downloaded files

The script creates debugging files:
- `page_screenshot.png` - Visual capture of the page
- `page_source.html` - HTML source for inspection
- `001_Document_Name.pdf`, `002_...pdf`, etc. - Downloaded PDFs

## Common Issues

1. **URL is session-specific**: Some document portals generate temporary URLs that expire. You may need to get a fresh URL each time.

2. **Dynamic content loading**: The Playwright version waits for content to load, but if PDFs are loaded via complex JavaScript, you may need to adjust wait times.

3. **Rate limiting**: The script includes 1-second delays between downloads. If you get blocked, increase this delay.

## License

This tool is provided as-is for legitimate use in accessing public documents.

## Disclaimer

- Please be respectful of the WV DEP servers and don't hammer them with requests
- The script includes a 1-second delay between downloads to be polite
- Some websites may have Terms of Service regarding automated access - please review before use
- Ensure you have the right to access and download these documents
- This tool is for educational and legitimate research purposes
