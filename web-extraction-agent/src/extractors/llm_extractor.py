"""LLM integration module for enhanced entity extraction using LiteLLM."""
import logging
import json
import requests
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class LLMEntityExtractor:
    """Extract entities using LiteLLM for better accuracy and semantic understanding."""
    
    def __init__(self, provider: str = "litellm", api_key: str = "", model: str = "", base_url: str = "", temperature: float = 0.7, use_job: bool = False):
        """
        Initialize LLM entity extractor.
        
        Args:
            provider: LLM provider ("litellm")
            api_key: API key (required for litellm)
            model: Model name to use
            base_url: Base URL for provider
            temperature: Temperature for generation
            use_job: Whether to use job mode
        """
        self.provider = provider.lower()
        self.api_key = api_key
        self.model = model
        self.base_url = base_url or "https://litellm-api.predev.praveg.ai/v1"
        self.temperature = temperature
        self.use_job = use_job
        self.client = None
        
        if self.provider == "litellm":
            self._init_litellm()
        else:
            logger.error(f"Unsupported LLM provider: {provider}. Only 'litellm' is supported.")
    
    def _get_auth_header(self) -> str:
        """Return Authorization header value with Bearer prefix when missing."""
        if not self.api_key:
            return ""
        return self.api_key if self.api_key.lower().startswith("bearer ") else f"Bearer {self.api_key}"

    def _init_litellm(self):
        """Initialize LiteLLM client."""
        if not self.api_key:
            logger.error("LiteLLM API key is required. Set LITELLM_API_KEY in .env file.")
            return
        
        # Test connection
        try:
            headers = {
                "accept": "application/json",
                "Authorization": self._get_auth_header(),
                "Content-Type": "application/json"
            }
            test_payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Hi"}],
                "temperature": self.temperature,
                "stream": False,
                "use_job": self.use_job
            }
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=test_payload,
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                self.client = True  # Mark as initialized
                logger.info(f"Initialized LiteLLM client at {self.base_url} with model: {self.model}")
            else:
                logger.error(f"LiteLLM connection test failed: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Failed to initialize LiteLLM client: {e}")
    
    def extract_entities(self, text: str, max_tokens: int = 1000) -> List[Dict[str, Any]]:
        """
        Extract entities from text using LLM.
        
        Args:
            text: Text to extract entities from
            max_tokens: Maximum tokens for response
            
        Returns:
            List of extracted entities
        """
        if not self.client:
            logger.debug("LLM client not available, returning empty list")
            return []
        
        if len(text) < 50:
            logger.debug("Text too short for LLM extraction")
            return []
        
        # Truncate text to reasonable size for LLM (avoid token limits)
        text_chunk = text[:3000]
        
        try:
            from config import LLM_EXTRACTION_PROMPT
            
            prompt = LLM_EXTRACTION_PROMPT.format(text=text_chunk)
            
            if self.provider == "litellm":
                response_text = self._query_litellm(prompt)
            else:
                logger.warning(f"Unsupported provider: {self.provider}")
                return []
            
            # Parse response
            entities = self._parse_llm_response(response_text)
            
            logger.debug(f"LLM extracted {len(entities)} entities")
            return entities
        
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return []
    
    def _query_litellm(self, prompt: str) -> str:
        """Query LiteLLM API."""
        try:
            headers = {
                "accept": "application/json",
                "Authorization": self._get_auth_header(),
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
                "stream": False,
                "use_job": self.use_job
            }
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")
            else:
                logger.error(f"LiteLLM API error: {response.status_code} - {response.text}")
                return ""
        except Exception as e:
            logger.error(f"LiteLLM query failed: {e}")
            return ""
    
    def _parse_llm_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse LLM response into entity list.
        
        Args:
            response: LLM response text
            
        Returns:
            List of entities
        """
        try:
            # Try to find JSON in response
            start_idx = response.find('[')
            end_idx = response.rfind(']') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.warning("No JSON array found in LLM response")
                return []
            
            json_str = response[start_idx:end_idx]
            entities = json.loads(json_str)
            
            # Validate and normalize entities
            normalized = []
            for entity in entities:
                if self._is_valid_entity(entity):
                    normalized.append({
                        "name": str(entity.get("name", "")),
                        "type": str(entity.get("type", "")).upper(),
                        "value": str(entity.get("value", "")),
                        "confidence": float(entity.get("confidence", 0.8))
                    })
            
            return normalized
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return []
    
    def _is_valid_entity(self, entity: Dict[str, Any]) -> bool:
        """
        Check if entity is valid.
        
        Args:
            entity: Entity to validate
            
        Returns:
            True if valid, False otherwise
        """
        required = ["name", "type", "value"]
        
        # Check required fields
        if not all(field in entity for field in required):
            return False
        
        # Check types are valid
        valid_types = ["COMPANY", "AMOUNT", "DATE", "PERSON"]
        if entity.get("type", "").upper() not in valid_types:
            return False
        
        # Check fields are non-empty
        if not entity.get("name") or not entity.get("value"):
            return False
        
        return True
    
    def extract_with_semantic_query(
        self, 
        text: str, 
        query: str,
        search_strategy: str = "comprehensive",
        quality_requirements: str = "high_detail"
    ) -> Dict[str, Any]:
        """
        Extract content based on semantic query understanding.
        
        Args:
            text: Text to extract from
            query: Natural language query or keywords
            search_strategy: How to search ("broad", "targeted", "comprehensive")
            quality_requirements: Quality level ("high_detail", "factual_data", "expert_analysis")
            
        Returns:
            Dictionary with semantic extraction results
        """
        if not self.client:
            logger.debug("LLM client not available for semantic extraction")
            return {
                "summary": "",
                "key_points": [],
                "entities": [],
                "relevance_score": 0.0,
                "content_quality": "low"
            }
        
        if len(text) < 50:
            logger.debug("Text too short for semantic extraction")
            return {
                "summary": "",
                "key_points": [],
                "entities": [],
                "relevance_score": 0.0,
                "content_quality": "low"
            }
        
        # Truncate text to manageable size
        text_chunk = text[:5000]
        
        try:
            from config import LLM_KEYWORD_EXTRACTION_PROMPT
            
            # Build context-aware prompt based on search strategy
            strategy_guidance = {
                "comprehensive": "Extract ALL relevant information comprehensively. Include every detail, fact, and context.",
                "broad": "Extract main points and key information. Focus on overview and general understanding.",
                "targeted": "Extract only the most specific and directly relevant details. Be precise and focused."
            }
            
            quality_guidance = {
                "high_detail": "Provide detailed, in-depth information with full context.",
                "factual_data": "Focus on concrete facts, numbers, dates, and verifiable information.",
                "expert_analysis": "Include analytical insights and expert-level interpretation."
            }
            
            prompt = f"""{LLM_KEYWORD_EXTRACTION_PROMPT.format(keywords=query, text=text_chunk)}

