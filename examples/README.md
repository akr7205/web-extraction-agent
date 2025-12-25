# Web Extractor Agent - Examples

This directory contains example scripts demonstrating various ways to use the Web Extractor Agent.

## Examples Overview

### 1. Basic Extraction (`01_basic_extraction.py`)
Demonstrates simple keyword-based extraction from a single URL.

```bash
python examples/01_basic_extraction.py
```

**Features shown:**
- Initialize the agent
- Extract content using keywords
- Display results with relevance scores

### 2. Semantic Query (`02_semantic_query.py`)
Shows how to use natural language queries for extraction.

```bash
python examples/02_semantic_query.py
```

**Features shown:**
- Natural language query processing
- LLM-enhanced extraction
- Semantic understanding

**Note:** Requires LLM API key in `.env` file.

### 3. Site-Wide Extraction (`03_site_wide_extraction.py`)
Demonstrates crawling and extracting from an entire website.

```bash
python examples/03_site_wide_extraction.py
```

**Features shown:**
- Website crawling
- Multi-page extraction
- Aggregated results and statistics

### 4. Library Usage (`04_library_usage.py`)
Shows how to use Web Extractor as a Python library in your own applications.

```bash
python examples/04_library_usage.py
```

**Features shown:**
- Simple extraction
- Multiple URL processing
- Saving results to files
- Error handling

## Running the Examples

All examples can be run directly:

```bash
# Run a specific example
python examples/01_basic_extraction.py

# Or from the examples directory
cd examples
python 01_basic_extraction.py
```

## Customizing Examples

Feel free to modify these examples to suit your needs:
- Change URLs to your target websites
- Adjust keywords or queries
- Modify extraction parameters
- Add your own processing logic

## Requirements

- Python 3.8+
- All dependencies installed (`pip install -r requirements.txt`)
- For LLM features: Set `LITELLM_API_KEY` in `.env` file

## Need Help?

Refer to the main [README.md](../README.md) for more information or check the source code in the `src/` directory.
