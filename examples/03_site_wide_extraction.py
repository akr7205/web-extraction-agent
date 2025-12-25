"""
Example 3: Site-wide extraction and crawling.

This example demonstrates how to extract data from an entire website
by crawling multiple pages.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from agent.web_extractor import WebExtractionAgent


def main():
    """Run site-wide extraction example."""
    print("=" * 70)
    print("Example 3: Site-Wide Extraction")
    print("=" * 70)
    
    # Initialize agent
    agent = WebExtractionAgent(use_llm=False)
    
    # Crawl and extract from entire site
    start_url = "https://example.com"
    keywords = ["example", "domain"]
    max_pages = 5  # Limit for demo purposes
    max_depth = 2
    
    print(f"\nStart URL: {start_url}")
    print(f"Keywords: {', '.join(keywords)}")
    print(f"Max Pages: {max_pages}, Max Depth: {max_depth}")
    print("\nCrawling... (this may take a moment)\n")
    
    # Perform site-wide extraction
    result = agent.extract_from_site_semantic(
        start_url=start_url,
        query=', '.join(keywords),
        max_pages=max_pages,
        max_depth=max_depth,
        use_llm=False
    )
    
    # Display results
    print(f"✅ Total Pages Crawled: {result['total_pages_crawled']}")
    print(f"✅ Successful Extractions: {result['successful_extractions']}")
    print(f"✅ Failed Extractions: {result['failed_extractions']}")
    print(f"✅ Total Time: {result['metadata']['total_duration_ms']}ms")
    
    # Show summary statistics
    if result.get('summary'):
        summary = result['summary']
        print(f"\n📈 Summary Statistics:")
        print(f"   Average Relevance: {summary.get('avg_relevance', 0):.3f}")
        print(f"   Total Matches: {summary.get('total_matches', 0)}")
        
        # Show top pages
        if summary.get('top_relevant_pages'):
            print(f"\n🏆 Top 3 Most Relevant Pages:")
            for i, page in enumerate(summary['top_relevant_pages'][:3], 1):
                print(f"\n   {i}. {page['title'][:50]}")
                print(f"      URL: {page['url']}")
                print(f"      Relevance: {page['relevance']:.3f}")
    
    print("\n" + "=" * 70)
    print("Example completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
