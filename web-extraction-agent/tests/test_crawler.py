"""Test crawler to debug crawling issues."""
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from crawlers.web_crawler import WebCrawler

# Test crawl
print("Testing crawler on analyticsindiamag.com...\n")
crawler = WebCrawler(max_pages=5, max_depth=2, delay_between_requests=1)
results = crawler.crawl('https://analyticsindiamag.com/')

print(f"\n{'='*70}")
print(f"CRAWL RESULTS:")
print(f"{'='*70}")
print(f"Total pages crawled: {len(results)}")
print(f"Visited URLs: {len(crawler.visited_urls)}")
print(f"Disallowed paths: {len(crawler.disallowed_paths)}")

if results:
    for i, page in enumerate(results, 1):
        print(f"\n{i}. {page['title'][:50]}")
        print(f"   URL: {page['url']}")
        print(f"   Depth: {page['depth']}")
        print(f"   HTML length: {len(page['html'])} bytes")
else:
    print("\n⚠️ No pages were crawled!")
    print(f"\nVisited URLs: {crawler.visited_urls}")
    print(f"\nDisallowed paths: {list(crawler.disallowed_paths)[:10]}")
