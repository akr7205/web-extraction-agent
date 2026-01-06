# Web Extraction Agent

A lightweight, open-source agent for extracting structured data from web pages with **comprehensive quality scoring** and **LLM-powered intelligence**. Features hybrid extraction combining rule-based patterns with advanced language models for meaningful, measurable results.

## 🆕 Latest: Quality Improvements

**NEW Quality Scoring System!** All extractions now include:
- **📊 Quality Grades (A-F)** - Instant quality assessment
- **🎯 Overall Score (0-1)** - Quantifiable extraction quality
- **📈 Multiple Metrics** - Relevance, completeness, content quality
- **🤖 LLM Enhancement** - 20-30% better extraction with AI
- **📑 Detailed Reports** - Comprehensive quality breakdowns

[**Quick Start: Test Quality Scoring**](#quick-quality-test) | [**View Full Documentation**](QUALITY_IMPROVEMENTS.md)

## Features

### Core Capabilities
- **🎯 Keyword-Based Extraction**: Extract content focused on specific keywords with relevance scoring
- **🕷️ Site-Wide Extraction**: Extract from all pages of a website with quality tracking
- **📊 Quality Scoring**: Every extraction includes A-F grade and 0-1 score
- **🤖 Hybrid Extraction**: Combines rule-based + LLM for best results
- **Safe Remote Fetching**: Secure HTTP/HTTPS fetching with timeout protection
- **Intelligent Parsing**: HTML parsing with automatic boilerplate removal

### Extraction Methods
- **Rule-Based**: Fast, reliable pattern matching (0.3-0.8s)
- **LLM-Enhanced**: AI-powered semantic extraction (1-3s)
- **Hybrid** *(Recommended)*: Combines both for optimal quality

### Quality Metrics
- **Overall Score**: Weighted combination of all metrics
- **Relevance Score**: Keyword match quality
- **Quality Score**: Content quality assessment (LLM)
- **Completeness Score**: Extraction completeness
- **Content Quality**: High/Medium/Low rating
- **Performance Trace**: Detailed timing breakdown

### Entity Extraction
- Companies (with confidence scoring)
- People (with title awareness)
- Dates & Amounts
- Keyword-specific entities
- Smart deduplication

## Installation

### Prerequisites

- Python 3.8+
- pip or conda

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd web-extractor-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. **Recommended**: Enable LLM for best quality (20-30% improvement):

**LiteLLM (Cloud API):**
```bash
# Configure in .env
cp .env.example .env
# Edit .env and set:
# USE_LLM=true
# LITELLM_API_KEY=your_api_key_here
# LITELLM_MODEL=deepinfra/Qwen/Qwen3-235B-A22B-Thinking-2507
```

See [LITELLM_GUIDE.md](LITELLM_GUIDE.md) for detailed LiteLLM setup instructions.

## Quick Quality Test

Test extraction quality with a single command:

```bash
# Quick test with quality scoring
python quick_quality_test.py https://techcrunch.com/article -k AI startup funding

# Test without LLM (faster)
python quick_quality_test.py https://example.com -k technology --no-llm

# Save detailed results
python quick_quality_test.py https://example.com -k AI ML -o results.json
```

**What you'll see:**
- Quality Grade (A-F) with visual indicator
- Overall Score (0-1) with progress bar
- Key metrics (relevance, quality, completeness)
- Extraction preview
- Performance timing
- Actionable recommendations

## Quick Start

### Python API

#### High-Quality Keyword Extraction (Recommended)

```python
from src.web_extractor import create_agent

# Create agent with LLM for best quality
agent = create_agent(use_llm=True)

# Extract with quality scoring
result = agent.extract_by_keywords(
    url="https://techcrunch.com/article",
    keywords=["AI", "machine learning", "startup", "funding"],
    use_llm=True
)

# Check quality
qm = result['quality_metrics']
print(f"Quality Grade: {qm['grade']}")  # A, B, C, D, or F
print(f"Overall Score: {qm['overall_score']}")  # 0.0 to 1.0
print(f"Assessment: {qm['assessment']}")

# Process if high quality
if qm['grade'] in ['A', 'B']:
    print("High quality extraction!")
    summary = result['keyword_extraction']['summary']
    entities = result.get('keyword_entities', {})
    # Process your data...
else:
    print(f"Low quality: {qm['assessment']}")
    # Adjust keywords or try different URL

agent.close()
```

#### Standard Extraction

```python
from src.web_extractor import create_agent

# Create agent
agent = create_agent(use_llm=True)

# Extract from URL
result = agent.extract(
    url="https://news.example.com/article",
    extraction_profile="news"
)

# Extract from HTML string
html_content = """<html>...</html>"""
result = agent.extract(
    url="https://example.com",
    raw_html=html_content,
    extraction_profile="product"
)

agent.close()
```

#### Keyword-Based Extraction

Universal extraction that works on ANY content type - just like Perplexity!

```python
from src.web_extractor import WebExtractionAgent

# Create agent
agent = WebExtractionAgent(use_llm=True)

# Extract content focused on specific keywords
# Now with quality metrics!
result = agent.extract_by_keywords(
    url="https://techcrunch.com/latest",
    keywords=["AI", "machine learning", "startup", "funding"],
    use_llm=True
)

# Check quality metrics
print(f"Quality Grade: {result['quality_metrics']['grade']}")
print(f"Relevance Score: {result['keyword_extraction']['relevance_score']}")
print(f"Total Matches: {result['keyword_extraction']['total_matches']}")
print(f"Summary: {result['keyword_extraction']['summary']}")
```

See [KEYWORD_EXTRACTION_GUIDE.md](KEYWORD_EXTRACTION_GUIDE.md) and [QUALITY_QUICK_REFERENCE.md](QUALITY_QUICK_REFERENCE.md) for detailed usage.

#### Site-Wide Extraction with Quality Tracking

Extract from **all pages** of a website with comprehensive quality metrics:

```python
from src.web_extractor import WebExtractionAgent

# Create agent
agent = WebExtractionAgent(use_llm=True)

# Extract from entire website with quality tracking
result = agent.extract_from_site(
    start_url="https://example.com",
    keywords=["AI", "technology", "innovation"],
    max_pages=50,
    max_depth=3,
    use_llm=True
)

# Access quality summary
summary = result['summary']
print(f"Overall Grade: {summary['overall_quality_grade']}")
print(f"Average Quality: {summary['avg_quality_score']}")
print(f"High Quality Pages: {summary['extraction_statistics']['high_quality_pages']}")

# View quality distribution
print(f"Quality Distribution: {summary['quality_distribution']}")

# Top quality pages
for page in summary['top_quality_pages'][:5]:
    print(f"Grade {page['grade']}: {page['title']} ({page['quality_score']:.2f})")
```

See [SITE_EXTRACTION_GUIDE.md](SITE_EXTRACTION_GUIDE.md) for comprehensive documentation.
Quick start: [QUICKSTART_SITE_EXTRACTION.md](QUICKSTART_SITE_EXTRACTION.md)

## Understanding Quality Scores

Every extraction now includes comprehensive quality metrics:

### Quality Grade (A-F)
- **Grade A (0.8-1.0)** 🌟: Excellent - Use with confidence
- **Grade B (0.65-0.8)** ✅: Good - Reliable for production
- **Grade C (0.5-0.65)** ⚠️: Fair - Verify results
- **Grade D (0.3-0.5)** ⚠️: Poor - Consider different keywords
- **Grade F (0.0-0.3)** ❌: Failed - Adjust strategy

### Score Components
- **Overall Score**: Weighted combination (Quality 40% + Relevance 30% + Completeness 30%)
- **Relevance Score**: How relevant content is to your keywords
- **Quality Score**: LLM assessment of content quality
- **Completeness Score**: Based on content length, matches, entities

### Example Quality Response
```json
{
  "quality_metrics": {
    "overall_score": 0.86,
    "grade": "A",
    "relevance_score": 0.85,
    "quality_score": 0.88,
    "completeness_score": 0.85,
    "content_quality": "high",
    "assessment": "Excellent extraction quality - highly relevant and comprehensive content found.",
    "metrics": {
      "content_length": 5234,
      "keyword_matches": 12,
      "entities_found": 8
    }
  }
}
```

**Learn more**: [QUALITY_QUICK_REFERENCE.md](QUALITY_QUICK_REFERENCE.md) | [QUALITY_IMPROVEMENTS.md](QUALITY_IMPROVEMENTS.md)

### FastAPI REST API Server

Start the API server:
```bash
cd src
python api.py
```

The server will start at `http://127.0.0.1:8000` with:
- **Interactive API docs**: http://127.0.0.1:8000/docs
- **Alternative docs**: http://127.0.0.1:8000/redoc

**Primary Endpoints (Recommended):**

1. **Extract by Keywords (from URL)** - `POST /extract/keywords` ⭐ **Recommended**
```bash
curl -X POST "http://127.0.0.1:8000/extract/keywords" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://techcrunch.com/article",
    "keywords": ["AI", "startup", "technology"],
    "use_llm": true
  }'
```

2. **Extract by Keywords (from HTML)** - `POST /extract/keywords/html`
```bash
curl -X POST "http://127.0.0.1:8000/extract/keywords/html" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "html": "<html>...</html>",
    "keywords": ["AI", "technology"],
    "use_llm": true
  }'
```

**Legacy Endpoints (Deprecated):**

3. **Extract from URL** - `POST /api/v1/extract/url` *(deprecated, use /extract/keywords instead)*
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/extract/url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "profile": "news"}'
```

4. **Extract from HTML** - `POST /api/v1/extract/html` *(deprecated, use /extract/keywords/html instead)*
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/extract/url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "profile": "news"}'
```

