#!/usr/bin/env python3
"""
Simple test script to check what we can access from the WV DEP website.
This uses only basic requests/cloudscraper (no browser required).
"""

import requests
import cloudscraper

URL = "https://documents.dep.wv.gov/AppEnhancer/datasources/AE/queryResults/%7B5e7eb9cb-3132-4168-bc08-ca9fe3d7cd3b%7D/30/-1?lqid=-1&lqrid=%7B5e7eb9cb-3132-4168-bc08-ca9fe3d7cd3b%7D&lqaid=30"

print("="*80)
print("Testing WV DEP Website Access")
print("="*80)

# Test 1: Basic requests
print("\n[Test 1] Using basic requests...")
try:
    response = requests.get(URL, timeout=10)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("✅ Success with basic requests!")
        print(f"Content length: {len(response.content)} bytes")
    else:
        print(f"❌ Failed: {response.status_code} {response.reason}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Cloudscraper
print("\n[Test 2] Using cloudscraper (anti-bot bypass)...")
try:
    scraper = cloudscraper.create_scraper()
    response = scraper.get(URL, timeout=10)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("✅ Success with cloudscraper!")
        print(f"Content length: {len(response.content)} bytes")

        # Save the HTML
        with open('test_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("📄 Saved response to: test_response.html")
    else:
        print(f"❌ Failed: {response.status_code} {response.reason}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*80)
print("Conclusion:")
print("="*80)
print("""
If both tests failed with 403:
- The website has strict anti-bot protection
- You MUST use the Playwright version on your local machine
- Run: python scrape_pdfs_playwright.py

If either test succeeded:
- Check test_response.html to see what the page contains
- The traditional scraper might work
""")
