"""Unit tests for keyword extractor."""

import pytest
import sys
from pathlib import Path
from bs4 import BeautifulSoup

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from extractors.keyword_extractor import KeywordExtractor


class TestKeywordExtractor:
    """Test cases for KeywordExtractor class."""
    
    def test_initialization(self):
        """Test that KeywordExtractor initializes correctly."""
        extractor = KeywordExtractor()
        assert extractor is not None
    
    def test_extract_by_keywords(self, sample_html, sample_keywords):
        """Test keyword extraction from HTML."""
        extractor = KeywordExtractor()
        soup = BeautifulSoup(sample_html, 'html.parser')
        
        result = extractor.extract_by_keywords(soup, sample_keywords)
        
        assert 'total_matches' in result
        assert 'relevance_score' in result
        assert 'matched_sections' in result
        assert result['total_matches'] >= 0
        assert 0 <= result['relevance_score'] <= 1
    
    def test_keyword_matching_case_insensitive(self):
        """Test that keyword matching is case-insensitive."""
        extractor = KeywordExtractor()
        html = "<html><body><p>PYTHON is great. python rocks!</p></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        keywords = ["python"]
        
        result = extractor.extract_by_keywords(soup, keywords)
        
        # Should match both uppercase and lowercase
        assert result['total_matches'] >= 2
    
    def test_no_matches(self):
        """Test extraction with no keyword matches."""
        extractor = KeywordExtractor()
        html = "<html><body><p>Some random text here.</p></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        keywords = ["nonexistent", "missing"]
        
        result = extractor.extract_by_keywords(soup, keywords)
        
        assert result['total_matches'] == 0
        assert result['relevance_score'] == 0
    
    def test_empty_keywords(self, sample_html):
        """Test extraction with empty keyword list."""
        extractor = KeywordExtractor()
        soup = BeautifulSoup(sample_html, 'html.parser')
        
        result = extractor.extract_by_keywords(soup, [])
        
        assert result['total_matches'] == 0
        assert result['relevance_score'] == 0