4. **Extract from HTML** - `POST /api/v1/extract/html` *(deprecated, use /extract/keywords/html instead)*
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/extract/html" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "html": "<html>...</html>", "profile": "news"}'
```

3. **Health Check** - `GET /health`
```bash
curl http://127.0.0.1:8000/health
```

4. **List Profiles** - `GET /api/v1/profiles`
```bash
curl http://127.0.0.1:8000/api/v1/profiles
```

**Python Client Example:**
```python
import requests

# Extract from URL
response = requests.post(
    "http://127.0.0.1:8000/api/v1/extract/url",
    json={"url": "https://example.com", "profile": "news"}
)
result = response.json()
print(f"Title: {result['title']}")
print(f"Entities: {len(result['entities'])}")
```

See `api_examples.py` for more examples.

### Command Line Interface

Extract from a URL:
```bash
python src/app.py extract-url https://example.com --profile news --format pretty
```

Extract from an HTML file:
```bash
python src/app.py extract-file page.html https://example.com --profile product
```

View version:
```bash
python src/app.py version
```

## API Reference

### `WebExtractionAgent.extract()`

Extract structured data from a web page.

**Parameters:**
- `url` (str): URL to extract from
- `raw_html` (str, optional): Pre-fetched HTML content
- `extraction_profile` (str): Profile to use - "news", "filing", or "product"

**Returns:** Dictionary with structure:
```json
{
  "title": "Page title",
  "entities": [
    {
      "name": "Apple Inc.",
      "type": "COMPANY",
      "value": "Apple Inc.",
      "confidence": 0.85
    },
    {
      "name": "$123.5 billion",
      "type": "AMOUNT",
      "value": "$123.5B",
      "confidence": 0.9
    }
  ],
  "content": "Cleaned main content text...",
  "metadata": {
    "fetched_at": "2024-01-15T10:30:45.123456Z",
    "source_url": "https://example.com",
    "extraction_profile": "news"
  },
  "trace": {
    "agent_id": "web-extractor-v1",
    "model_used": "beautifulsoup4+rule-based-ner",
    "duration_ms": 543,
    "errors": []
  }
}
```

## Extraction Profiles

### News Profile
Optimized for news articles and blog posts.
- Extracts from common article containers: `<article>`, `main`, `.article-body`
- Removes: navigation, sidebars, comments, ads
- Best for: News sites, blogs, journalism

### Filing Profile
Optimized for financial documents and legal filings.
- Extracts from: `main`, `.content`, `.filing-body`
- Removes: navigation, metadata sections, sidebars
- Best for: SEC filings, financial reports, regulatory documents

### Product Profile
Optimized for e-commerce product pages.
- Extracts from: `main`, `.product-details`, `.description`
- Removes: navigation, reviews, comments, ads
- Best for: Product pages, e-commerce, specifications

## Entity Types

The agent extracts four main entity types:

### COMPANY
Business entities with organizational suffixes
- Pattern: `Inc.`, `LLC`, `Ltd.`, `Corp.`, `Corporation`, `Group`, `PLC`
- Example: "Apple Inc.", "Goldman Sachs Group Inc."
- Confidence: 0.85

### AMOUNT
Monetary amounts and quantities
- Pattern: `$1,000`, `$1.5M`, `5 million`, `2.5B`
- Example: "$123.5 billion", "€500M", "1 million"
- Confidence: 0.9

### DATE
## LLM-Enhanced Extraction

### How It Works

The agent uses a **hybrid approach** combining two extraction methods:

1. **Rule-Based Extraction** (Always Active)
   - Fast regex-based entity recognition
   - ~50-100ms processing time
   - Reliable for structured data patterns
   - No external dependencies

2. **LiteLLM Enhancement** (Optional)
   - Queries managed cloud models through LiteLLM
   - Improves entity accuracy and coverage
   - Detects context-dependent entities
   - Adds ~500-2000ms depending on model latency

### Configuration

Add the LiteLLM block to `.env`:

```bash
USE_LLM=true
LITELLM_API_KEY=replace-with-real-key
LITELLM_BASE_URL=https://litellm-api.predev.praveg.ai/v1
LITELLM_MODEL=deepinfra/Qwen/Qwen3-235B-A22B-Thinking-2507
LITELLM_TEMPERATURE=0.7
LITELLM_USE_JOB=true
```

> **Note:** LiteLLM acts as a unified API layer. Your billing, quotas, and latency depend on the upstream provider you configure through LiteLLM.

### LLM Advantages

- **Better semantic understanding**: Recognizes entities in context
- **Reduced false positives**: LLM validates rule-based findings
- **Entity relationship detection**: Understands connections between entities
- **Improved confidence scoring**: Adds `llm_confidence` metadata for auditing
- **Content classification**: Helps auto-select the best heuristics

### Performance with LiteLLM

```
Without LLM:
- Processing time: 100-300ms
- Entities extracted: 8-15 per typical page
- Accuracy: ~85% for structured patterns

