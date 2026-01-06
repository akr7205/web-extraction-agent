"""Semantic query processor for natural language queries."""
import logging
import json
import requests
import re
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class SemanticQueryProcessor:
    """Process natural language queries and extract semantic search parameters."""
    
    def __init__(self, api_key: str, model: str, base_url: str, temperature: float = 0.3):
        """
        Initialize semantic query processor.
        
        Args:
            api_key: API key for LLM provider
            model: Model name
            base_url: Base URL for API
            temperature: Temperature for generation (lower for more focused)
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process natural language query into structured search parameters.
        
        Args:
            query: Natural language query from user
            
        Returns:
            Dictionary with keywords, intent, focus_areas, and search_strategy
        """
        # Check if it's already keywords (comma-separated short terms)
        is_keywords = self._is_keyword_list(query)
        
        if is_keywords:
            # Simple keyword list
            keywords = [k.strip() for k in query.split(',') if k.strip()]
            return {
                "query_type": "keywords",
                "original_query": query,
                "keywords": keywords,
                "intent": "keyword_search",
                "focus_areas": keywords,
                "search_strategy": "keyword_matching",
                "semantic_expansion": True
            }
        
        # Natural language query - use LLM to extract semantic meaning
        try:
            semantic_params = self._extract_semantic_parameters(query)
            return {
                "query_type": "natural_language",
                "original_query": query,
                **semantic_params
            }
        except Exception as e:
            logger.error(f"Failed to process semantic query: {e}")
            # Fallback to basic keyword extraction
            return self._fallback_extraction(query)
    
    def _is_keyword_list(self, query: str) -> bool:
        """
        Determine if query is a simple keyword list.
        
        Returns:
            True if it's a comma-separated keyword list
        """
        # Check for comma-separated short terms
        if ',' in query:
            parts = [p.strip() for p in query.split(',')]
            # Keywords are typically 1-3 words each
            if all(len(p.split()) <= 3 for p in parts):
                return True
        
        # Single short term
        if len(query.split()) <= 3 and not any(word in query.lower() for word in 
            ['give', 'show', 'find', 'get', 'search', 'tell', 'what', 'how', 'why', 'where', 'when', 'who']):
            return True
        
        return False
    
    def _extract_semantic_parameters(self, query: str) -> Dict[str, Any]:
        """
        Use LLM to extract semantic search parameters from natural language query.
        
        Args:
            query: Natural language query
            
        Returns:
            Dictionary with keywords, intent, focus_areas, search_strategy
        """
        prompt = f"""You are a semantic query analyzer. Analyze the user's query and extract structured search parameters.

User Query: "{query}"

Extract:
1. **keywords**: List of 3-8 key terms/concepts to search for (most important)
2. **intent**: What the user wants (e.g., "comprehensive_info", "specific_facts", "overview", "comparison", "detailed_analysis")
3. **focus_areas**: Specific aspects to focus on (e.g., "technical details", "pricing", "history", "features")
4. **search_strategy**: How to search ("broad" for general info, "targeted" for specific details, "comprehensive" for everything)
5. **quality_requirements**: What makes content relevant ("high_detail", "factual_data", "expert_analysis")

Examples:
- Query: "Give me all the details for this" → intent: comprehensive_info, keywords: [main topics from context], search_strategy: comprehensive
- Query: "AI technology trends" → intent: overview, keywords: [AI, technology, trends, innovation], search_strategy: broad
- Query: "pricing and features" → intent: specific_facts, keywords: [pricing, cost, features, capabilities], search_strategy: targeted

Return ONLY valid JSON in this exact format:
{{
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "intent": "comprehensive_info",
  "focus_areas": ["area1", "area2"],
  "search_strategy": "comprehensive",
  "quality_requirements": "high_detail",
  "semantic_expansion": true
}}

JSON Response:"""
        
        try:
            response_text = self._query_llm(prompt)
            
            # Parse JSON response
            # Remove markdown code blocks if present
            response_text = re.sub(r'```json\s*', '', response_text)
            response_text = re.sub(r'```\s*', '', response_text)
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            
            # Validate required fields
            if not result.get('keywords') or not isinstance(result['keywords'], list):
                raise ValueError("Invalid keywords in LLM response")
            
            # Ensure defaults
            result.setdefault('intent', 'comprehensive_info')
            result.setdefault('search_strategy', 'comprehensive')
            result.setdefault('semantic_expansion', True)
            result.setdefault('focus_areas', result['keywords'][:3])
            result.setdefault('quality_requirements', 'high_detail')
            
            logger.info(f"Extracted semantic parameters: {result['intent']}, keywords: {result['keywords']}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            raise
    
    def _query_llm(self, prompt: str) -> str:
        """
        Query LLM API.
        
        Args:
            prompt: Prompt text
            
        Returns:
            Response text
        """
        headers = {
            "accept": "application/json",
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "stream": False,
            "use_job": False  # Use sync for query processing
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            return content.strip()
            
        except Exception as e:
            logger.error(f"LLM query failed: {e}")
            raise
    
    def _fallback_extraction(self, query: str) -> Dict[str, Any]:
        """
        Fallback extraction using simple NLP when LLM fails.
        
        Args:
            query: Natural language query
            
        Returns:
            Dictionary with basic search parameters
        """
        # Remove common question words and extract nouns/keywords
        stop_words = {'give', 'show', 'find', 'get', 'search', 'tell', 'me', 'the', 'a', 'an', 
                     'for', 'about', 'all', 'this', 'that', 'these', 'those', 'what', 'how', 'why'}
        
        words = query.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Detect intent from query patterns
        query_lower = query.lower()
        if any(phrase in query_lower for phrase in ['all details', 'everything', 'comprehensive', 'complete']):
            intent = "comprehensive_info"
            search_strategy = "comprehensive"
        elif any(phrase in query_lower for phrase in ['overview', 'summary', 'about']):
            intent = "overview"
            search_strategy = "broad"
        else:
            intent = "specific_facts"
            search_strategy = "targeted"
        
        return {
            "keywords": keywords[:8] if keywords else ["information", "details"],
            "intent": intent,
            "focus_areas": keywords[:3] if keywords else ["main content"],
            "search_strategy": search_strategy,
            "quality_requirements": "high_detail",
            "semantic_expansion": True
        }
