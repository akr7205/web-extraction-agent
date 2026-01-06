"""
Example 4: Using the Web Extractor as a Python library.

This example shows different ways to use the Web Extractor Agent
in your own Python applications.
"""

import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from agent.web_extractor import WebExtractionAgent


def example_1_simple_extraction():
    """Simple keyword-based extraction."""
    print("\n1. Simple Keyword Extraction")
    print("-" * 50)
    
    agent = WebExtractionAgent(use_llm=False)
    result = agent.extract_by_keywords(
        url="https://example.com",
        keywords=["example", "domain"]
    )
    
    print(f"Title: {result['title']}")
    print(f"Matches: {result['keyword_extraction']['total_matches']}")


def example_2_multiple_urls():
    """Extract from multiple URLs."""
    print("\n2. Multiple URL Extraction")
    print("-" * 50)
    
    agent = WebExtractionAgent(use_llm=False)
    urls = ["https://example.com", "https://example.org"]
    keywords = ["example"]
    
    results = []
    for url in urls:
        result = agent.extract_by_keywords(url=url, keywords=keywords)
        results.append({
            "url": url,
            "title": result['title'],
            "relevance": result['keyword_extraction']['relevance_score']
        })
    
    print(f"Processed {len(results)} URLs:")
    for r in results:
        print(f"  • {r['title']}: {r['relevance']:.3f}")


def example_3_save_to_file():
    """Extract and save results to file."""
    print("\n3. Save Results to File")
    print("-" * 50)
    
    agent = WebExtractionAgent(use_llm=False)
    result = agent.extract_by_keywords(
        url="https://example.com",
        keywords=["example"]
    )
    
    output_file = "extraction_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Results saved to: {output_file}")


def example_4_error_handling():
    """Proper error handling."""
    print("\n4. Error Handling")
    print("-" * 50)
    
    agent = WebExtractionAgent(use_llm=False)
    
    try:
        result = agent.extract_by_keywords(
            url="https://invalid-url-that-does-not-exist.com",
            keywords=["test"]
        )
        print(f"Success: {result['title']}")
    except Exception as e:
        print(f"Error occurred: {type(e).__name__}")
        print(f"Message: {str(e)}")
        print("✓ Error handled gracefully")


def main():
    """Run all examples."""
    print("=" * 70)
    print("Example 4: Using as a Python Library")
    print("=" * 70)
    
    example_1_simple_extraction()
    example_2_multiple_urls()
    example_3_save_to_file()
    example_4_error_handling()
    
    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