With LiteLLM (Qwen 235B via LiteLLM API):
- Processing time: 700-1800ms (network + model)
- Entities extracted: 15-25 per typical page
- Accuracy: ~95% including semantic entities
```

### Using LLM in Python

```python
from src.web_extractor import create_agent

# With LiteLLM
agent = create_agent(use_llm=True)
result = agent.extract(url="https://example.com")

# Without LLM (rule-based only)
agent = create_agent(use_llm=False)
result = agent.extract(url="https://example.com")

agent.close()
```

### Response with LLM

The `trace.model_used` field indicates extraction method:

```json
{
  "trace": {
    "model_used": "beautifulsoup4+rule-based-ner+litellm-llm",
    "duration_ms": 1245,
    "errors": []
  },
  "entities": [
    {
      "name": "Apple Inc.",
      "type": "COMPANY",
      "value": "Apple Inc.",
      "confidence": 0.95,
      "llm_confidence": 0.98
    }
  ]
}
```

### LiteLLM Costs

- **Usage Based**: You pay the upstream provider that LiteLLM routes to
- **Bring Your Own Key**: Choose any supported vendor/model combination
- **Network Dependent**: Requires outbound HTTPS access to the LiteLLM endpoint

### Troubleshooting LLM

**"401 Unauthorized"**
- Verify `LITELLM_API_KEY`
- Ensure the key includes the `Bearer ` prefix if required by your provider

**"Model not found"**
- Double-check `LITELLM_MODEL`
- Confirm the selected provider exposes the requested model name

**Slow responses**
- Lower `LITELLM_TEMPERATURE` or switch to a smaller model
- Disable `use_job` for synchronous responses if supported by the backend
- Set `USE_LLM=false` for bulk runs when semantic accuracy is less critical

Temporal references
- Pattern: `MM/DD/YYYY`, `January 15, 2024`, `12-31-2024`
- Example: "January 15, 2024", "Q4 2024", "December 25, 2025"
- Confidence: 0.85

### PERSON
Individual names
- Pattern: Capitalized proper names
- Example: "Tim Cook", "Elon Musk", "Sarah Anderson"
- Confidence: 0.65

## Terms of Service & Legal Compliance

### User Responsibility

Users of this tool are **solely responsible** for ensuring compliance with:

1. **Website Terms of Service**: Always review and comply with the target website's ToS
2. **Robots.txt**: Respect robots.txt exclusions and crawl delays
3. **Legal Regulations**: Comply with GDPR, CCPA, and other data protection laws
4. **Rate Limiting**: Implement appropriate delays between requests
5. **Copyright**: Do not republish extracted content without permission

### Recommended Practices

- **Identify Your Bot**: Use a descriptive User-Agent header
- **Respect Crawl Delays**: Add delays between requests (default: no delay)
- **Check robots.txt**: Review target domain's crawl rules
- **Honor disallow directives**: Respect exclusion patterns
- **Limit Scope**: Only extract necessary data
- **Cache Results**: Avoid re-fetching identical pages
- **Document Sources**: Always cite and attribute data sources

### Prohibited Use Cases

Do not use this tool for:
- Violating website Terms of Service
- Bypassing authentication or access controls
- Extracting personal information in violation of privacy laws
- Republishing copyrighted content
- Creating competing services through scraping
- Accessing private or protected content
- Denial-of-service attacks or abuse

## Performance Characteristics

### Processing Speed
- Typical page: < 500ms
- Large page (10MB+): < 2000ms
- Average: 400-800ms

### Resource Usage
- Memory: ~50-100MB per extraction
- CPU: Minimal (parsing-bound)
- Network: Determined by page size

### Limitations
- Max content size: 5 MB
- Entity extraction limited to top 20 most confident
- Text output limited to first 10,000 characters
- Request timeout: 10 seconds

## Configuration

Edit `src/config.py` to customize:

```python
# Request settings
REQUEST_TIMEOUT = 10  # seconds
MAX_CONTENT_SIZE = 5 * 1024 * 1024  # 5 MB
USER_AGENT = "Your Bot Name/1.0"

