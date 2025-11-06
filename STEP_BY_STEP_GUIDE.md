# Step-by-Step Guide: Running the WV DEP PDF Scraper

## Prerequisites Check

### Step 1: Check if Python is installed

Open a terminal/command prompt and run:

```bash
python --version
```

Or try:
```bash
python3 --version
```

**Expected output:** `Python 3.7` or higher (e.g., `Python 3.11.0`)

**If Python is not installed:**
- Windows: Download from https://www.python.org/downloads/
- Mac: `brew install python3` or download from python.org
- Linux: `sudo apt install python3 python3-pip` (Ubuntu/Debian)

---

## Installation Steps

### Step 2: Navigate to the project directory

```bash
cd /path/to/WV_CWA-401
```

In your case:
```bash
cd /home/user/WV_CWA-401
```

### Step 3: (Optional but Recommended) Create a virtual environment

This keeps the project dependencies isolated:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

**Expected output:** Your prompt should change to show `(venv)` at the beginning

### Step 4: Install Playwright and BeautifulSoup

```bash
pip install playwright beautifulsoup4
```

**Expected output:** You'll see download progress and "Successfully installed..." messages

### Step 5: Install Chromium browser for Playwright

```bash
playwright install chromium
```

**Expected output:** Download progress bar and "Chromium ... downloaded"

---

## Running the Scraper

### Step 6: Run the scraper with default URL

**Basic run (headless mode - no visible browser):**
```bash
python scrape_pdfs_playwright.py
```

**OR run with visible browser (recommended for first time):**
```bash
python scrape_pdfs_playwright.py --no-headless
```

### Step 7: Watch the output

You should see:
```
Starting WV DEP PDF Scraper (Playwright)
Target URL: https://documents.dep.wv.gov/...
Output directory: downloaded_pdfs
Headless mode: True
================================================================================

Launching browser...
Navigating to https://documents.dep.wv.gov/...
Page loaded successfully!
Screenshot saved to: downloaded_pdfs/page_screenshot.png
HTML saved to: downloaded_pdfs/page_source.html

Searching for PDF links and download buttons...
Found X potential PDF link(s)/button(s):
1. Document Name Here
   URL: https://...

================================================================================
Starting downloads...

[1/X] Document Name
  Downloading from URL: https://...
  Saved: downloaded_pdfs/001_Document_Name.pdf

...

================================================================================
Download complete!
Successfully downloaded X PDF(s) to: downloaded_pdfs
================================================================================
```

---

## What Gets Created

After running, you'll see a new folder `downloaded_pdfs/` containing:

1. **PDF files:** `001_Document_Name.pdf`, `002_Another_Doc.pdf`, etc.
2. **page_screenshot.png** - Screenshot of the webpage (for debugging)
3. **page_source.html** - HTML source (for debugging)

---

## Common Scenarios

### Scenario 1: Using a different URL

```bash
python scrape_pdfs_playwright.py "https://your-new-url-here"
```

### Scenario 2: Save to a different folder

```bash
python scrape_pdfs_playwright.py -o my_custom_folder
```

### Scenario 3: Debug mode (see what's happening)

```bash
python scrape_pdfs_playwright.py --no-headless
```

This will show the browser window so you can see exactly what the script is doing.

---

## Troubleshooting

### Problem: "playwright: command not found" or "No module named 'playwright'"

**Solution:**
```bash
pip install playwright
playwright install chromium
```

### Problem: "Permission denied" on Linux/Mac

**Solution:**
```bash
chmod +x scrape_pdfs_playwright.py
```

### Problem: No PDFs found

**Solution:**
1. Check the screenshot: `downloaded_pdfs/page_screenshot.png`
2. Open `downloaded_pdfs/page_source.html` in a browser
3. The URL might be expired or session-specific - get a fresh URL
4. Run with `--no-headless` to see what the browser sees

### Problem: "Browser executable not found"

**Solution:**
```bash
playwright install chromium
```

### Problem: Downloads fail or timeout

**Solution:**
- Check your internet connection
- The website might be down or blocking requests
- Try running with `--no-headless` to see what's happening

---

## Quick Reference Commands

```bash
# Basic run
python scrape_pdfs_playwright.py

# See browser while it runs
python scrape_pdfs_playwright.py --no-headless

# Custom URL
python scrape_pdfs_playwright.py "YOUR_URL"

# Custom output folder
python scrape_pdfs_playwright.py -o custom_folder

# Full custom command
python scrape_pdfs_playwright.py "YOUR_URL" -o custom_folder --no-headless

# Get help
python scrape_pdfs_playwright.py --help
```

---

## Next Steps

1. Navigate to the `downloaded_pdfs` folder to see your PDFs
2. If no PDFs were found, check the screenshot and HTML files
3. If the URL is session-specific, get a fresh URL from the website and try again

---

## Deactivating Virtual Environment (when done)

If you created a virtual environment, deactivate it when done:

```bash
deactivate
```

Your prompt will return to normal (without `(venv)`).
