# Project Structure

This document describes the organization of the Web Extractor Agent codebase.

## Directory Layout

```
web-extractor-agent/
│
├── src/                           # Source code
│   ├── __init__.py               # Package initialization
│   ├── web_extractor.py          # Main extraction agent
│   ├── config.py                 # Configuration management
│   ├── cli.py                    # Command-line interface
│   ├── app.py                    # FastAPI application
│   ├── api.py                    # API routes and endpoints
│   │
│   ├── extractors/               # Extraction modules
│   │   ├── __init__.py
│   │   (referenced from parent via imports)
│   │
│   ├── crawlers/                 # Web crawling modules
│   │   ├── __init__.py
│   │   (referenced from parent via imports)
│   │
│   ├── processors/               # Data processing modules
│   │   ├── __init__.py
│   │   (referenced from parent via imports)
│   │
│   ├── utils/                    # Utility modules
│   │   ├── __init__.py
│   │   ├── constants.py          # Application constants
│   │   └── logger.py             # Logging utilities
│   │
│   ├── entity_extractor.py       # Entity recognition
│   ├── keyword_extractor.py      # Keyword matching
│   ├── llm_extractor.py          # LLM-based extraction
│   ├── semantic_query_processor.py  # Query processing
│   └── web_crawler.py            # Website crawler
│
├── tests/                        # Test suite
│   ├── conftest.py              # Pytest configuration and fixtures
│   ├── test_entity_extractor.py # Entity extractor tests
│   ├── test_keyword_extractor.py # Keyword extractor tests
│   ├── test_web_extractor.py    # Main agent tests
│   ├── test_crawler.py          # Crawler tests
│   ├── test_extraction.py       # Integration tests
│   └── test_full_suite.py       # Comprehensive test suite
│
├── examples/                     # Usage examples
│   ├── README.md                # Examples documentation
│   ├── 01_basic_extraction.py   # Basic usage
│   ├── 02_semantic_query.py     # Semantic queries
│   ├── 03_site_wide_extraction.py  # Site crawling
│   └── 04_library_usage.py      # Library integration
│
├── scripts/                      # Utility scripts
│   └── check_litellm.py         # LiteLLM configuration check
│
├── docs/                         # Documentation (if added)
│
├── .env.example                 # Environment configuration template
├── .gitignore                   # Git ignore rules
├── setup.py                     # Package setup script
├── pyproject.toml               # Modern Python project configuration
├── requirements.txt             # Production dependencies
├── README.md                    # Project documentation
├── CONTRIBUTING.md              # Contribution guidelines
├── CHANGELOG.md                 # Version history
├── LICENSE                      # MIT License
├── Makefile                     # Development commands
├── cli_keyword_extract.py       # Interactive CLI (legacy)
└── HEALTH_CHECK_REPORT.txt     # System status report
```

### Directory Responsibilities