# Entity extraction
MAX_PROCESSING_TIME_MS = 2000
MIN_CONTENT_LENGTH = 50

# Profiles
EXTRACTION_PROFILES = { ... }
```

## Testing

Run the comprehensive test suite:

```bash
cd src
python test_web_extractor.py
```

### Test Coverage

The suite includes:
- **News extraction**: Verifies article content extraction
- **Financial extraction**: Tests filing document parsing
- **Product extraction**: Validates product page handling
- **Malformed HTML**: Ensures graceful error handling
- **Empty pages**: Tests edge cases
- **Entity extraction**: Validates company, amount, date, person extraction
- **Performance**: Ensures < 2 second processing
- **JSON serialization**: Confirms output is JSON-serializable
- **Trace logging**: Validates error tracking

### Running Specific Tests

```bash
python -m pytest test_web_extractor.py::TestWebExtractionAgent::test_news_extraction -v
```

## Architecture

### Components

```
web-extractor-agent/
├── src/
│   ├── web_extractor.py      # Core extraction engine
│   ├── entity_extractor.py   # Entity recognition module
│   ├── config.py             # Configuration and profiles
│   ├── app.py                # CLI and API interface
│   └── test_web_extractor.py # Test suite
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── examples/                 # Example scripts and HTML
```

### Data Flow

```
URL/HTML Input
    ↓
