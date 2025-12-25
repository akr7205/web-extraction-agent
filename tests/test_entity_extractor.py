"""Unit tests for entity extractor."""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from extractors.entity_extractor import EntityExtractor


class TestEntityExtractor:
    """Test cases for EntityExtractor class."""
    
    def test_initialization(self):
        """Test that EntityExtractor initializes correctly."""
        extractor = EntityExtractor()
        assert extractor is not None
    
    def test_extract_companies(self):
        """Test company extraction."""
        extractor = EntityExtractor()
        text = "Apple Inc. and Microsoft Corporation are technology companies."
        entities = extractor.extract_entities(text)
        
        # Should find at least one company
        company_entities = [e for e in entities if e['type'] in ['COMPANY', 'ORG']]
        assert len(company_entities) > 0
    
    def test_extract_people(self):
        """Test person extraction."""
        extractor = EntityExtractor()
        text = "Steve Jobs and Bill Gates founded major tech companies."
        entities = extractor.extract_entities(text)
        
        # Should find at least one person
        person_entities = [e for e in entities if e['type'] == 'PERSON']
        assert len(person_entities) > 0
    
    def test_extract_dates(self):
        """Test date extraction."""
        extractor = EntityExtractor()
        text = "The company was founded on January 1, 2000."
        entities = extractor.extract_entities(text)
        
        # Should find at least one date
        date_entities = [e for e in entities if e['type'] == 'DATE']
        assert len(date_entities) > 0
    
    def test_extract_amounts(self):
        """Test amount/money extraction."""
        extractor = EntityExtractor()
        text = "The revenue was $100 million in the first quarter."
        entities = extractor.extract_entities(text)
        
        # Should find at least one amount
        amount_entities = [e for e in entities if e['type'] in ['AMOUNT', 'MONEY']]
        assert len(amount_entities) > 0
    
    def test_empty_text(self):
        """Test extraction with empty text."""
        extractor = EntityExtractor()
        entities = extractor.extract_entities("")
        assert entities == []
