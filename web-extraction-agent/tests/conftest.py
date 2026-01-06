"""Test configuration and fixtures for pytest."""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


@pytest.fixture
def sample_html():
    """Provide sample HTML for testing."""
    return """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Example Domain</h1>
            <p>This domain is for use in illustrative examples in documents.</p>
            <p>Apple Inc. was founded by Steve Jobs in 1976.</p>
            <p>The company earned $100 million in revenue.</p>
        </body>
    </html>
    """


@pytest.fixture
def sample_keywords():
    """Provide sample keywords for testing."""
    return ["example", "domain", "Apple", "technology"]


@pytest.fixture
def sample_url():
    """Provide sample URL for testing."""
    return "https://example.com"