[Fetch] → Safe HTTP retrieval with size/timeout limits
    ↓
[Parse] → BeautifulSoup HTML parsing (lxml backend)
    ↓
[Clean] → Remove boilerplate (scripts, nav, ads)
    ↓
[Extract Title] → Profile-specific selectors + fallbacks
    ↓
[Extract Content] → Article/main content extraction
    ↓
[Extract Entities] → Rule-based NER (Company, Amount, Date, Person)
    ↓
[Format Output] → Consistent JSON with metadata + trace
```

## Troubleshooting

### Connection Timeout
**Problem**: `RequestException: Request timeout`
**Solution**: 
- Increase `REQUEST_TIMEOUT` in config.py
- Check network connectivity
- Verify URL is accessible

### Large Content Size
**Problem**: Warning about exceeding max content size
**Solution**:
- Increase `MAX_CONTENT_SIZE` in config.py
- Target smaller page sections if possible

### Low Entity Extraction
**Problem**: Few or no entities extracted
**Solution**:
- Ensure page has sufficient text content
- Try different extraction profile
- Check that entity patterns match your content

### Encoding Issues
**Problem**: Garbled text in output
**Solution**:
- Ensure proper UTF-8 encoding
- Python handles most encodings automatically
- Check source page encoding declaration

## Examples

### Extract News Article

```python
from src.web_extractor import create_agent

