"""Entity extraction module using rule-based patterns."""
import re
from typing import List, Dict, Any
from datetime import datetime
from dateutil import parser as date_parser

from config import ENTITY_TYPES


class Entity:
    """Represents an extracted entity."""
    
    def __init__(self, name: str, entity_type: str, value: str, confidence: float = 0.8):
        self.name = name
        self.type = entity_type
        self.value = value
        self.confidence = confidence
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        return {
            "name": self.name,
            "type": self.type,
            "value": self.value,
            "confidence": self.confidence
        }


class EntityExtractor:
    """Extract named entities from text using rule-based patterns."""
    
    def __init__(self):
        self.patterns = {
            k: re.compile(v, re.IGNORECASE) for k, v in ENTITY_TYPES.items()
        }
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract entities from text with improved quality and deduplication.
        
        Args:
            text: Text to extract entities from
            
        Returns:
            List of entity dictionaries with name, type, value, and confidence
        """
        entities = []
        seen = set()  # Avoid duplicates
        
        # Extract AMOUNT entities
        amounts = self._extract_amounts(text)
        for amount in amounts:
            key = (amount.type, amount.value.lower())
            if key not in seen:
                entities.append(amount.to_dict())
                seen.add(key)
        
        # Extract DATE entities
        dates = self._extract_dates(text)
        for date in dates:
            key = (date.type, date.value.lower())
            if key not in seen:
                entities.append(date.to_dict())
                seen.add(key)
        
        # Extract PERSON entities
        persons = self._extract_persons(text)
        for person in persons:
            key = (person.type, person.name.lower())
            if key not in seen:
                entities.append(person.to_dict())
                seen.add(key)
        
        # Extract COMPANY entities
        companies = self._extract_companies(text)
        for company in companies:
            key = (company.type, company.name.lower())
            if key not in seen:
                entities.append(company.to_dict())
                seen.add(key)
        
        # Sort by confidence (highest first) and limit to top entities
        entities.sort(key=lambda e: e.get('confidence', 0), reverse=True)
        return entities[:30]  # Return top 30 entities
    
    def _extract_amounts(self, text: str) -> List[Entity]:
        """Extract monetary amounts and quantities."""
        entities = []
        
        # Match currency amounts: $1,000 or $1.5M
        currency_pattern = r'\$[\d,]+(?:\.\d{2})?|\d+(?:\.\d+)?\s*(?:million|billion|thousand|M|B|K)'
        matches = re.finditer(currency_pattern, text, re.IGNORECASE)
        for match in matches:
            value = match.group(0).strip()
            normalized = self._normalize_amount(value)
            if normalized:
                entities.append(Entity(
                    name=value,
                    entity_type="AMOUNT",
                    value=normalized,
                    confidence=0.9
                ))
        
        return entities[:20]  # Limit to 20 to avoid noise
    
    def _normalize_amount(self, amount: str) -> str:
        """Normalize amount to standard format."""
        amount_clean = amount.strip()
        
        # Convert multipliers
        amount_clean = amount_clean.replace("million", "M")
        amount_clean = amount_clean.replace("billion", "B")
        amount_clean = amount_clean.replace("thousand", "K")
        
        return amount_clean
    
    def _extract_dates(self, text: str) -> List[Entity]:
        """Extract date entities."""
        entities = []
        
        # Match common date formats: MM/DD/YYYY, DD-MM-YYYY, Mon DD, YYYY
        date_pattern = r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2},?\s+\d{4}'
        matches = re.finditer(date_pattern, text, re.IGNORECASE)
        
        for match in matches:
            date_str = match.group(0)
            try:
                # Try to parse and normalize the date
                parsed_date = date_parser.parse(date_str, fuzzy=False)
                formatted = parsed_date.strftime("%Y-%m-%d")
                entities.append(Entity(
                    name=date_str,
                    entity_type="DATE",
                    value=formatted,
                    confidence=0.85
                ))
            except (ValueError, TypeError):
                # If parsing fails, keep original format
                entities.append(Entity(
                    name=date_str,
                    entity_type="DATE",
                    value=date_str,
                    confidence=0.6
                ))
        
        return entities[:20]
    
    def _extract_persons(self, text: str) -> List[Entity]:
        """Extract person names using improved capitalization patterns."""
        entities = []
        seen_names = set()
        
        # Common titles that indicate a person name follows
        titles = ['Mr.', 'Ms.', 'Mrs.', 'Dr.', 'Prof.', 'CEO', 'President', 'Director']
        
        # Match sequences of capitalized words (likely names)
        words = text.split()
        for i in range(len(words) - 1):
            word1 = words[i].strip('.,;:!?()"\'')
            word2 = words[i + 1].strip('.,;:!?()"\'')
            
            # Check for title + name pattern
            has_title = i > 0 and any(words[i-1].startswith(t) for t in titles)
            
            # Check if both words are capitalized and not at sentence start
            if (word1 and word1[0].isupper() and len(word1) > 1 and
                word2 and word2[0].isupper() and len(word2) > 1):
                
                # Filter out common false positives
                if (not word1.isupper() or len(word1) > 3) and \
                   (not word2.isupper() or len(word2) > 3):
                    
                    name = f"{word1} {word2}"
                    name_lower = name.lower()
                    
                    # Avoid duplicates and very common words
                    if name_lower not in seen_names and \
                       word1.lower() not in ['the', 'this', 'that', 'these', 'those'] and \
                       word2.lower() not in ['the', 'this', 'that', 'these', 'those']:
                        
                        # Higher confidence if title is present
                        confidence = 0.75 if has_title else 0.65
                        
                        entities.append(Entity(
                            name=name,
                            entity_type="PERSON",
                            value=name,
                            confidence=confidence
                        ))
                        seen_names.add(name_lower)
        
        return entities[:15]
    
    def _extract_companies(self, text: str) -> List[Entity]:
        """Extract company names with improved pattern matching."""
        entities = []
        seen_companies = set()
        
        # Match company name patterns with business suffixes
        company_pattern = r'\b[A-Z][\w\s&]+(?:Inc\.|LLC|Ltd\.|Corp\.|Corporation|Company|Inc|Co\.|Group|PLC|Ltd)\b'
        matches = re.finditer(company_pattern, text)
        
        for match in matches:
            name = match.group(0).strip()
            name_lower = name.lower()
            
            # Filter out short/generic matches and duplicates
            if len(name) > 3 and len(name) < 100 and name_lower not in seen_companies:
                # Higher confidence for well-formed company names
                confidence = 0.90 if any(suffix in name for suffix in ['Inc.', 'Corp.', 'LLC', 'Ltd.']) else 0.85
                
                entities.append(Entity(
                    name=name,
                    entity_type="COMPANY",
                    value=name,
                    confidence=confidence
                ))
                seen_companies.add(name_lower)
        
        # Also look for well-known company patterns without suffixes
        # Match: Apple, Google, Microsoft (capitalized standalone names in specific contexts)
        tech_pattern = r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)?)\s+(?:announced|launched|released|acquired|developed|created|introduced)\b'
        tech_matches = re.finditer(tech_pattern, text)
        
        for match in tech_matches:
            name = match.group(1).strip()
            name_lower = name.lower()
            
            if len(name) > 2 and name_lower not in seen_companies:
                entities.append(Entity(
                    name=name,
                    entity_type="COMPANY",
                    value=name,
                    confidence=0.70
                ))
                seen_companies.add(name_lower)
        
        return entities[:20]  # Increased limit for companies
