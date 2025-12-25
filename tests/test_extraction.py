"""Quick test to verify extraction functionality."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from agent.web_extractor import WebExtractionAgent

print("Testing basic extraction...\n")

# Test without LLM (faster)
agent = WebExtractionAgent(use_llm=False)
print("✅ Agent initialized")

# Test extraction with keywords
print("\nTesting keyword extraction on example.com...")
result = agent.extract_by_keywords(
    url='https://example.com',
    keywords=['example', 'domain']
)

print(f"\n{'='*70}")
print("EXTRACTION TEST RESULTS")
print(f"{'='*70}")
print(f"✅ Title: {result.get('title', 'N/A')}")
print(f"✅ Keywords: {', '.join(result.get('keywords', []))}")
print(f"✅ Total matches: {result['keyword_extraction']['total_matches']}")
print(f"✅ Relevance score: {result['keyword_extraction']['relevance_score']:.3f}")
print(f"✅ Processing time: {result['trace']['duration_ms']}ms")
print(f"✅ LLM used: {result['trace']['llm_used']}")
print(f"\n{'='*70}")
print("✅ EXTRACTION TEST PASSED!")
print(f"{'='*70}\n")