agent = create_agent()
result = agent.extract(
    url="https://news.ycombinator.com/",
    extraction_profile="news"
)

print(f"Title: {result['title']}")
print(f"Content length: {len(result['content'])}")
print(f"Entities found: {len(result['entities'])}")
print(f"Processing time: {result['trace']['duration_ms']}ms")

agent.close()
```

### Extract Financial Filings

```python
from src.web_extractor import create_agent

agent = create_agent()
result = agent.extract(
    url="https://sec.gov/cgi-bin/browse-edgar",
    extraction_profile="filing"
)

# Get financial amounts
amounts = [e for e in result['entities'] if e['type'] == 'AMOUNT']
for amount in amounts:
    print(f"Found: {amount['name']} ({amount['value']})")

agent.close()
```

### Extract Product Information

```python
from src.web_extractor import create_agent
import json

agent = create_agent()
result = agent.extract(
    url="https://example.com/product",
    extraction_profile="product"
)

# Save as JSON
with open("product_data.json", "w") as f:
    json.dump(result, f, indent=2)

agent.close()
```

### Batch Processing with Quality Filtering

```python
from src.web_extractor import create_agent

urls = [
    "https://example1.com",
    "https://example2.com",
    "https://example3.com"
]

keywords = ["AI", "machine learning", "technology"]

agent = create_agent(use_llm=True)
high_quality_results = []
low_quality_results = []

for url in urls:
    try:
        result = agent.extract_by_keywords(url, keywords, use_llm=True)
        
        # Filter by quality
        grade = result['quality_metrics']['grade']
        if grade in ['A', 'B']:
            high_quality_results.append(result)
            print(f"✓ {grade}: {url}")
        else:
            low_quality_results.append(result)
            print(f"⚠  {grade}: {url}")
            
    except Exception as e:
        print(f"✗ Failed: {url} - {e}")

