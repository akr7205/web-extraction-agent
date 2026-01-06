"""Core web extraction module."""
import json
import re
import time
import logging
from collections import Counter
from typing import Optional, Dict, Any, List
from datetime import datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, Timeout, ConnectionError

from config import (
    AGENT_ID, MODEL_USED, REQUEST_TIMEOUT, MAX_CONTENT_SIZE, USER_AGENT,
    EXTRACTION_PROFILES, COMMON_REMOVE_SELECTORS, MIN_CONTENT_LENGTH,
    MAX_PROCESSING_TIME_MS, DEBUG, LOG_LEVEL, USE_LLM,
    LITELLM_API_KEY, LITELLM_BASE_URL, LITELLM_MODEL,
    LITELLM_TEMPERATURE, LITELLM_USE_JOB, LLM_SUMMARY_PROMPT
)
from extractors.entity_extractor import EntityExtractor
from extractors.llm_extractor import LLMEntityExtractor, HybridEntityExtractor
from extractors.keyword_extractor import KeywordExtractor, LLMKeywordExtractor, HybridKeywordExtractor
from crawlers.web_crawler import WebCrawler

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WebExtractionAgent:
    """Agent for extracting structured data from web pages."""
    
    def __init__(self, use_llm: bool = True):
        """
        Initialize Web Extraction Agent.
        
        Args:
            use_llm: Whether to use LLM for enhanced extraction
        """
        self.rule_extractor = EntityExtractor()
        self.keyword_extractor = KeywordExtractor()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
        
        # Initialize LLM extractor if enabled
        self.llm_extractor = None
        self.hybrid_extractor = None
        self.llm_keyword_extractor = None
        self.llm_client_config = None
        
        if use_llm and USE_LLM:
            if not LITELLM_API_KEY:
                logger.warning("LiteLLM API key is missing. Falling back to rule-based extraction.")
            else:
                self.llm_client_config = self._build_llm_client_config()
                try:
                    self.llm_extractor = LLMEntityExtractor(
                        provider="litellm",
                        api_key=LITELLM_API_KEY,
                        model=LITELLM_MODEL,
                        base_url=LITELLM_BASE_URL,
                        temperature=LITELLM_TEMPERATURE,
                        use_job=LITELLM_USE_JOB
                    )
                    logger.info(f"LLM entity extraction enabled with LiteLLM ({LITELLM_MODEL})")
                except Exception as e:
                    logger.warning(f"Failed to initialize LiteLLM extractor: {e}. Using rule-based only.")
                try:
                    self.llm_keyword_extractor = LLMKeywordExtractor(
                        llm_client={
                            "api_key": self.llm_client_config["auth_header"],
                            "base_url": self.llm_client_config["base_url"],
                            "use_job": self.llm_client_config["use_job"]
                        },
                        provider="litellm",
                        model=LITELLM_MODEL
                    )
                    logger.info("LLM keyword extraction enabled with LiteLLM")
                except Exception as e:
                    logger.warning(f"Failed to initialize LiteLLM keyword extractor: {e}. Using rule-based keywords only.")
        else:
            logger.debug("LLM extraction disabled. Using rule-based extraction only.")

        self.hybrid_extractor = HybridEntityExtractor(self.rule_extractor, self.llm_extractor)
        self.hybrid_keyword_extractor = HybridKeywordExtractor(self.keyword_extractor, self.llm_keyword_extractor)
    
    def extract(
        self,
        url: str,
        raw_html: Optional[str] = None,
        extraction_profile: str = "news"
    ) -> Dict[str, Any]:
        """
        Extract structured data from a web page.
        
        Args:
            url: URL to extract from
            raw_html: Optional pre-fetched HTML content
            extraction_profile: Profile to use (news, filing, product)
            
        Returns:
            Dictionary with title, entities, content, metadata, and trace
        """
        start_time = time.time()
        errors = []
        
        try:
            # Validate input
            if not url:
                raise ValueError("URL is required")
            
            if extraction_profile not in EXTRACTION_PROFILES:
                errors.append(f"Unknown profile '{extraction_profile}', defaulting to 'news'")
                extraction_profile = "news"
            
            # Fetch HTML if not provided
            if raw_html:
                html_content = raw_html
                logger.debug("Using provided HTML content")
            else:
                html_content = self._fetch_html(url)
            
            # Parse and clean HTML
            soup = self._parse_and_clean(html_content, extraction_profile)
            
            # Extract components
            title = self._extract_title(soup, extraction_profile)
            content = self._extract_content(soup, extraction_profile)
            entities = self._extract_entities(content)
            structured_sections = self._extract_structured_sections(soup)
            auto_keywords = self._auto_select_keywords(content)
            keyword_snapshot = self._run_keyword_extraction(
                soup,
                content,
                auto_keywords,
                use_llm=False,
                min_relevance_score=0.15
            ) if auto_keywords else {}
            quality_metrics = self._calculate_extraction_quality(
                keyword_snapshot,
                len(content),
                len(entities)
            )
            semantic_summary = self._generate_semantic_summary(
                title,
                content,
                structured_sections,
                entities
            )
            
            # Check for minimum content
            if len(content) < MIN_CONTENT_LENGTH:
                errors.append(f"Content too short: {len(content)} chars (min: {MIN_CONTENT_LENGTH})")
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Build response
            return {
                "title": title,
                "entities": entities,
                "content": content,
                "structured_content": structured_sections,
                "semantic_summary": semantic_summary,
                "quality_metrics": quality_metrics,
                "metadata": {
                    "fetched_at": datetime.utcnow().isoformat() + "Z",
                    "source_url": url,
                    "extraction_profile": extraction_profile,
                    "auto_keywords": auto_keywords
                },
                "trace": {
                    "agent_id": AGENT_ID,
                    "model_used": MODEL_USED,
                    "duration_ms": duration_ms,
                    "errors": errors
                }
            }
        
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            errors.append(f"Extraction failed: {str(e)}")
            logger.error(f"Extraction error for {url}: {e}")
            
            # Return partial result with error
            return {
                "title": "",
                "entities": [],
                "content": "",
                "structured_content": [],
                "semantic_summary": {},
                "quality_metrics": {
                    "overall_score": 0.0,
                    "grade": "F",
                    "relevance_score": 0.0,
                    "quality_score": 0.0,
                    "completeness_score": 0.0,
                    "content_quality": "unknown",
                    "metrics": {
                        "content_length": 0,
                        "keyword_matches": 0,
                        "entities_found": 0
                    },
                    "assessment": "Quality assessment unavailable."
                },
                "metadata": {
                    "fetched_at": datetime.utcnow().isoformat() + "Z",
                    "source_url": url,
                    "extraction_profile": extraction_profile,
                    "auto_keywords": []
                },
                "trace": {
                    "agent_id": AGENT_ID,
                    "model_used": MODEL_USED,
                    "duration_ms": duration_ms,
                    "errors": errors
                }
            }
    
    def extract_by_keywords(
        self,
        url: str,
        keywords: List[str],
        raw_html: Optional[str] = None,
        use_llm: bool = True
    ) -> Dict[str, Any]:
        """
        Extract content from a web page focused on specific keywords with quality scoring.
        Works universally on any content type - no profile needed.
        
        Args:
            url: URL to extract from
            keywords: List of keywords to focus extraction on
            raw_html: Optional pre-fetched HTML content
            use_llm: Whether to use LLM for keyword-focused extraction
            
        Returns:
            Dictionary with keyword-focused extraction results and quality metrics
        """
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            # Validate input
            if not url:
                raise ValueError("URL is required")
            if not keywords:
                raise ValueError("Keywords are required")
            
            # Use universal profile - works for all content types
            extraction_profile = "news"
            
            # Fetch HTML if not provided
            fetch_start = time.time()
            if raw_html:
                html_content = raw_html
                logger.debug("Using provided HTML content")
                fetch_ms = 0
            else:
                html_content = self._fetch_html(url)
                fetch_ms = int((time.time() - fetch_start) * 1000)
            
            # Parse and clean HTML
            parse_start = time.time()
            soup = self._parse_and_clean(html_content, extraction_profile)
            parse_ms = int((time.time() - parse_start) * 1000)
            
            # Extract title and basic content
            title = self._extract_title(soup, extraction_profile)
            content = self._extract_content(soup, extraction_profile)
            
            # Check if we got valid content
            if not content or len(content) < 50:
                warnings.append("Extracted content is too short or empty - possible encoding issue")
                logger.warning(f"Content too short ({len(content)} chars) for {url}")
            
            # Keyword-based extraction with quality tracking
            extract_start = time.time()
            keyword_results = self._run_keyword_extraction(
                soup,
                content,
                keywords,
                use_llm=use_llm,
                min_relevance_score=0.2
            )
            
            extract_ms = int((time.time() - extract_start) * 1000)
            
            # Extract entities from keyword-relevant content
            keyword_entities = self.keyword_extractor.extract_keyword_entities(content, keywords)
            
            # Calculate extraction quality metrics
            quality_metrics = self._calculate_extraction_quality(
                keyword_results,
                len(content),
                len(keyword_entities)
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Build comprehensive response with quality scores
            result = {
                "title": title or "No title extracted",
                "keywords": keywords,
                "keyword_extraction": {
                    "matched_sections": keyword_results.get("matched_sections", []),
                    "summary": keyword_results.get("summary", ""),
                    "key_points": keyword_results.get("key_points", []),
                    "relevance_score": round(keyword_results.get("relevance_score", 0.0), 3),
                    "total_matches": keyword_results.get("total_matches", 0),
                    "quality_score": round(keyword_results.get("quality_score", 0.0), 3),
                    "content_quality": keyword_results.get("content_quality", "unknown"),
                    "extraction_method": keyword_results.get("extraction_method", "rule-based")
                },
                "keyword_entities": keyword_entities,
                "full_content": content[:2000],  # Limit to first 2000 chars for response
                "quality_metrics": quality_metrics,
                "metadata": {
                    "fetched_at": datetime.utcnow().isoformat() + "Z",
                    "source_url": url,
                    "keywords_used": keywords,
                    "content_length": len(content),
                    "title_extracted": bool(title)
                },
                "trace": {
                    "agent_id": AGENT_ID,
                    "model_used": MODEL_USED,
                    "duration_ms": duration_ms,
                    "fetch_ms": fetch_ms,
                    "parse_ms": parse_ms,
                    "extract_ms": extract_ms,
                    "llm_used": use_llm and self.llm_keyword_extractor is not None,
                    "errors": errors,
                    "warnings": warnings
                }
            }
            
            # Add LLM-specific results if available
            if keyword_results.get("llm_summary"):
                result["llm_insights"] = {
                    "summary": keyword_results.get("llm_summary", ""),
                    "entities": keyword_results.get("llm_entities", []),
                    "confidence": keyword_results.get("llm_confidence", 0.0)
                }
            
            return result
        
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            errors.append(f"Keyword extraction failed: {str(e)}")
            logger.error(f"Keyword extraction error for {url}: {e}")
            
            # Return error result with quality metrics
            return {
                "title": "",
                "keywords": keywords,
                "keyword_extraction": {
                    "matched_sections": [],
                    "summary": "",
                    "relevance_score": 0.0,
                    "total_matches": 0,
                    "key_points": []
                },
                "keyword_entities": {},
                "full_content": "",
                "metadata": {
                    "fetched_at": datetime.utcnow().isoformat() + "Z",
                    "source_url": url,
                    "keywords_used": keywords
                },
                "trace": {
                    "agent_id": AGENT_ID,
                    "model_used": MODEL_USED,
                    "duration_ms": duration_ms,
                    "llm_used": False,
                    "errors": errors
                }
            }
    
    def extract_by_semantic_query(
        self,
        url: str,
        query: str,
        use_llm: bool = True,
        raw_html: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract content using semantic query understanding (supports natural language).
        
        Args:
            url: URL to extract from
            query: Natural language query or keywords (e.g., "Give me all the details", "AI technology pricing")
            use_llm: Whether to use LLM for semantic understanding
            raw_html: Optional pre-fetched HTML
            
        Returns:
            Dictionary with semantically relevant content and quality metrics
        """
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            # Process query to extract semantic parameters
            from processors.semantic_query_processor import SemanticQueryProcessor
            from config import LITELLM_API_KEY, LITELLM_MODEL, LITELLM_BASE_URL
            
            semantic_processor = SemanticQueryProcessor(
                api_key=LITELLM_API_KEY,
                model=LITELLM_MODEL,
                base_url=LITELLM_BASE_URL
            )
            
            logger.info(f"Processing semantic query: '{query}'")
            query_params = semantic_processor.process_query(query)
            
            keywords = query_params.get('keywords', [query])
            intent = query_params.get('intent', 'comprehensive_info')
            search_strategy = query_params.get('search_strategy', 'comprehensive')
            quality_requirements = query_params.get('quality_requirements', 'high_detail')
            
            logger.info(f"Query analysis: intent={intent}, keywords={keywords}, strategy={search_strategy}")
            
            # Fetch and parse HTML
            fetch_start = time.time()
            if raw_html:
                html_content = raw_html
                fetch_ms = 0
            else:
                html_content = self._fetch_html(url)
                fetch_ms = int((time.time() - fetch_start) * 1000)
            
            parse_start = time.time()
            soup = self._parse_and_clean(html_content, "news")
            parse_ms = int((time.time() - parse_start) * 1000)
            
            # Extract title and content
            title = self._extract_title(soup, "news")
            content = self._extract_content(soup, "news")
            
            if not content or len(content) < 50:
                warnings.append("Extracted content is too short or empty")
                logger.warning(f"Content too short ({len(content)} chars) for {url}")
            
            # Semantic extraction using LLM
            extract_start = time.time()
            keyword_results = self._run_keyword_extraction(
                soup,
                content,
                keywords,
                use_llm=use_llm,
                min_relevance_score=0.15
            )
            
            if use_llm and self.llm_extractor:
                # Use LLM for semantic extraction
                llm_results = self.llm_extractor.extract_with_semantic_query(
                    text=content,
                    query=query,
                    search_strategy=search_strategy,
                    quality_requirements=quality_requirements
                )
                
                matched_keywords = llm_results.get('keywords_found', keywords)
                quality_metrics = self.keyword_extractor.calculate_content_quality(
                    content,
                    matched_keywords,
                    llm_results.get('relevance_score', keyword_results.get('relevance_score', 0.0))
                )
                
                final_results = {
                    "matched_sections": keyword_results.get("matched_sections", [])[:10],
                    "summary": llm_results.get("summary", keyword_results.get("summary", "")),
                    "key_points": llm_results.get("key_points", keyword_results.get("key_points", [])),
                    "relevance_score": llm_results.get("relevance_score", keyword_results.get("relevance_score", 0.0)),
                    "total_matches": keyword_results.get("total_matches", 0),
                    "content_quality": llm_results.get("content_quality", quality_metrics.get("quality_level", "medium")),
                    "quality_score": quality_metrics.get("quality_score", keyword_results.get("quality_score", 0.0)),
                    "extraction_method": "semantic_llm"
                }
                llm_entities = llm_results.get("entities", keyword_results.get("llm_entities", []))
            else:
                quality_metrics = self.keyword_extractor.calculate_content_quality(
                    content,
                    keywords,
                    keyword_results.get("relevance_score", 0.0)
                )
                final_results = {
                    "matched_sections": keyword_results.get("matched_sections", []),
                    "summary": keyword_results.get("summary", ""),
                    "key_points": keyword_results.get("key_points", []),
                    "relevance_score": keyword_results.get("relevance_score", 0.0),
                    "total_matches": keyword_results.get("total_matches", 0),
                    "quality_score": quality_metrics.get("quality_score", keyword_results.get("quality_score", 0.0)),
                    "content_quality": quality_metrics.get("quality_level", keyword_results.get("content_quality", "unknown")),
                    "extraction_method": keyword_results.get("extraction_method", "keyword_based")
                }
                llm_entities = keyword_results.get("llm_entities", [])
            
            extract_ms = int((time.time() - extract_start) * 1000)
            
            # Extract keyword entities
            keyword_entities = self.keyword_extractor.extract_keyword_entities(content, keywords)
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Build comprehensive response
            result = {
                "title": title or "No title extracted",
                "keywords": keywords,
                "query_analysis": {
                    "original_query": query,
                    "query_type": query_params.get("query_type", "unknown"),
                    "intent": intent,
                    "search_strategy": search_strategy,
                    "quality_requirements": quality_requirements
                },
                "keyword_extraction": {
                    "matched_sections": final_results.get("matched_sections", []),
                    "summary": final_results.get("summary", ""),
                    "key_points": final_results.get("key_points", []),
                    "relevance_score": round(final_results.get("relevance_score", 0.0), 3),
                    "total_matches": final_results.get("total_matches", 0),
                    "quality_score": round(final_results.get("quality_score", 0.0), 3),
                    "content_quality": final_results.get("content_quality", "unknown"),
                    "extraction_method": final_results.get("extraction_method", "unknown")
                },
                "keyword_entities": keyword_entities,
                "llm_entities": llm_entities,
                "full_content": content[:3000],  # First 3000 chars
                "quality_metrics": quality_metrics,
                "metadata": {
                    "fetched_at": datetime.utcnow().isoformat() + "Z",
                    "source_url": url,
                    "query_used": query,
                    "keywords_extracted": keywords,
                    "content_length": len(content),
                    "title_extracted": bool(title)
                },
                "trace": {
                    "agent_id": AGENT_ID,
                    "model_used": MODEL_USED + "+semantic-query-processor",
                    "duration_ms": duration_ms,
                    "fetch_ms": fetch_ms,
                    "parse_ms": parse_ms,
                    "extract_ms": extract_ms,
                    "llm_used": use_llm and self.llm_extractor is not None,
                    "semantic_processing": True,
                    "errors": errors,
                    "warnings": warnings
                }
            }
            
            logger.info(f"Semantic extraction completed in {duration_ms}ms - Quality: {final_results.get('content_quality')}, Relevance: {final_results.get('relevance_score'):.3f}")
            return result
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            errors.append(f"Semantic extraction failed: {str(e)}")
            logger.error(f"Semantic extraction error for {url}: {e}")
            
            # Return error result
            return {
                "title": "",
                "keywords": [query],
                "query_analysis": {"original_query": query, "error": str(e)},
                "keyword_extraction": {
                    "matched_sections": [],
                    "summary": "",
                    "relevance_score": 0.0,
                    "total_matches": 0,
                    "key_points": []
                },
                "keyword_entities": {},
                "llm_entities": [],
                "full_content": "",
                "metadata": {
                    "fetched_at": datetime.utcnow().isoformat() + "Z",
                    "source_url": url,
                    "query_used": query
                },
                "trace": {
                    "agent_id": AGENT_ID,
                    "model_used": MODEL_USED,
                    "duration_ms": duration_ms,
                    "llm_used": False,
                    "semantic_processing": False,
                    "errors": errors
                }
            }
    
    def _fetch_html(self, url: str) -> str:
        """
        Safely fetch HTML from URL with proper encoding handling.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content as string
            
        Raises:
            RequestException: If fetch fails
        """
        try:
            logger.debug(f"Fetching URL: {url}")
            
            # Validate URL
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"Invalid URL: {url}")
            
            response = self.session.get(
                url,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True,
                verify=True
            )
            response.raise_for_status()
            
            # Check content size
            if len(response.content) > MAX_CONTENT_SIZE:
                logger.warning(f"Content exceeds max size: {len(response.content)} bytes")
            
            # Check if content is actually HTML
            content_type = response.headers.get('Content-Type', '').lower()
            if 'html' not in content_type and content_type:
                logger.warning(f"Content-Type is not HTML: {content_type}")
            
            # Get encoding from response
            encoding = response.encoding or 'utf-8'
            
            # Try to decode with proper encoding
            try:
                # Use response.text which handles encoding automatically
                html = response.text
                
                # Validate that we got actual text (not binary garbage)
                # Check if content contains common HTML markers
                if html and ('<html' in html.lower() or '<!doctype' in html.lower() or '<body' in html.lower()):
                    return html
                else:
                    # Try alternative decoding methods
                    logger.warning("Response text doesn't look like HTML, trying alternative decoding")
                    
                    # Try different encodings
                    for enc in ['utf-8', 'iso-8859-1', 'windows-1252', 'ascii']:
                        try:
                            decoded = response.content.decode(enc, errors='strict')
                            if '<' in decoded and '>' in decoded:  # Basic HTML check
                                logger.debug(f"Successfully decoded with {enc}")
                                return decoded
                        except (UnicodeDecodeError, AttributeError):
                            continue
                    
                    # Last resort: decode with errors='replace'
                    logger.warning("Using fallback decoding with error replacement")
                    return response.content.decode('utf-8', errors='replace')
                    
            except (UnicodeDecodeError, AttributeError) as e:
                logger.error(f"Decoding error: {e}")
                return response.content.decode('utf-8', errors='replace')
        
        except Timeout:
            raise RequestException(f"Request timeout for {url}")
        except ConnectionError as e:
            raise RequestException(f"Connection error for {url}: {e}")
        except Exception as e:
            raise RequestException(f"Failed to fetch {url}: {e}")
    
    def _parse_and_clean(self, html: str, profile: str) -> BeautifulSoup:
        """
        Parse HTML and remove boilerplate.
        
        Args:
            html: HTML content
            profile: Extraction profile
            
        Returns:
            Cleaned BeautifulSoup object
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
        except Exception as e:
            logger.warning(f"Failed to parse with lxml, falling back to html.parser: {e}")
            soup = BeautifulSoup(html, 'html.parser')
        
        # Remove common boilerplate
        for selector in COMMON_REMOVE_SELECTORS:
            for element in soup.select(selector):
                element.decompose()
        
        # Remove profile-specific boilerplate
        profile_config = EXTRACTION_PROFILES.get(profile, {})
        for selector in profile_config.get("remove_selectors", []):
            for element in soup.select(selector):
                element.decompose()
        
        return soup
    
    def _extract_title(self, soup: BeautifulSoup, profile: str) -> str:
        """
        Extract page title.
        
        Args:
            soup: BeautifulSoup object
            profile: Extraction profile
            
        Returns:
            Title string
        """
        # Try profile-specific selectors first
        profile_config = EXTRACTION_PROFILES.get(profile, {})
        for selector in profile_config.get("title_selectors", []):
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text:
                    return text
        
        # Fallback to og:title meta tag
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"]
        
        # Fallback to <title> tag
        if soup.title:
            return soup.title.string or ""
        
        return ""
    
    def _extract_content(self, soup: BeautifulSoup, profile: str) -> str:
        """
        Extract main content from page with garbage content detection.
        
        Args:
            soup: BeautifulSoup object
            profile: Extraction profile
            
        Returns:
            Cleaned content text
        """
        profile_config = EXTRACTION_PROFILES.get(profile, {})
        selectors = profile_config.get("selectors", ["main", ".content", "article"])
        
        # Try profile-specific content selectors
        content = None
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                content = element
                break
        
        # Fallback to body
        if not content:
            content = soup.body or soup.html or soup
        
        # Extract text with paragraph preservation
        paragraphs = []
        for p in content.find_all(['p', 'div', 'section'], recursive=True):
            text = p.get_text(strip=True)
            if text and len(text) > 20:  # Skip very short lines
                # Check if text is actually readable (not binary garbage)
                if self._is_readable_text(text):
                    paragraphs.append(text)
        
        # Join and clean
        full_text = '\n\n'.join(paragraphs)
        full_text = self._normalize_whitespace(full_text)
        
        # Final check: if content looks like garbage, return empty
        if full_text and not self._is_readable_text(full_text[:500]):
            logger.warning("Extracted content appears to be binary/garbage data")
            return ""
        
        return full_text[:10000]  # Limit to 10k chars

    def _extract_structured_sections(self, soup: BeautifulSoup, max_sections: int = 8) -> List[Dict[str, Any]]:
        """Capture heading-based sections to retain document structure."""
        sections: List[Dict[str, Any]] = []
        if not soup:
            return sections
        heading_tags = ['h1', 'h2', 'h3', 'h4']
        for heading in soup.find_all(heading_tags):
            heading_text = heading.get_text(" ", strip=True)
            if not heading_text or len(heading_text) < 4:
                continue
            snippet_parts: List[str] = []
            bullet_points: List[str] = []
            sibling = heading.next_sibling
            while sibling:
                name = getattr(sibling, 'name', None)
                if name in heading_tags:
                    break
                if name in ['p', 'div', 'section']:
                    text = sibling.get_text(" ", strip=True)
                    if text and len(text) > 30 and self._is_readable_text(text):
                        snippet_parts.append(text)
                elif name in ['ul', 'ol']:
                    for li in sibling.find_all('li', recursive=False):
                        li_text = li.get_text(" ", strip=True)
                        if li_text:
                            bullet_points.append(li_text)
                sibling = sibling.next_sibling
                if sum(len(part) for part in snippet_parts) > 900:
                    break
            if not snippet_parts and not bullet_points:
                continue
            snippet = ' '.join(snippet_parts).strip()
            if len(snippet) > 600:
                snippet = snippet[:597].rstrip() + "..."
            sections.append({
                "heading": heading_text,
                "level": heading.name,
                "snippet": snippet,
                "bullets": bullet_points[:5]
            })
            if len(sections) >= max_sections:
                break
        if not sections and soup.body:
            fallback_text = soup.body.get_text(" ", strip=True)
            if fallback_text:
                fallback = fallback_text[:400] + ("..." if len(fallback_text) > 400 else "")
                sections.append({
                    "heading": "Overview",
                    "level": "body",
                    "snippet": fallback,
                    "bullets": []
                })
        return sections
    
    def _is_readable_text(self, text: str) -> bool:
        """
        Check if text is readable (not binary garbage).
        
        Args:
            text: Text to check
            
        Returns:
            True if text appears readable
        """
        if not text:
            return False
        
        # Check for high ratio of non-ASCII characters
        non_ascii = sum(1 for c in text if ord(c) > 127)
        if len(text) > 50 and non_ascii / len(text) > 0.5:
            return False
        
        # Check for common control characters (sign of binary data)
        control_chars = sum(1 for c in text if ord(c) < 32 and c not in '\n\r\t')
        if control_chars > len(text) * 0.1:
            return False
        
        # Check for reasonable word-like patterns
        # At least some spaces should exist in readable text
        if len(text) > 100 and text.count(' ') < len(text) * 0.05:
            return False
        
        return True

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace while keeping paragraph separation."""
        if not text:
            return ""
        lines = [line.strip() for line in text.splitlines()]
        lines = [line for line in lines if line]
        return '\n\n'.join(lines)
    
    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract entities from content using hybrid approach.
        
        Args:
            text: Content text
            
        Returns:
            List of extracted entities
        """
        try:
            # Use hybrid extractor (combines rule-based + LLM)
            entities = self.hybrid_extractor.extract_entities(text)
            # Already sorted and limited in hybrid extractor
            return entities
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return []

    def _run_keyword_extraction(
        self,
        soup: BeautifulSoup,
        text: str,
        keywords: List[str],
        use_llm: bool = True,
        min_relevance_score: float = 0.2
    ) -> Dict[str, Any]:
        """Unified helper for keyword extraction with optional LLM support."""
        if not keywords:
            return {
                "keywords_used": [],
                "matched_sections": [],
                "summary": "",
                "relevance_score": 0.0,
                "total_matches": 0,
                "quality_score": 0.0,
                "content_quality": "unknown",
                "extraction_method": "rule-based",
                "key_points": []
            }

        if use_llm and self.hybrid_keyword_extractor:
            result = self.hybrid_keyword_extractor.extract(soup, text, keywords, use_llm=True)
        else:
            result = self.keyword_extractor.extract_by_keywords(
                soup,
                keywords,
                context_sentences=3,
                min_relevance_score=min_relevance_score
            )
            result["quality_score"] = result.get("relevance_score", 0.0)
            result["content_quality"] = self._assess_quality(
                result.get("total_matches", 0),
                result.get("relevance_score", 0.0)
            )
            result["extraction_method"] = "rule-based"

        if not result.get("key_points"):
            result["key_points"] = self._build_key_points(result.get("matched_sections", []))

        return result

    def _build_key_points(self, matched_sections: List[Dict[str, Any]], limit: int = 5) -> List[str]:
        """Create concise key points from matched sections for readability."""
        key_points = []
        for section in matched_sections:
            context = section.get("context") or section.get("text", "")
            if not context:
                continue
            snippet = context.strip()
            if len(snippet) > 220:
                snippet = snippet[:217].rstrip() + "..."
            key_points.append(snippet)
            if len(key_points) >= limit:
                break
        return key_points
    
    def _calculate_extraction_quality(
        self,
        keyword_results: Dict[str, Any],
        content_length: int,
        entity_count: int
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive quality metrics for the extraction.
        
        Args:
            keyword_results: Results from keyword extraction
            content_length: Length of extracted content
            entity_count: Number of extracted entities
            
        Returns:
            Dictionary with quality metrics
        """
        # Extract metrics
        relevance_score = keyword_results.get("relevance_score", 0.0)
        total_matches = keyword_results.get("total_matches", 0)
        quality_score = keyword_results.get("quality_score", relevance_score)
        content_quality = keyword_results.get("content_quality", "unknown")
        
        # Calculate completeness score
        completeness = 0.0
        if content_length > 1000:
            completeness += 0.3
        if total_matches >= 5:
            completeness += 0.3
        if entity_count >= 3:
            completeness += 0.2
        if relevance_score >= 0.5:
            completeness += 0.2
        
        # Calculate overall score (weighted average)
        overall_score = (
            quality_score * 0.4 +
            relevance_score * 0.3 +
            completeness * 0.3
        )
        
        # Determine grade
        if overall_score >= 0.8:
            grade = "A"
        elif overall_score >= 0.65:
            grade = "B"
        elif overall_score >= 0.5:
            grade = "C"
        elif overall_score >= 0.3:
            grade = "D"
        else:
            grade = "F"
        
        return {
            "overall_score": round(overall_score, 3),
            "grade": grade,
            "relevance_score": round(relevance_score, 3),
            "quality_score": round(quality_score, 3),
            "completeness_score": round(completeness, 3),
            "content_quality": content_quality,
            "metrics": {
                "content_length": content_length,
                "keyword_matches": total_matches,
                "entities_found": entity_count
            },
            "assessment": self._get_quality_assessment(grade, overall_score)
        }
    
    def _assess_quality(self, matches: int, relevance: float) -> str:
        """Assess content quality based on matches and relevance."""
        if matches >= 5 and relevance >= 0.7:
            return "high"
        elif matches >= 3 and relevance >= 0.4:
            return "medium"
        else:
            return "low"
    
    def _get_quality_assessment(self, grade: str, score: float) -> str:
        """Get human-readable quality assessment."""
        assessments = {
            "A": "Excellent extraction quality - highly relevant and comprehensive content found.",
            "B": "Good extraction quality - relevant content found with minor gaps.",
            "C": "Fair extraction quality - some relevant content found, but incomplete.",
            "D": "Poor extraction quality - limited relevant content found.",
            "F": "Failed extraction - no meaningful relevant content found."
        }
        return assessments.get(grade, "Quality assessment unavailable.")

    def _auto_select_keywords(self, content: str, max_keywords: int = 6) -> List[str]:
        """Derive representative keywords from extracted content for scoring."""
        if not content:
            return []
        tokens = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        if not tokens:
            return []
        stop_words = getattr(self.keyword_extractor, 'stop_words', set())
        candidates = [token for token in tokens if token not in stop_words]
        if not candidates:
            return []
        frequency = Counter(candidates)
        ordered = [word for word, _ in frequency.most_common(max_keywords * 2)]
        unique_ordered: List[str] = []
        for word in ordered:
            if word not in unique_ordered:
                unique_ordered.append(word)
            if len(unique_ordered) >= max_keywords:
                break
        return unique_ordered

    def _generate_semantic_summary(
        self,
        title: str,
        content: str,
        structured_sections: List[Dict[str, Any]],
        entities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Produce a semantic summary, preferring LLM output when available."""
        if not content:
            return {
                "summary": "",
                "topics": [],
                "entities": [],
                "suggested_title": title,
                "source": "none"
            }
        fallback_topics = [section["heading"] for section in structured_sections[:5]]
        fallback_entities = [
            {"name": entity.get("name"), "type": entity.get("type")}
            for entity in entities[:5]
            if entity.get("name")
        ]
        summary_info = {
            "summary": self._fallback_summary(content),
            "topics": fallback_topics,
            "entities": fallback_entities,
            "suggested_title": title,
            "source": "heuristic"
        }
        if not self.llm_client_config:
            return summary_info
        try:
            sections_text = "\n".join(
                f"- {section['heading']}: {section['snippet']}"
                for section in structured_sections[:5]
            )
            llm_input = (
                f"Title: {title or 'N/A'}\n"
                f"Sections:\n{sections_text}\n\n"
                f"Content:\n{content[:6000]}"
            )
            prompt = LLM_SUMMARY_PROMPT.format(content=llm_input)
            response_text = self._call_llm(prompt, temperature=0.35, max_tokens=700)
            if not response_text:
                return summary_info
            cleaned = re.sub(r'```json\s*', '', response_text)
            cleaned = re.sub(r'```\s*', '', cleaned).strip()
            payload = json.loads(cleaned)
            summary_info.update({
                "summary": payload.get("summary", summary_info["summary"]),
                "topics": payload.get("topics", summary_info["topics"]),
                "entities": payload.get("entities", summary_info["entities"]),
                "suggested_title": payload.get("suggested_title", summary_info["suggested_title"]),
                "source": "llm"
            })
            return summary_info
        except Exception as exc:
            logger.debug(f"Semantic summary fallback due to LLM error: {exc}")
            return summary_info

    def _call_llm(self, prompt: str, temperature: float = 0.4, max_tokens: int = 600) -> str:
        """Call LiteLLM-compatible endpoint with standard settings."""
        if not self.llm_client_config:
            return ""
        try:
            headers = {
                "accept": "application/json",
                "Authorization": self.llm_client_config["auth_header"],
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.llm_client_config["model"],
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "stream": False,
                "use_job": self.llm_client_config["use_job"],
                "max_tokens": max_tokens
            }
            response = requests.post(
                f"{self.llm_client_config['base_url']}/chat/completions",
                json=payload,
                headers=headers,
                timeout=45
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")
            logger.warning(f"LLM call failed with status {response.status_code}")
            return ""
        except Exception as exc:
            logger.error(f"LLM call error: {exc}")
            return ""

    def _fallback_summary(self, content: str, sentence_count: int = 2) -> str:
        """Generate a quick deterministic summary if LLM is unavailable."""
        if not content:
            return ""
        sentences = re.split(r'(?<=[.!?])\s+', content.strip())
        summary = ' '.join(sentences[:sentence_count]).strip()
        if not summary:
            return content[:200].strip()
        return summary

    def _build_llm_client_config(self) -> Dict[str, Any]:
        """Assemble reusable LiteLLM client configuration."""
        return {
            "auth_header": self._format_auth_header(LITELLM_API_KEY),
            "base_url": LITELLM_BASE_URL.rstrip('/'),
            "model": LITELLM_MODEL,
            "temperature": LITELLM_TEMPERATURE,
            "use_job": LITELLM_USE_JOB
        }

    @staticmethod
    def _format_auth_header(api_key: str) -> str:
        """Ensure Authorization header contains Bearer prefix."""
        if not api_key:
            return ""
        return api_key if api_key.lower().startswith("bearer ") else f"Bearer {api_key}"
    
    def extract_from_site(
        self,
        start_url: str,
        keywords: Optional[List[str]] = None,
        max_pages: int = 50,
        max_depth: int = 3,
        use_llm: bool = True,
        extraction_profile: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract data from all pages of a website with comprehensive quality tracking.
        
        Args:
            start_url: Starting URL to crawl from
            keywords: Optional keywords for focused extraction
            max_pages: Maximum number of pages to extract from
            max_depth: Maximum crawl depth
            use_llm: Whether to use LLM for extraction
            extraction_profile: Profile for entity extraction (if not using keywords)
            
        Returns:
            Dictionary with aggregated results from all pages
        """
        start_time = time.time()
        
        logger.info(f"Starting site-wide extraction from {start_url}")
        logger.info(f"Max pages: {max_pages}, Keywords: {keywords or 'None'}")
        
        # Initialize crawler
        crawler = WebCrawler(
            max_pages=max_pages,
            max_depth=max_depth,
            same_domain_only=True,
            delay_between_requests=0.5,
            user_agent=USER_AGENT,
            respect_robots=False  # Set to False by default for better extraction
        )
        
        # Crawl the site
        crawled_pages = crawler.crawl(start_url)
        
        logger.info(f"Crawled {len(crawled_pages)} pages, starting extraction...")
        
        # Extract from each page
        results = []
        successful = 0
        failed = 0
        
        for i, page in enumerate(crawled_pages, 1):
            try:
                logger.info(f"Extracting [{i}/{len(crawled_pages)}]: {page['url']}")
                
                if keywords:
                    # Keyword-based extraction
                    result = self.extract_by_keywords(
                        url=page['url'],
                        keywords=keywords,
                        raw_html=page['html'],
                        use_llm=use_llm
                    )
                else:
                    # Entity-based extraction
                    profile = extraction_profile or "news"
                    result = self.extract(
                        url=page['url'],
                        raw_html=page['html'],
                        extraction_profile=profile
                    )
                
                # Add crawl metadata
                result['metadata']['crawl_depth'] = page['depth']
                result['metadata']['page_number'] = i
                
                results.append(result)
                successful += 1
                
            except Exception as e:
                logger.error(f"Failed to extract from {page['url']}: {e}")
                failed += 1
        
        total_duration_ms = int((time.time() - start_time) * 1000)
        
        # Build aggregated response
        response = {
            "start_url": start_url,
            "total_pages_crawled": len(crawled_pages),
            "successful_extractions": successful,
            "failed_extractions": failed,
            "keywords": keywords,
            "extraction_profile": extraction_profile,
            "pages": results,
            "metadata": {
                "fetched_at": datetime.utcnow().isoformat() + "Z",
                "total_duration_ms": total_duration_ms
            },
            "summary": self._create_site_summary(results, keywords)
        }
        
        logger.info(f"Site extraction completed: {successful} successful, {failed} failed")
        
        return response
    
    def _create_site_summary(
        self,
        results: List[Dict[str, Any]],
        keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a comprehensive summary of site-wide extraction results with quality metrics.
        
        Args:
            results: List of extraction results
            keywords: Optional keywords used
            
        Returns:
            Summary dictionary with quality scores and statistics
        """
        if not results:
            return {
                "total_pages": 0,
                "avg_relevance": 0.0,
                "total_matches": 0,
                "overall_quality_score": 0.0,
                "quality_grade": "F",
                "top_keywords": []
            }
        
        if keywords:
            # Keyword extraction summary with quality metrics
            total_matches = sum(
                r.get('keyword_extraction', {}).get('total_matches', 0)
                for r in results
            )
            
            relevance_scores = [
                r.get('keyword_extraction', {}).get('relevance_score', 0.0)
                for r in results
            ]
            avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
            
            # Calculate quality scores across all pages
            quality_scores = [
                r.get('quality_metrics', {}).get('overall_score', 0.0)
                for r in results if 'quality_metrics' in r
            ]
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else avg_relevance
            
            # Determine overall grade
            if avg_quality >= 0.8:
                overall_grade = "A"
            elif avg_quality >= 0.65:
                overall_grade = "B"
            elif avg_quality >= 0.5:
                overall_grade = "C"
            elif avg_quality >= 0.3:
                overall_grade = "D"
            else:
                overall_grade = "F"
            
            # Find pages with highest quality
            quality_distribution = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
            for r in results:
                grade = r.get('quality_metrics', {}).get('grade', 'F')
                quality_distribution[grade] = quality_distribution.get(grade, 0) + 1
            
            # Find pages with highest relevance
            top_pages = sorted(
                results,
                key=lambda r: r.get('quality_metrics', {}).get('overall_score', 0.0),
                reverse=True
            )[:10]
            
            return {
                "total_pages": len(results),
                "avg_relevance": round(avg_relevance, 3),
                "avg_quality_score": round(avg_quality, 3),
                "overall_quality_grade": overall_grade,
                "total_matches": total_matches,
                "keywords_used": keywords,
                "quality_distribution": quality_distribution,
                "top_quality_pages": [
                    {
                        "url": p['metadata']['source_url'],
                        "title": p.get('title', 'Untitled'),
                        "quality_score": p.get('quality_metrics', {}).get('overall_score', 0.0),
                        "grade": p.get('quality_metrics', {}).get('grade', 'F'),
                        "relevance": p.get('keyword_extraction', {}).get('relevance_score', 0.0),
                        "matches": p.get('keyword_extraction', {}).get('total_matches', 0)
                    }
                    for p in top_pages
                ],
                "extraction_statistics": {
                    "high_quality_pages": quality_distribution.get("A", 0) + quality_distribution.get("B", 0),
                    "medium_quality_pages": quality_distribution.get("C", 0),
                    "low_quality_pages": quality_distribution.get("D", 0) + quality_distribution.get("F", 0),
                    "avg_matches_per_page": round(total_matches / len(results), 2) if results else 0
                }
            }
        else:
            # Entity extraction summary
            all_entities = []
            for r in results:
                all_entities.extend(r.get('entities', []))
            
            # Count entity types
            entity_counts = {}
            for entity in all_entities:
                entity_type = entity.get('type', 'unknown')
                entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
            
            return {
                "total_pages": len(results),
                "total_entities": len(all_entities),
                "entity_types": entity_counts,
                "pages_with_content": sum(
                    1 for r in results if len(r.get('content', '')) > MIN_CONTENT_LENGTH
                )
            }
    
    def extract_from_site_semantic(
        self,
        start_url: str,
        query: str,
        max_pages: int = 50,
        max_depth: int = 3,
        use_llm: bool = True
    ) -> Dict[str, Any]:
        """
        Extract from entire site using semantic query understanding.
        
        Args:
            start_url: Starting URL
            query: Natural language query or keywords
            max_pages: Maximum pages to crawl
            max_depth: Maximum crawl depth
            use_llm: Whether to use LLM for semantic extraction
            
        Returns:
            Dictionary with site-wide semantic extraction results
        """
        start_time = time.time()
        
        # Initialize crawler
        crawler = WebCrawler(
            max_pages=max_pages,
            max_depth=max_depth
        )
        
        # Process query once
        from processors.semantic_query_processor import SemanticQueryProcessor
        from config import LITELLM_API_KEY, LITELLM_MODEL, LITELLM_BASE_URL
        
        semantic_processor = SemanticQueryProcessor(
            api_key=LITELLM_API_KEY,
            model=LITELLM_MODEL,
            base_url=LITELLM_BASE_URL
        )
        
        logger.info(f"Starting site-wide semantic extraction: '{query}'")
        query_params = semantic_processor.process_query(query)
        keywords = query_params.get('keywords', [query])
        
        logger.info(f"Crawling site: {start_url} (max_pages={max_pages}, max_depth={max_depth})")
        pages = crawler.crawl(start_url)
        logger.info(f"Found {len(pages)} pages to extract from")
        
        results = []
        failed = []
        
        for i, page_data in enumerate(pages, 1):
            page_url = page_data['url']
            logger.info(f"Extracting page {i}/{len(pages)}: {page_url}")
            
            try:
                # Use semantic extraction
                result = self.extract_by_semantic_query(
                    url=page_url,
                    query=query,
                    use_llm=use_llm,
                    raw_html=page_data.get('html')
                )
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Failed to extract from {page_url}: {e}")
                failed.append({'url': page_url, 'error': str(e)})
        
        total_duration_ms = int((time.time() - start_time) * 1000)
        
        # Build summary
        summary = self._create_site_summary(results, keywords)
        
        return {
            "start_url": start_url,
            "query": query,
            "query_analysis": query_params,
            "keywords": keywords,
            "total_pages_crawled": len(pages),
            "successful_extractions": len(results),
            "failed_extractions": len(failed),
            "pages": results,
            "failed_pages": failed,
            "summary": summary,
            "metadata": {
                "fetched_at": datetime.utcnow().isoformat() + "Z",
                "crawl_config": {
                    "max_pages": max_pages,
                    "max_depth": max_depth
                },
                "total_duration_ms": total_duration_ms,
                "avg_page_duration_ms": int(total_duration_ms / max(len(results), 1))
            },
            "trace": {
                "agent_id": AGENT_ID,
                "model_used": MODEL_USED + "+semantic-query-processor",
                "extraction_mode": "site_semantic",
                "llm_used": use_llm,
                "semantic_processing": True
            }
        }
    
    def close(self):
        """Clean up resources."""
        self.session.close()


def create_agent(use_llm: bool = True) -> WebExtractionAgent:
    """
    Factory function to create agent.
    
    Args:
        use_llm: Whether to use LLM for enhanced extraction (default: True)
    
    Returns:
        WebExtractionAgent instance
    """
    return WebExtractionAgent(use_llm=use_llm)
