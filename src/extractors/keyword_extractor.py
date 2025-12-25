"""Keyword-based extraction module for targeted content extraction."""
import logging
import re
from typing import List, Dict, Any, Optional, Set
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)


class KeywordExtractor:
    """Extract content based on user-provided keywords."""
    
    def __init__(self):
        """Initialize keyword extractor."""
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'it', 'its', 'they', 'their', 'them'
        }
        
        # Semantic expansion dictionary for common topics
        self.semantic_expansions = {
            'ai': ['artificial intelligence', 'machine learning', 'deep learning', 'neural network', 
                   'chatgpt', 'llm', 'large language model', 'generative ai', 'ml', 'automation',
                   'computer vision', 'natural language processing', 'nlp', 'algorithm', 'model'],
            'finance': ['financial', 'money', 'investment', 'banking', 'economy', 'economic',
                       'market', 'stock', 'trading', 'capital', 'funding', 'revenue', 'profit',
                       'budget', 'fiscal', 'monetary', 'credit', 'loan', 'debt', 'asset'],
            'technology': ['tech', 'digital', 'software', 'hardware', 'innovation', 'startup',
                          'innovation', 'computing', 'internet', 'cloud', 'data', 'cyber'],
            'health': ['healthcare', 'medical', 'medicine', 'hospital', 'doctor', 'patient',
                      'disease', 'treatment', 'therapy', 'wellness', 'pharmaceutical'],
            'business': ['company', 'corporate', 'enterprise', 'commerce', 'industry',
                        'management', 'strategy', 'operation', 'commercial', 'trade'],
            'politics': ['political', 'government', 'policy', 'election', 'parliament',
                        'legislation', 'senator', 'congress', 'ministry', 'diplomatic'],
            'climate': ['environmental', 'weather', 'global warming', 'carbon', 'emission',
                       'sustainability', 'renewable', 'pollution', 'temperature', 'climate change'],
            'education': ['school', 'university', 'student', 'learning', 'teaching',
                         'academic', 'educational', 'training', 'curriculum', 'scholarship']
        }
    
    def extract_by_keywords(
        self,
        soup: BeautifulSoup,
        keywords: List[str],
        context_sentences: int = 2,
        min_relevance_score: float = 0.2
    ) -> Dict[str, Any]:
        """
        Extract content relevant to provided keywords.
        
        Args:
            soup: BeautifulSoup object of the page
            keywords: List of keywords to search for
            context_sentences: Number of sentences to include before/after keyword match
            min_relevance_score: Minimum relevance score (0-1) for inclusion
            
        Returns:
            Dictionary with keyword-relevant content
        """
        if not keywords:
            logger.warning("No keywords provided")
            return {
                "keywords_used": [],
                "matched_sections": [],
                "summary": "",
                "relevance_score": 0.0
            }
        
        # Normalize keywords
        normalized_keywords = self._normalize_keywords(keywords)
        
        # Expand keywords with semantic variations
        expanded_keywords = self._expand_keywords_semantically(normalized_keywords)
        logger.debug(f"Expanded keywords: {expanded_keywords[:10]}...")  # Log first 10
        
        # Extract text content with structure
        text_blocks = self._extract_text_blocks(soup)
        
        # Find relevant sections using expanded keywords
        matched_sections = []
        for block in text_blocks:
            # Calculate relevance using both original and expanded keywords
            relevance = self._calculate_relevance(block['text'], expanded_keywords)
            if relevance >= min_relevance_score:
                matched_sections.append({
                    "text": block['text'],
                    "tag": block['tag'],
                    "relevance_score": relevance,
                    "matched_keywords": self._find_matched_keywords(block['text'], expanded_keywords),
                    "original_keywords": self._find_matched_keywords(block['text'], normalized_keywords),
                    "context": self._extract_context(block['text'], expanded_keywords, context_sentences)
                })
        
        # Sort by relevance
        matched_sections.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Generate summary
        summary = self._generate_summary(matched_sections, normalized_keywords)
        
        # Calculate overall relevance
        overall_relevance = sum(s['relevance_score'] for s in matched_sections) / max(len(matched_sections), 1)
        
        return {
            "keywords_used": keywords,
            "matched_sections": matched_sections,
            "summary": summary,
            "relevance_score": round(overall_relevance, 3),
            "total_matches": len(matched_sections)
        }
    
    def extract_keyword_entities(
        self,
        text: str,
        keywords: List[str]
    ) -> Dict[str, List[str]]:
        """
        Extract entities related to specific keywords.
        
        Args:
            text: Text content to analyze
            keywords: Keywords to focus extraction on
            
        Returns:
            Dictionary mapping keywords to related entities
        """
        normalized_keywords = self._normalize_keywords(keywords)
        keyword_entities = {}
        
        # Split into sentences
        sentences = self._split_into_sentences(text)
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            entities = set()
            
            for sentence in sentences:
                sentence_lower = sentence.lower()
                if keyword_lower in sentence_lower:
                    # Extract capitalized words/phrases (likely entities)
                    found_entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', sentence)
                    entities.update(found_entities)
                    
                    # Extract numbers with context
                    numbers = re.findall(r'\b\d+(?:,\d{3})*(?:\.\d+)?\s*(?:%|percent|dollars?|\$|€|£|million|billion|thousand)?\b', sentence)
                    entities.update(numbers)
            
            keyword_entities[keyword] = list(entities)
        
        return keyword_entities
    
    def _normalize_keywords(self, keywords: List[str]) -> List[str]:
        """Normalize keywords by lowercasing and removing stop words."""
        normalized = []
        for keyword in keywords:
            # Convert to lowercase
            kw = keyword.lower().strip()
            # Remove if it's a stop word
            if kw not in self.stop_words:
                normalized.append(kw)
        return normalized
    
    def _expand_keywords_semantically(self, keywords: List[str]) -> List[str]:
        """Expand keywords with semantically related terms."""
        expanded = set(keywords)  # Start with original keywords
        
        for keyword in keywords:
            # Check if keyword has semantic expansions
            if keyword in self.semantic_expansions:
                expanded.update(self.semantic_expansions[keyword])
            
            # Add common variations
            # Add plural/singular variations
            if keyword.endswith('s'):
                expanded.add(keyword[:-1])  # Remove 's'
            else:
                expanded.add(keyword + 's')  # Add 's'
            
            # Add common suffixes
            if not keyword.endswith('ing'):
                # Try to add 'ing' form
                if keyword.endswith('e'):
                    expanded.add(keyword[:-1] + 'ing')
                else:
                    expanded.add(keyword + 'ing')
        
        return list(expanded)
    
    def _extract_text_blocks(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract text blocks with their HTML tag information."""
        blocks = []
        
        # Priority tags for content (ordered by importance)
        content_tags = ['article', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'section', 'li', 'div', 'span']
        
        for tag_name in content_tags:
            for tag in soup.find_all(tag_name):
                text = tag.get_text(separator=' ', strip=True)
                
                # Skip very short or very long texts
                if 30 < len(text) < 2000:  # Minimum 30 chars, max 2000 for quality
                    # Skip navigation, menu, footer, sidebar, header content
                    parent_classes = ' '.join(tag.get('class', []))
                    parent_id = tag.get('id', '').lower()
                    
                    # Check if this is likely navigation/UI content
                    skip_patterns = ['nav', 'menu', 'footer', 'sidebar', 'ad', 'header', 'widget', 
                                   'category', 'tag-', 'related', 'popular', 'trending', 'subscribe']
                    if any(skip in parent_classes.lower() for skip in skip_patterns):
                        continue
                    if any(skip in parent_id for skip in skip_patterns):
                        continue
                    
                    # Skip if text has too many links (indicates navigation)
                    link_count = len(tag.find_all('a'))
                    word_count = len(text.split())
                    if word_count > 0 and link_count / word_count > 0.3:  # >30% links = navigation
                        continue
                    
                    blocks.append({
                        'text': text,
                        'tag': tag_name
                    })
        
        # Remove duplicates (same text from different tags)
        seen_texts = set()
        unique_blocks = []
        for block in blocks:
            if block['text'] not in seen_texts:
                seen_texts.add(block['text'])
                unique_blocks.append(block)
        
        return unique_blocks
    
    def _calculate_relevance(self, text: str, keywords: List[str]) -> float:
        """
        Calculate relevance score of text to keywords.
        
        Returns a score between 0 and 1.
        """
        text_lower = text.lower()
        text_words = set(re.findall(r'\b\w+\b', text_lower))
        
        # Count keyword matches with different weights
        matches = 0
        phrase_matches = 0
        word_matches = 0
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # Check for exact phrase match (highest weight)
            if keyword_lower in text_lower:
                phrase_matches += 1
                matches += 3.0  # Phrase match gets highest weight
            else:
                # Check for individual word matches
                keyword_words = set(re.findall(r'\b\w+\b', keyword_lower))
                matched_words = len(keyword_words.intersection(text_words))
                if matched_words > 0:
                    word_matches += matched_words
                    matches += matched_words * 0.5  # Word match gets lower weight
        
        # Bonus for multiple different keyword matches
        if phrase_matches > 1:
            matches += phrase_matches * 0.5
        
        # Normalize score based on text length (longer text = lower per-word score)
        text_length_factor = min(len(text_words) / 100, 1.0)  # Penalize very long texts slightly
        
        # Normalize to 0-1 range
        if len(keywords) == 0:
            return 0.0
        
        score = matches / (len(keywords) * 3.5)  # Adjusted normalization
        score = score * (1.2 - text_length_factor * 0.2)  # Slight adjustment for length
        
        return min(score, 1.0)
    
    def _find_matched_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Find which keywords are present in the text."""
        text_lower = text.lower()
        matched = []
        
        for keyword in keywords:
            if keyword in text_lower:
                matched.append(keyword)
        
        return matched
    
    def _extract_context(
        self,
        text: str,
        keywords: List[str],
        context_sentences: int
    ) -> str:
        """Extract context around keyword matches."""
        sentences = self._split_into_sentences(text)
        
        # Find sentences with keywords
        relevant_indices = set()
        for i, sentence in enumerate(sentences):
            sentence_lower = sentence.lower()
            for keyword in keywords:
                if keyword in sentence_lower:
                    # Add this sentence and surrounding context
                    start = max(0, i - context_sentences)
                    end = min(len(sentences), i + context_sentences + 1)
                    relevant_indices.update(range(start, end))
        
        # Build context string
        relevant_sentences = [sentences[i] for i in sorted(relevant_indices)]
        return ' '.join(relevant_sentences)
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _generate_summary(
        self,
        matched_sections: List[Dict[str, Any]],
        keywords: List[str]
    ) -> str:
        """Generate a summary from matched sections."""
        if not matched_sections:
            return "No relevant content found for the specified keywords."
        
        # Take the most relevant sections (top 5 for better summary)
        top_sections = matched_sections[:5]
        
        summary_parts = []
        for i, section in enumerate(top_sections, 1):
            context = section.get('context', section['text'])
            matched_kw = section.get('matched_keywords', [])
            
            # Limit context length but keep it meaningful
            if len(context) > 400:
                # Try to break at sentence boundary
                truncated = context[:397]
                last_period = truncated.rfind('.')
                if last_period > 200:  # Only break at period if it's not too early
                    context = truncated[:last_period + 1]
                else:
                    context = truncated + "..."
            
            # Add section with keyword tags
            if matched_kw:
                kw_str = ', '.join(matched_kw[:3])  # Show top 3 matched keywords
                summary_parts.append(f"[{kw_str}] {context}")
            else:
                summary_parts.append(context)
        
        return "\n\n".join(summary_parts)
    
    def calculate_content_quality(self, text: str, matched_keywords: List[str], relevance_score: float) -> Dict[str, Any]:
        """
        Calculate quality metrics for extracted content.
        
        Args:
            text: Content text
            matched_keywords: Keywords found in text
            relevance_score: Relevance score
            
        Returns:
            Dictionary with quality metrics
        """
        # Word and sentence analysis
        words = text.split()
        word_count = len(words)
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        # Calculate metrics
        avg_word_length = sum(len(w) for w in words) / max(word_count, 1)
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        # Quality indicators
        has_numbers = bool(re.search(r'\d+', text))
        has_proper_nouns = bool(re.search(r'\b[A-Z][a-z]+\b', text))
        has_dates = bool(re.search(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', text))
        
        # Complexity score (0-1)
        complexity = min((avg_word_length - 3) / 7, 1.0)  # Normalize assuming 3-10 char words
        readability = min(avg_sentence_length / 30, 1.0)  # Normalize assuming 0-30 words/sentence
        
        # Information density (keywords per 100 words)
        keyword_density = (len(matched_keywords) / max(word_count, 1)) * 100
        
        # Calculate overall quality score
        quality_score = (
            relevance_score * 0.4 +  # Relevance most important
            (complexity * 0.2) +      # Content complexity
            (has_numbers * 0.15) +    # Factual content
            (has_proper_nouns * 0.15) +  # Specific entities
            (min(keyword_density / 5, 1.0) * 0.1)  # Keyword density (capped at 5%)
        )
        
        # Quality level
        if quality_score >= 0.7:
            quality_level = "high"
        elif quality_score >= 0.4:
            quality_level = "medium"
        else:
            quality_level = "low"
        
        return {
            "quality_score": round(quality_score, 3),
            "quality_level": quality_level,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_word_length": round(avg_word_length, 2),
            "avg_sentence_length": round(avg_sentence_length, 2),
            "keyword_density": round(keyword_density, 2),
            "has_factual_content": has_numbers or has_dates,
            "has_entities": has_proper_nouns,
            "complexity": round(complexity, 2),
            "readability": round(readability, 2)
        }


class LLMKeywordExtractor:
    """Use LLM for keyword-focused extraction."""
    
    def __init__(self, llm_client, provider: str, model: str):
        """
        Initialize LLM keyword extractor.
        
        Args:
            llm_client: Initialized LLM client (LiteLLM)
            provider: LLM provider name ("litellm")
            model: Model name to use
        """
        self.client = llm_client
        self.provider = provider
        self.model = model
    
    def extract_with_keywords(
        self,
        text: str,
        keywords: List[str],
        max_tokens: int = 1500
    ) -> Dict[str, Any]:
        """
        Use LLM to extract information focused on specific keywords with quality scoring.
        
        Args:
            text: Text content to analyze
            keywords: Keywords to focus extraction on
            max_tokens: Maximum tokens for response
            
        Returns:
            Dictionary with keyword-focused extraction results including quality metrics
        """
        if not self.client or not keywords:
            return {
                "extracted_info": {},
                "summary": "",
                "keywords_found": [],
                "quality_score": 0.0,
                "confidence": 0.0
            }
        
        # Truncate text to reasonable size (larger for better context)
        text_chunk = text[:5000]
        
        # Use improved prompt from config
        from config import LLM_KEYWORD_EXTRACTION_PROMPT
        
        try:
            prompt = LLM_KEYWORD_EXTRACTION_PROMPT.format(
                keywords=", ".join(keywords),
                text=text_chunk
            )
            
            # Query LLM
            response_text = self._query_llm(prompt)
            
            if not response_text:
                return self._fallback_response()
            
            # Parse response
            result = self._parse_llm_keyword_response(response_text, keywords)
            return result
            
        except Exception as e:
            logger.error(f"LLM keyword extraction failed: {e}")
            return self._fallback_response()
    
    def _query_llm(self, prompt: str) -> str:
        """Query the LLM client."""
        try:
            if self.provider == "litellm":
                import requests
                headers = {
                    "accept": "application/json",
                    "Authorization": self.client['api_key'],
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "stream": False,
                    "use_job": self.client.get('use_job', True)
                }
                response = requests.post(
                    f"{self.client['base_url']}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data['choices'][0]['message']['content']
                else:
                    logger.error(f"LLM request failed: {response.status_code}")
                    return ""
            else:
                logger.error(f"Unsupported provider: {self.provider}")
                return ""
        except Exception as e:
            logger.error(f"LLM query error: {e}")
            return ""
    
    def _parse_llm_keyword_response(self, response: str, keywords: List[str]) -> Dict[str, Any]:
        """Parse LLM response for keyword extraction."""
        import json
        
        try:
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                data = json.loads(json_str)
                
                return {
                    "extracted_info": data.get("key_points", []),
                    "summary": data.get("summary", ""),
                    "entities": data.get("entities", []),
                    "keywords_found": keywords,
                    "quality_score": data.get("relevance_score", 0.7),
                    "confidence": data.get("relevance_score", 0.7),
                    "content_quality": data.get("content_quality", "medium")
                }
            else:
                return self._fallback_response()
                
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM JSON response")
            return self._fallback_response()
    
    def _fallback_response(self) -> Dict[str, Any]:
        """Return fallback response when LLM fails."""
        return {
            "extracted_info": {},
            "summary": "LLM extraction unavailable",
            "keywords_found": [],
            "quality_score": 0.0,
            "confidence": 0.0,
            "content_quality": "low"
        }


class HybridKeywordExtractor:
    """Combine rule-based and LLM keyword extraction for best results."""
    
    def __init__(self, rule_extractor: KeywordExtractor, llm_extractor: Optional[LLMKeywordExtractor] = None):
        """
        Initialize hybrid keyword extractor.
        
        Args:
            rule_extractor: Rule-based keyword extractor
            llm_extractor: Optional LLM keyword extractor
        """
        self.rule_extractor = rule_extractor
        self.llm_extractor = llm_extractor
    
    def extract(
        self,
        soup: BeautifulSoup,
        text: str,
        keywords: List[str],
        use_llm: bool = True
    ) -> Dict[str, Any]:
        """
        Extract using both methods and merge results with quality scoring.
        
        Args:
            soup: BeautifulSoup object
            text: Plain text content
            keywords: Keywords to focus on
            use_llm: Whether to use LLM enhancement
            
        Returns:
            Combined extraction results with quality metrics
        """
        # Get rule-based extraction
        rule_result = self.rule_extractor.extract_by_keywords(
            soup, keywords, context_sentences=2
        )
        
        # Get LLM extraction if available and requested
        llm_result = None
        if use_llm and self.llm_extractor:
            llm_result = self.llm_extractor.extract_with_keywords(text, keywords)
        
        # Merge results
        merged = self._merge_results(rule_result, llm_result, keywords)
        
        return merged
    
    def _merge_results(
        self,
        rule_result: Dict[str, Any],
        llm_result: Optional[Dict[str, Any]],
        keywords: List[str]
    ) -> Dict[str, Any]:
        """
        Merge rule-based and LLM results with quality assessment.
        
        Args:
            rule_result: Results from rule-based extraction
            llm_result: Results from LLM extraction (optional)
            keywords: Original keywords
            
        Returns:
            Merged results with quality metrics
        """
        # Start with rule-based results
        merged = {
            "keywords_used": keywords,
            "matched_sections": rule_result.get("matched_sections", []),
            "summary": rule_result.get("summary", ""),
            "relevance_score": rule_result.get("relevance_score", 0.0),
            "total_matches": rule_result.get("total_matches", 0),
            "extraction_method": "rule-based"
        }
        
        # Enhance with LLM if available
        if llm_result and llm_result.get("quality_score", 0) > 0:
            merged["llm_summary"] = llm_result.get("summary", "")
            merged["llm_entities"] = llm_result.get("entities", [])
            merged["llm_insights"] = llm_result.get("extracted_info", {})
            merged["extraction_method"] = "hybrid"
            
            # Calculate combined quality score
            rule_score = rule_result.get("relevance_score", 0.0)
            llm_score = llm_result.get("quality_score", 0.0)
            merged["quality_score"] = (rule_score * 0.4 + llm_score * 0.6)
            merged["llm_confidence"] = llm_result.get("confidence", 0.0)
            merged["content_quality"] = llm_result.get("content_quality", "medium")
        else:
            merged["quality_score"] = rule_result.get("relevance_score", 0.0)
            merged["content_quality"] = self._assess_content_quality(
                rule_result.get("total_matches", 0),
                rule_result.get("relevance_score", 0.0)
            )
        
        return merged
    
    def _assess_content_quality(self, matches: int, relevance: float) -> str:
        """Assess content quality based on matches and relevance."""
        if matches >= 5 and relevance >= 0.7:
            return "high"
        elif matches >= 3 and relevance >= 0.4:
            return "medium"
        else:
            return "low"
        
        try:
            if self.provider == "litellm":
                response = self._query_litellm(prompt)
            else:
                return {"error": f"Unsupported provider: {self.provider}. Only 'litellm' is supported."}
            
            # Parse JSON response
            import json
            
            # Try to find JSON in response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                # Fallback to raw response
                return {
                    "extracted_info": {},
                    "summary": response[:500],
                    "keywords_found": keywords
                }
                
        except Exception as e:
            logger.error(f"LLM keyword extraction failed: {e}")
            return {
                "error": str(e),
                "extracted_info": {},
                "summary": "",
                "keywords_found": []
            }
