"""Unit tests for web extractor agent."""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from agent.web_extractor import WebExtractionAgent


class TestWebExtractionAgent:
    """Test cases for WebExtractionAgent class."""
    
    def test_initialization_without_llm(self):
        """Test agent initialization without LLM."""
        agent = WebExtractionAgent(use_llm=False)
        assert agent is not None
        assert agent.rule_extractor is not None
        assert agent.keyword_extractor is not None
    
    def test_initialization_with_llm(self):
        """Test agent initialization with LLM."""
        agent = WebExtractionAgent(use_llm=True)
        assert agent is not None
    
    def test_extract_by_keywords(self, sample_url):
        """Test keyword-based extraction."""
        agent = WebExtractionAgent(use_llm=False)
        
        result = agent.extract_by_keywords(
            url=sample_url,
            keywords=['example', 'domain']
        )
        
        assert 'title' in result
        assert 'keyword_extraction' in result
        assert 'trace' in result
        assert result['keyword_extraction']['total_matches'] >= 0
        assert 0 <= result['keyword_extraction']['relevance_score'] <= 1
    
    def test_extract_result_structure(self, sample_url):
        """Test that extraction result has correct structure."""
        agent = WebExtractionAgent(use_llm=False)
        
        result = agent.extract_by_keywords(
            url=sample_url,
            keywords=['test']
        )
        
        # Check required fields
        assert 'title' in result
        assert 'keywords' in result
        assert 'keyword_extraction' in result
        assert 'metadata' in result
        assert 'trace' in result
        
        # Check metadata structure
        assert 'source_url' in result['metadata']
        assert 'fetched_at' in result['metadata']
        
        # Check trace structure
        assert 'duration_ms' in result['trace']
        assert 'llm_used' in result['trace']
