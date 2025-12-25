"""
Example 1: Basic keyword extraction from a single URL.

This example demonstrates how to extract content based on keywords
from a single webpage.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from agent.web_extractor import WebExtractionAgent


def main():
    """Run basic keyword extraction example."""
    print("=" * 70)
    print("Example 1: Basic Keyword Extraction")
    print("=" * 70)
    
    # Initialize agent without LLM for faster extraction
    agent = WebExtractionAgent(use_llm=False)
    
    # Extract from example.com
    url = "https://example.com"
    keywords = ["example", "domain", "illustrative"]
    
    print(f"\nExtracting from: {url}")
    print(f"Keywords: {', '.join(keywords)}")
    print("\nProcessing...\n")
    
    # Perform extraction
    result = agent.extract_by_keywords(
        url=url,
        keywords=keywords
    )
    
    # Display results
    print(f"✅ Title: {result['title']}")
    print(f"✅ Relevance Score: {result['keyword_extraction']['relevance_score']:.3f}")
    print(f"✅ Total Matches: {result['keyword_extraction']['total_matches']}")
    print(f"✅ Processing Time: {result['trace']['duration_ms']}ms")
    
    # Show matched sections
    if result['keyword_extraction']['matched_sections']:
        print(f"\n📑 Top Matched Sections:")
        for i, section in enumerate(result['keyword_extraction']['matched_sections'][:3], 1):
            print(f"\n  {i}. Relevance: {section['relevance_score']:.3f}")
            print(f"     Keywords: {', '.join(section['matched_keywords'])}")
            preview = section['text'][:100] + "..." if len(section['text']) > 100 else section['text']
            print(f"     Preview: {preview}")
    
    print("\n" + "=" * 70)
    print("Example completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