- **src/**: Everything that ships with the library/service lives here. Each subpackage owns a specific stage of the extraction pipeline (crawl → preprocess → extract → expose via API/CLI).
- **tests/**: Mirrors the `src` tree so every module has a dedicated test file plus end-to-end coverage in `test_full_suite.py`.
- **examples/**: Ready-to-run scripts demonstrating realistic usage scenarios; best place to copy/paste when prototyping.
- **scripts/**: Operational helpers that developers may run manually (e.g., environment checks) but are not imported elsewhere.
- **docs/**: Optional landing spot for long-form documentation. Add here when README sections start feeling crowded.
- **Project root files**: Tooling (`Makefile`, `requirements.txt`), packaging (`setup.py`, `pyproject.toml`), compliance (`LICENSE`), and operational status artifacts (`HEALTH_CHECK_REPORT.txt`).

## Module Descriptions

### Core Modules

#### `web_extractor.py`
The main extraction agent that orchestrates crawler selection, extraction strategies, and result normalization. It is the single entry point used by the API, CLI, and examples.

**Key Classes:**
- `WebExtractionAgent`: Main agent class for web extraction

**Key Methods:**
- `extract_by_keywords()`: Extract content based on keywords
- `extract_by_semantic_query()`: Extract using natural language
- `extract_from_site_semantic()`: Site-wide extraction

**Interactions:**
- Accepts configuration objects from `config.py`.
- Delegates crawling to `WebCrawler` and extraction logic to the extractor modules.
- Emits structured responses that downstream clients can serialize directly.

#### `config.py`
Central configuration management using environment variables with sensible defaults. Settings cascade in the following order of precedence: CLI args → environment variables → `.env` file → in-code defaults.

**Key Constants:**
- `AGENT_ID`, `VERSION`: Application metadata
- `USE_LLM`, `LITELLM_*`: LLM configuration
- `REQUEST_TIMEOUT`, `MAX_CONTENT_SIZE`: HTTP settings
- `EXTRACTION_PROFILES`: Extraction strategies

**Usage Tips:** Load configuration once at process start and inject it, rather than importing settings ad-hoc, to keep testability high.

### Extractor Modules

#### `entity_extractor.py`
Rule-based entity recognition for companies, people, dates, amounts. Uses deterministic pattern libraries so it is fast, predictable, and easy to reason about.

**Key Classes:**
- `EntityExtractor`: Pattern-based entity recognition

**When to use:** Prefer this module for compliance-critical or offline environments where LLM access is restricted.

#### `keyword_extractor.py`
Keyword matching and relevance scoring.

**Key Classes:**
- `KeywordExtractor`: Rule-based keyword matching
- `LLMKeywordExtractor`: LLM-enhanced extraction
- `HybridKeywordExtractor`: Combines both approaches

**Implementation Notes:** Hybrid mode first runs the rule-based pass for precision, then asks the LLM to fill gaps. This keeps latency predictable while improving recall.

#### `llm_extractor.py`
LLM-powered extraction using LiteLLM.

**Key Classes:**
- `LLMEntityExtractor`: LLM-based entity extraction
- `HybridEntityExtractor`: Combines rule-based and LLM

**Operational Considerations:** Reads provider info from the `LITELLM_*` configuration keys and gracefully degrades to deterministic extractors if LLM usage is disabled.

### Crawler Modules

#### `web_crawler.py`
Website crawling with robots.txt respect and depth control. Handles concurrency, deduplication, and content-type filtering before handing HTML off to processors.

**Key Classes:**
- `WebCrawler`: Multi-page website crawler

**Key Behaviors:**
- Enforces politeness delays based on configuration.
- Maintains a crawl frontier that can be extended for custom scheduling strategies.

### Processor Modules

#### `semantic_query_processor.py`
Processes natural language queries into structured search parameters.

**Key Classes:**
- `SemanticQueryProcessor`: Query understanding and parsing

**Pipeline:** Tokenizes the query, maps synonyms to canonical fields, and prepares prompts/filters that both keyword- and LLM-backed extractors can consume.

### Utility Modules

#### `utils/constants.py`
Application-wide constants and defaults.

#### `utils/logger.py`
Logging configuration and utilities.

**Key Functions:**
- `setup_logger()`: Configure a new logger
- `get_logger()`: Get existing logger instance

### API Modules

#### `app.py`
FastAPI application setup and configuration. Creates the ASGI app, wires dependency injection for `WebExtractionAgent`, and exposes middleware (CORS, error handlers, tracing hooks).

#### `api.py`
REST API endpoints for extraction services. Each route parses request payloads, invokes the agent, and returns a standardized response schema so SDKs remain stable.

#### `cli.py`
Modern command-line interface with argument parsing. Supports both one-off extraction commands and long-running watch modes via subcommands.

#### `cli_keyword_extract.py`
Legacy helper maintained for backward compatibility with early adopters. New features should target `src/cli.py` unless absolute compatibility is required.

## Runtime Data Flow

1. **Configuration Resolution**: `config.py` aggregates defaults, `.env`, and CLI flags into a single settings object.
2. **Input Acquisition**: Depending on the use case, either the crawler (`web_crawler.py`) collects pages or direct HTML/URLs are passed via API/CLI.
3. **Preprocessing**: Processors (currently `SemanticQueryProcessor`) normalize inputs, tokenize keywords, and define the extraction plan.
4. **Extraction**: The agent coordinates keyword, entity, and LLM extractors, merging results per the chosen profile (deterministic, LLM-only, or hybrid).
5. **Post-processing**: Results are deduplicated, ranked, and validated against schema expectations.
6. **Delivery**: Responses surface through FastAPI endpoints, CLI output, or example scripts for embedding in other pipelines.

## Test Structure

Tests are organized by module they're testing:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **Fixtures**: Reusable test data in `conftest.py`

**Recommended Workflow:**
- Run `pytest tests/test_<module>.py` while developing a feature.
- Execute `pytest tests/test_full_suite.py -m "not slow"` before opening a pull request.
- Use fixtures from `conftest.py` to avoid duplicating HTML samples and configuration objects.

## Import Structure

The package uses relative imports internally:

```python
# From within src/
from .config import AGENT_ID, USE_LLM
from .entity_extractor import EntityExtractor
from .web_crawler import WebCrawler
```

External usage:
```python
# From outside src/
from src.web_extractor import WebExtractionAgent
from src.config import VERSION
```

## Configuration Files

### `pyproject.toml`
Modern Python project configuration including:
- Build system configuration
- Project metadata
- Dependencies
- Tool configuration (pytest, black, isort, mypy)

### `setup.py`
Traditional setup script for backward compatibility.

### `.env.example`
Template for environment variables with documentation.

## Development Workflow

1. **Install**: `pip install -e ".[dev]"`
2. **Format**: `make format` (black, isort)
3. **Lint**: `make lint` (flake8, mypy)
4. **Test**: `make test` or `make test-cov`
5. **Run**: `make run-cli` or `make run-api`

**Details:**
- Installation in editable mode ensures local changes are immediately reflected without reinstalling.
- Formatting and linting commands align with CI, so running them locally prevents avoidable pipeline failures.
- Coverage runs (`make test-cov`) upload reports when CI secrets are available; locally they generate HTML under `htmlcov/`.
- `make run-cli` launches the modern CLI, while `make run-api` starts the FastAPI server with auto-reload for rapid iteration.

## Adding New Features

### New Extractor
1. Create module in `src/`
2. Add tests in `tests/test_<module>.py`
3. Import in appropriate `__init__.py`
4. Document in README
5. Add example in `examples/`

**Additional Guidance:**
- Decide early whether the extractor is deterministic, LLM-based, or hybrid so configuration flags can be scoped correctly.
- Reuse helper utilities (e.g., tokenization, HTML parsing) from `utils/` to keep logic centralized.

### New API Endpoint
1. Add route in `src/api.py`
2. Update `src/app.py` if needed
3. Add tests
4. Document in API docs

**Checklist:** Validate request/response models in Pydantic, add OpenAPI metadata, and ensure rate-limiting/logging middleware observe the new route.

### New CLI Command
1. Update `src/cli.py`
2. Add argument to parser
3. Implement handler
4. Update CLI documentation

**Best Practices:** Keep business logic in shared libraries and let the CLI focus on input parsing, so API and CLI stay feature-parity.

## Best Practices

1. **Type Hints**: Use type hints for all functions
2. **Docstrings**: Document all public APIs
3. **Tests**: Write tests for new features
4. **Logging**: Use the logger from `utils.logger`
5. **Configuration**: Use environment variables via `config.py`
6. **Error Handling**: Use try/except with specific exceptions
7. **Code Style**: Follow PEP 8, use black for formatting

## Dependencies

See `requirements.txt` for full list:
- **Web**: requests, aiohttp, beautifulsoup4
- **NLP**: spacy
- **API**: fastapi, uvicorn, pydantic
- **Utilities**: python-dotenv, python-dateutil

## Further Reading

- [README.md](README.md): User documentation
- [CONTRIBUTING.md](CONTRIBUTING.md): Development guide
- [examples/README.md](examples/README.md): Usage examples
