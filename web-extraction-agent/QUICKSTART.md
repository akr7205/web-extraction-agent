# 🚀 Quick Start Guide - Web Extractor Agent

Welcome to Web Extractor Agent! This guide will get you up and running in 5 minutes.

## ⚡ Fast Track Installation

```bash
# 1. Clone or navigate to project
cd web-extractor-agent

# 2. Create virtual environment (if not exists)
python -m venv .venv

# 3. Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up environment (optional, for LLM features)
cp .env.example .env
# Edit .env and add your LITELLM_API_KEY if you have one
```

## 🎯 Quick Examples

### Example 1: Simple Extraction (No Setup Required)

```python
import sys
sys.path.insert(0, 'src')

from web_extractor import WebExtractionAgent

# Create agent
agent = WebExtractionAgent(use_llm=False)

# Extract from a website
result = agent.extract_by_keywords(
    url="https://example.com",
    keywords=["example", "domain"]
)

# Show results
print(f"Title: {result['title']}")
print(f"Relevance: {result['keyword_extraction']['relevance_score']:.2f}")
print(f"Matches: {result['keyword_extraction']['total_matches']}")
```

### Example 2: Interactive CLI

```bash
# Run the interactive CLI
python cli_keyword_extract.py

# Follow the prompts:
# 1. Choose extraction mode (single page or site-wide)
# 2. Enter URL(s)
# 3. Enter keywords or query
# 4. Wait for results!
```

### Example 3: Command-Line Arguments

```bash
# Extract with command-line args
python -m src.cli \
  --url https://example.com \
  --keywords "example, domain" \
  --output results.json

# Site-wide extraction
python -m src.cli \
  --url https://example.com \
  --site \
  --keywords "AI, technology" \
  --max-pages 10
```

## 📚 Run Pre-Made Examples

```bash
# Basic extraction
python examples/01_basic_extraction.py

# Site-wide crawling
python examples/03_site_wide_extraction.py

# Library usage patterns
python examples/04_library_usage.py
```

## 🧪 Verify Installation

```bash
# Run tests to make sure everything works
pytest tests/

# Or run comprehensive test suite
python tests/test_full_suite.py
```

## 🔧 Common Use Cases

### Extract Product Information
```python
agent = WebExtractionAgent(use_llm=False)
result = agent.extract_by_keywords(
    url="https://product-page.com",
    keywords=["price", "features", "specifications"]
)
```

### Extract News Articles
```python
agent = WebExtractionAgent(use_llm=True)  # LLM for better understanding
result = agent.extract_by_semantic_query(
    url="https://news-site.com/article",
    query="Give me the main story and key facts"
)
```

### Crawl Entire Website
```python
agent = WebExtractionAgent(use_llm=False)
result = agent.extract_from_site_semantic(
    start_url="https://company-website.com",
    query="pricing, features, contact",
    max_pages=20,
    max_depth=3
)
```

## 💡 Pro Tips

1. **Start without LLM**: It's faster and works great for most cases
   ```python
   agent = WebExtractionAgent(use_llm=False)
   ```

2. **Use LLM for complex queries**: When you need semantic understanding
   ```python
   agent = WebExtractionAgent(use_llm=True)
   ```

3. **Save results**: Always save important extractions
   ```python
   import json
   with open('results.json', 'w') as f:
       json.dump(result, f, indent=2)
   ```

4. **Handle errors gracefully**:
   ```python
   try:
       result = agent.extract_by_keywords(url, keywords)
   except Exception as e:
       print(f"Error: {e}")
   ```

## 🐛 Troubleshooting

### Import Errors
```bash
# Make sure you're in the project directory
cd web-extractor-agent

# Verify Python path
python -c "import sys; print(sys.path)"
```

### Dependencies Missing
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### LLM Not Working
```bash
# Check LLM configuration
python scripts/check_litellm.py

# Make sure .env file exists and has LITELLM_API_KEY set
```

### Tests Failing
```bash
# Run verbose tests to see details
pytest -v

# Check environment setup
python -c "import sys; sys.path.insert(0, 'src'); from config import *; print('Config OK')"
```

## 📖 Next Steps

1. **Read the documentation**:
   - [README.md](README.md) - Full documentation
   - [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Architecture
   - [CONTRIBUTING.md](CONTRIBUTING.md) - Development guide

2. **Explore examples**:
   - Check out `examples/` directory
   - Try modifying them for your use case

3. **Run tests**:
   - `pytest tests/` - Verify everything works
   - Learn from test code

4. **Start developing**:
   - Read [CONTRIBUTING.md](CONTRIBUTING.md)
   - Check out development commands in `Makefile`

## 🆘 Getting Help

- **Check documentation**: Most questions are answered in README.md
- **Run examples**: See working code in `examples/` directory
- **Read tests**: Tests show how to use each component
- **Review code**: Source code is well-documented

## 🎓 Learning Path

1. ✅ **Start here** (this guide)
2. 📚 Read [README.md](README.md) for full features
3. 🔍 Run [examples/](examples/) to see it in action
4. 🧪 Review [tests/](tests/) to understand the API
5. 🏗️ Read [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for architecture
6. 🔧 Check [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

## ✨ You're Ready!

That's it! You now know enough to start using Web Extractor Agent.

Try running:
```bash
python examples/01_basic_extraction.py
```

Happy extracting! 🎉
