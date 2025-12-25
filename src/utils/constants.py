"""
Constants used throughout the application.
"""

# Version
VERSION = "1.0.0"

# HTTP Constants
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
DEFAULT_TIMEOUT = 10
MAX_CONTENT_SIZE = 5 * 1024 * 1024  # 5 MB

# Extraction Constants
MIN_CONTENT_LENGTH = 50
MAX_PROCESSING_TIME_MS = 30000

# Quality Scoring Weights
QUALITY_WEIGHTS = {
    "relevance": 0.4,
    "completeness": 0.3,
    "quality": 0.3
}

# Entity Types
ENTITY_TYPES = [
    "COMPANY",
    "ORG",
    "PERSON",
    "DATE",
    "AMOUNT",
    "LOCATION",
    "PRODUCT",
]

# Crawling Defaults
DEFAULT_MAX_PAGES = 50
DEFAULT_MAX_DEPTH = 3
DEFAULT_DELAY_BETWEEN_REQUESTS = 1.0

# LLM Defaults
DEFAULT_LLM_TEMPERATURE = 0.7
DEFAULT_LLM_MAX_TOKENS = 2000
