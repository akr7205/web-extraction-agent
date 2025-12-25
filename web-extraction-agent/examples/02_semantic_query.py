"""
Example 2: Semantic query-based extraction.

This example shows how to use natural language queries
to extract relevant information from web pages.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from agent.web_extractor import WebExtractionAgent


def main():
    """Run semantic query extraction example."""
    print("=" * 70)
    print("Example 2: Semantic Query Extraction")
    print("=" * 70)
    
    # Initialize agent with LLM for better semantic understanding
    # Note: Requires LLM API key in .env file
    agent = WebExtractionAgent(use_llm=True)
    
    # Extract using natural language query
    url = "https://example.com"
    query = "Give me all the information about this domain"
    
    print(f"\nExtracting from: {url}")
    print(f"Query: {query}")
    print("\nProcessing...\n")
    
    # Perform extraction
    try:
        result = agent.extract_by_semantic_query(
            url=url,
            query=query,
            use_llm=True
        )
        
        # Display results
        print(f"✅ Title: {result['title']}")
        print(f"✅ Relevance Score: {result['keyword_extraction']['relevance_score']:.3f}")
        print(f"✅ Processing Time: {result['trace']['duration_ms']}ms")
        print(f"✅ LLM Used: {result['trace']['llm_used']}")
        
        # Show summary if available
        if result['keyword_extraction'].get('summary'):
            print(f"\n📝 Summary:")
            print(f"   {result['keyword_extraction']['summary']}")
        
        print("\n" + "=" * 70)
        print("Example completed!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Note: This example requires LLM API key in .env file")
        print("   Set LITELLM_API_KEY in your .env file to use this feature.")


if __name__ == "__main__":
    main()
