# Manual Download Helper Guide

Since the WV DEP website blocks automated scripts, here's how to download PDFs manually (more efficiently):

## Method 1: Browser Developer Tools

1. **Open the page in your browser:**
   ```
   https://documents.dep.wv.gov/AppEnhancer/datasources/AE/queryResults/%7B5e7eb9cb-3132-4168-bc08-ca9fe3d7cd3b%7D/30/-1?lqid=-1&lqrid=%7B5e7eb9cb-3132-4168-bc08-ca9fe3d7cd3b%7D&lqaid=30
   ```

2. **Open Developer Tools:**
   - Chrome/Edge: Press `F12` or `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)
   - Firefox: Press `F12` or `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)

3. **Go to the Console tab**

4. **Paste this JavaScript code:**

```javascript
// Find all PDF links on the page
const links = Array.from(document.querySelectorAll('a'))
  .filter(a => a.href && (a.href.includes('.pdf') || a.textContent.toLowerCase().includes('pdf')))
  .map((a, index) => ({
    index: index + 1,
    text: a.textContent.trim(),
    url: a.href
  }));

console.log(`Found ${links.length} potential PDF links:`);
console.table(links);

// Copy all URLs to clipboard
const urls = links.map(l => l.url).join('\n');
copy(urls);
console.log('\n✅ URLs copied to clipboard!');
```

5. **Press Enter** - The PDF URLs will be copied to your clipboard

6. **Use a download manager:**
   - Paste the URLs into a download manager like:
     - **JDownloader** (Windows/Mac/Linux) - Free
     - **Internet Download Manager** (Windows) - Paid
     - **Free Download Manager** (Windows/Mac/Linux) - Free

## Method 2: Browser Extension

Use a browser extension like:

### **DownThemAll** (Firefox/Chrome)
1. Install DownThemAll extension
2. Go to the WV DEP page
3. Click the DownThemAll icon
4. Filter for `.pdf` files
5. Download all at once

### **Download All Files** (Chrome)
1. Install "Download All Files" extension
2. Visit the page
3. Click the extension icon
4. Select PDF files
5. Download

## Method 3: Extract Links Script (Run Locally)

If you can access the page in your browser, you can:

1. **Save the page:**
   - In your browser: `Ctrl+S` / `Cmd+S`
   - Save as "Webpage, Complete"

2. **Run this Python script on the saved HTML:**

```python
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests

# Load your saved HTML file
with open('saved_page.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
base_url = "https://documents.dep.wv.gov"

# Find all links
links = soup.find_all('a', href=True)
pdf_links = []

for link in links:
    href = link['href']
    if 'pdf' in href.lower() or 'pdf' in link.text.lower():
        full_url = urljoin(base_url, href)
        pdf_links.append(full_url)

print(f"Found {len(pdf_links)} PDF links:")
for i, url in enumerate(pdf_links, 1):
    print(f"{i}. {url}")

# Save to file
with open('pdf_urls.txt', 'w') as f:
    for url in pdf_links:
        f.write(url + '\n')

print("\nURLs saved to pdf_urls.txt")
```

## Method 4: Use the Playwright Scraper on Your Local Machine

**This is still the best option!**

The automated scraper will work perfectly on your local computer (Windows/Mac/Linux) because:
- It uses a real browser (bypasses anti-bot detection)
- No network restrictions like in cloud environments
- Fully automated - just run and wait

### To use it on your local machine:

```bash
# Install
pip install playwright beautifulsoup4
python -m playwright install chromium

# Run
python scrape_pdfs_playwright.py

# Or watch it work:
python scrape_pdfs_playwright.py --no-headless
```

That's it! The PDFs will be downloaded automatically to `downloaded_pdfs/` folder.

---

## Which Method Should You Use?

- **Have Python locally?** → Use the Playwright scraper ⭐ **BEST**
- **Don't have Python?** → Use browser Developer Tools + download manager
- **Want simple?** → Use a browser extension
- **Tech-savvy?** → Extract links with JavaScript console