Additional Instructions:
- Search Strategy: {strategy_guidance.get(search_strategy, strategy_guidance['comprehensive'])}
- Quality Requirement: {quality_guidance.get(quality_requirements, quality_guidance['high_detail'])}
- Focus on extracting meaningful, high-quality content only
- Assign high relevance scores (0.8+) only to truly relevant content
- Filter out generic or low-value information

JSON Response:"""
            
            response_text = self._query_litellm(prompt)
            
            # Parse JSON response
            import re
            response_text = re.sub(r'```json\s*', '', response_text)
            response_text = re.sub(r'```\s*', '', response_text)
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            
            # Ensure all required fields
            result.setdefault('summary', '')
            result.setdefault('key_points', [])
            result.setdefault('entities', [])
            result.setdefault('relevance_score', 0.0)
            result.setdefault('content_quality', 'medium')
            result.setdefault('keywords_found', [])
            
            logger.debug(f"Semantic extraction: relevance={result['relevance_score']}, quality={result['content_quality']}")
            return result
            
        except Exception as e:
            logger.error(f"Semantic extraction failed: {e}")
            return {
                "summary": "",
                "key_points": [],
                "entities": [],
                "relevance_score": 0.0,
                "content_quality": "low"
            }
    
    
    def enhance_title(self, content: str, original_title: str = "") -> str:
        """
        Enhance or generate title using LLM.
        
        Args:
            content: Page content
            original_title: Original extracted title
            
        Returns:
            Enhanced title
        """
        if not self.client or len(content) < 100:
            return original_title
        
        try:
            prompt = f"""Given the following content, provide a concise, descriptive title (max 100 chars).
            
