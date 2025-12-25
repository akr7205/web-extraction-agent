"""Configuration for the Web Extraction Agent."""
import os
from typing import Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Version
VERSION = "1.0.0"

# Agent Configuration
AGENT_ID = "web-extractor-v1"
MODEL_USED = "beautifulsoup4+rule-based-ner+litellm-llm"

# LLM Configuration
USE_LLM = os.getenv("USE_LLM", "true").lower() == "true"

# LiteLLM Configuration
LITELLM_API_KEY = os.getenv("LITELLM_API_KEY", "")
LITELLM_BASE_URL = os.getenv("LITELLM_BASE_URL", "https://litellm-api.predev.praveg.ai/v1")
LITELLM_MODEL = os.getenv("LITELLM_MODEL", "deepinfra/Qwen/Qwen3-235B-A22B-Thinking-2507")
LITELLM_TEMPERATURE = float(os.getenv("LITELLM_TEMPERATURE", "0.7"))
LITELLM_USE_JOB = os.getenv("LITELLM_USE_JOB", "true").lower() == "true"

# Request Configuration
REQUEST_TIMEOUT = 10  # seconds
MAX_CONTENT_SIZE = 5 * 1024 * 1024  # 5 MB
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

# Extraction Profiles
EXTRACTION_PROFILES = {
    "news": {
        "selectors": ["article", "main", ".article-body", ".post-content"],
        "title_selectors": ["h1", ".headline", ".title"],
        "remove_selectors": ["nav", ".sidebar", ".comments", ".ads", "script", "style"]
    },
    "filing": {
        "selectors": ["main", ".content", ".filing-body"],
        "title_selectors": ["h1", ".document-title"],
        "remove_selectors": ["nav", ".metadata", ".sidebar", "script", "style"]
    },
    "product": {
        "selectors": ["main", ".product-details", ".description"],
        "title_selectors": ["h1", ".product-name"],
        "remove_selectors": ["nav", ".reviews", ".comments", ".ads", "script", "style"]
    }
}

# Entity Types and Patterns
ENTITY_TYPES = {
    "COMPANY": r"\b(?:Inc\.|LLC|Ltd\.|Corp\.|Corporation|Company|Inc|Co\.)\b",
    "AMOUNT": r"\$[\d,]+(?:\.\d{2})?|\d+(?:\.\d+)?\s*(?:million|billion|thousand|M|B|K)",
    "DATE": r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2},?\s+\d{4}",
    "PERSON": r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b",
}

# Boilerplate Removal Selectors (common across all profiles)
COMMON_REMOVE_SELECTORS = [
    "script", "style", "meta", "link", "noscript",
    ".cookie-notice", ".ad", ".advertisement",
    ".footer", "footer", ".navbar", "nav"
]

# Processing
MAX_PROCESSING_TIME_MS = 2000  # 2 seconds
MIN_CONTENT_LENGTH = 50  # Minimum characters to consider as valid content

# Logging
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = "DEBUG" if DEBUG else "INFO"

# LLM Entity Extraction Prompt
LLM_EXTRACTION_PROMPT = """You are an expert data extraction system. Extract ONLY the most important and meaningful structured entities from the given text.

Focus on extracting:
1. COMPANY: Business names (especially with Inc., Corp., LLC, Ltd.) - include notable companies even without suffixes
2. AMOUNT: Monetary values ($X, billions, millions), revenue, investments, financial figures
3. DATE: Important temporal references (announcements, deadlines, events)
4. PERSON: Key individuals (CEOs, founders, officials, notable figures)

IMPORTANT QUALITY RULES:
- Only extract entities that are central to the content's meaning
- Avoid generic or common terms ("the company", "the person")
- Provide confidence scores: 0.9+ for definite entities, 0.7-0.9 for likely entities, below 0.7 for uncertain
- Extract full context (e.g., "CEO John Smith" not just "John Smith")
- For amounts, include context (e.g., "$5M Series A funding" not just "$5M")

Return ONLY a valid JSON array with objects containing: name, type, value, confidence (0-1)
Do not include explanations, markdown, or any text outside the JSON array.

Text to extract from:
{text}

JSON Array:"""

# LLM Keyword-Focused Extraction Prompt
LLM_KEYWORD_EXTRACTION_PROMPT = """You are an expert content analyst specializing in keyword-focused information extraction.

Your task: Extract and summarize ONLY the information directly relevant to these keywords: {keywords}

Extraction guidelines:
1. Find all mentions and context related to the specified keywords
2. Extract key facts, figures, and statements about these topics
3. Include relevant entities (people, companies, dates, amounts) connected to the keywords
4. Provide brief, factual summaries - no speculation
5. Maintain accuracy - quote or paraphrase precisely
6. Focus on HIGH-QUALITY, meaningful content only
7. Assign relevance scores honestly - only 0.8+ for truly relevant content

Return a JSON object with:
{{
  "summary": "Concise summary of keyword-relevant content (2-3 sentences)",
  "key_points": ["List of 3-5 important facts related to keywords"],
  "entities": [{{"name": "entity", "type": "COMPANY/PERSON/DATE/AMOUNT", "relevance": "why relevant to keywords", "confidence": 0.9}}],
  "keywords_found": ["list of keywords actually found in text"],
  "relevance_score": 0.95,
  "content_quality": "high/medium/low"
}}

IMPORTANT:
- relevance_score: 0.0-1.0 (how relevant content is to keywords)
- content_quality: "high" (detailed, factual), "medium" (some relevance), "low" (generic)
- Only extract content with clear relevance to keywords

Text to analyze:
{text}

JSON Response:"""

# LLM Content Summarization Prompt
LLM_SUMMARY_PROMPT = """You are an expert content analyst. Analyze the extracted content and provide:
1. A concise title if not present
2. Key entities and their relationships
3. Main topics and themes

Content to analyze:
{content}

Provide a structured analysis in JSON format."""