agent.close()

print(f"\nHigh quality: {len(high_quality_results)}")
print(f"Low quality: {len(low_quality_results)}")

# Save high-quality results only
import json
with open("high_quality_results.json", "w") as f:
    json.dump(high_quality_results, f, indent=2)
```

## Recent Improvements (December 2024)

### Quality Scoring System ✨
- **Quantifiable metrics**: 0-1 scores and A-F grades for every extraction
- **Multiple dimensions**: Relevance, quality, completeness scoring
- **Actionable assessments**: Clear recommendations based on quality
- **Performance tracking**: Detailed timing breakdown (fetch, parse, extract)

### Enhanced LLM Integration 🤖
- **Improved prompts**: Focus on meaningful, context-rich entity extraction
- **Hybrid extraction**: Combines rule-based + LLM (40% + 60% weighting)
- **Confidence scoring**: Entities include confidence levels
- **Quality assessment**: LLM evaluates content quality

### Better Entity Extraction 🎯
- **Title-aware person detection**: Recognizes CEO, Dr., Prof., etc.
- **Contextual company extraction**: Identifies companies without suffixes
- **Smart deduplication**: Case-insensitive, intelligent merging
- **Confidence-based ranking**: Top entities by confidence

### Site-Wide Quality Analysis 🌐
- **Quality distribution**: Track grades across all pages
- **Top page ranking**: Identify highest quality pages
- **Extraction statistics**: High/medium/low quality page counts
- **Aggregate metrics**: Overall quality assessment

### Testing & Documentation 📚
- **Quick test tool**: `quick_quality_test.py` for instant quality checks
- **Comprehensive tests**: `test_quality_extraction.py` for detailed analysis
- **Quality guides**: Complete documentation on using quality metrics
- **Examples**: Real-world usage patterns and best practices

**See full details**: [IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md)

## Documentation

### Quality & Improvements
- **[IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md)** - Complete overview of quality improvements
- **[QUALITY_IMPROVEMENTS.md](QUALITY_IMPROVEMENTS.md)** - Detailed technical documentation
- **[QUALITY_QUICK_REFERENCE.md](QUALITY_QUICK_REFERENCE.md)** - Quick reference guide

### Extraction Guides
- **[KEYWORD_EXTRACTION_GUIDE.md](KEYWORD_EXTRACTION_GUIDE.md)** - Keyword extraction details
- **[SITE_EXTRACTION_GUIDE.md](SITE_EXTRACTION_GUIDE.md)** - Site-wide extraction guide
- **[QUICKSTART_SITE_EXTRACTION.md](QUICKSTART_SITE_EXTRACTION.md)** - Quick start

### LLM Setup
- **[LITELLM_GUIDE.md](LITELLM_GUIDE.md)** - LiteLLM integration guide
- **[LITELLM_VERIFICATION_REPORT.md](LITELLM_VERIFICATION_REPORT.md)** - Verification details

### Architecture
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[API_v2_UPDATE.md](API_v2_UPDATE.md)** - API v2 changes

## Contributing

Contributions are welcome! Areas for improvement:

1. **Quality Enhancements**: Further improve scoring algorithms
2. **More LLM Providers**: Add support for additional providers
3. **Advanced Features**: Real-time quality monitoring, A/B testing
4. **Performance**: Further optimize for speed and accuracy
5. **Testing**: Expand test coverage with more edge cases

## License

MIT License - See LICENSE file

## Support

For issues, questions, or suggestions:
- Check the troubleshooting section
- Review existing issues on GitHub
- Create a new issue with:
  - URL that's causing problems (if shareable)
  - Error message and stack trace
  - Expected vs actual behavior

## Version History

### v1.0.0 (2024-01-15)
- Initial release
- Support for news, filing, product profiles
- Rule-based entity extraction
- Comprehensive testing suite
- CLI and Python API
