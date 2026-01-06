"""
Web Extractor Agent - A comprehensive web extraction and analysis toolkit.

This package provides tools for extracting structured data from web pages,
including entity recognition, keyword extraction, and semantic search capabilities.
"""

__version__ = "1.0.0"
__author__ = "Web Extractor Team"
__license__ = "MIT"

from .web_extractor import WebExtractionAgent
from .config import AGENT_ID, VERSION

__all__ = [
    "WebExtractionAgent",
    "AGENT_ID",
    "VERSION",
]