Original title: {original_title}

Content: {content[:1000]}

Provide only the title, nothing else."""
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=100,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            new_title = message.content[0].text.strip() if message.content else original_title
            return new_title if len(new_title) < 200 else original_title
        
        except Exception as e:
            logger.error(f"Title enhancement failed: {e}")
            return original_title
    
    def classify_content(self, text: str) -> str:
        """
        Classify content type using LLM.
        
        Args:
            text: Text to classify
            
        Returns:
            Classification (news, financial, product, other)
        """
        if not self.client or len(text) < 50:
            return "other"
        
        try:
            prompt = f"""Classify this content into one category:
- news: News article or blog post
- financial: Financial report or filing
- product: Product description or e-commerce
- other: Other content type

Content: {text[:500]}

Respond with ONLY the category name."""
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            classification = message.content[0].text.strip().lower() if message.content else "other"
            valid_types = ["news", "financial", "product", "other"]
            
            return classification if classification in valid_types else "other"
        
        except Exception as e:
            logger.error(f"Content classification failed: {e}")
            return "other"


class HybridEntityExtractor:
    """Hybrid extractor combining rule-based and LLM approaches."""
    
    def __init__(self, rule_extractor, llm_extractor: Optional[LLMEntityExtractor] = None):
        """
        Initialize hybrid extractor.
        
        Args:
            rule_extractor: Rule-based entity extractor
            llm_extractor: Optional LLM entity extractor
        """
        self.rule_extractor = rule_extractor
        self.llm_extractor = llm_extractor
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract entities using both methods and merge results.
        
        Args:
            text: Text to extract entities from
            
        Returns:
            Merged and deduplicated entity list
        """
        # Get rule-based entities
        rule_entities = self.rule_extractor.extract_entities(text)
        
        # Get LLM entities if available
        llm_entities = []
        if self.llm_extractor:
            llm_entities = self.llm_extractor.extract_entities(text)
        
        # Merge entities
        merged = self._merge_entities(rule_entities, llm_entities)
        
        # Sort by confidence and limit
        merged.sort(key=lambda e: e.get('confidence', 0), reverse=True)
        return merged[:20]
    
    def _merge_entities(
        self,
        rule_entities: List[Dict[str, Any]],
        llm_entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Merge entities from both sources.
        
        Args:
            rule_entities: Entities from rule-based extractor
            llm_entities: Entities from LLM extractor
            
        Returns:
            Merged entity list
        """
        # Start with rule-based entities
        merged = {}
        
        for entity in rule_entities:
            key = (entity['type'], entity['name'].lower())
            merged[key] = entity
        
        # Add or enhance with LLM entities
        for entity in llm_entities:
            key = (entity['type'], entity['name'].lower())
            
            if key in merged:
                # Enhance existing entity with LLM confidence
                if entity.get('confidence', 0) > merged[key].get('confidence', 0):
                    # Use LLM confidence if higher, but keep both values
                    merged[key]['llm_confidence'] = entity['confidence']
                    merged[key]['confidence'] = min(
                        0.95,
                        max(merged[key]['confidence'], entity['confidence'])
                    )
            else:
                # Add new LLM-discovered entity
                merged[key] = entity
        
        return list(merged.values())
