# Web Extractor Agent - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     WEB EXTRACTOR AGENT                          │
│                         (v1.0.0)                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │     CLI     │   │  REST API   │   │   Library   │
    │  Interface  │   │   (FastAPI) │   │   (Python)  │
    └─────────────┘   └─────────────┘   └─────────────┘
            │                 │                 │
            └─────────────────┼─────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │                   │
                    │  WebExtractor     │
                    │     Agent         │
                    │   (Orchestrator)  │
                    │                   │
                    └─────────┬─────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
        ┌───────────┐  ┌───────────┐  ┌───────────┐
        │Extractors │  │ Crawlers  │  │Processors │
        └───────────┘  └───────────┘  └───────────┘
                │             │             │
        ┌───────┴───────┐     │      ┌─────┴─────┐
        ▼               ▼     │      ▼           ▼
   ┌────────┐      ┌────────┐│ ┌─────────┐ ┌─────────┐
   │Entity  │      │Keyword ││ │Semantic │ │  Query  │
   │Extract │      │Extract ││ │ Crawler │ │Processor│
   └────────┘      └────────┘│ └─────────┘ └─────────┘
        │               │     │
        ▼               ▼     ▼
   ┌────────────────────────────┐
   │      LLM Enhancement       │
   │       (Optional)           │
   │      LiteLLM Client        │
   └────────────────────────────┘
```

## Component Interaction Flow

### 1. Keyword-Based Extraction (Hybrid Mode)
```
User Input
   │
   ├─► URL + Keywords
   │
   ▼
WebExtractionAgent
   │
   ├─► Fetch HTML (requests)
   │
   ├─► Parse HTML (BeautifulSoup)
   │
   ├─► HybridKeywordExtractor
   │   │
   │   ├─► Rule-based Extraction
   │   │   ├─► Find keyword matches
   │   │   ├─► Extract sections
   │   │   └─► Calculate relevance
   │   │
   │   ├─► LLM Enhancement (if enabled)
   │   │   ├─► Semantic understanding
   │   │   ├─► Context enrichment
   │   │   └─► Quality assessment
   │   │
   │   └─► Merge Results
   │
   ├─► HybridEntityExtractor
   │   │
   │   ├─► Pattern-based NER
   │   │   └─► (companies, people, dates)
   │   │
   │   └─► LLM Entity Extraction (if enabled)
   │
   ├─► Quality Scoring System
   │   ├─► Relevance Score (keyword matches)
   │   ├─► Completeness Score (content coverage)
   │   ├─► Quality Score (LLM assessment)
   │   ├─► Overall Score (weighted avg)
   │   └─► Grade Assignment (A-F)
   │
   ▼
Results with Comprehensive Quality Metrics
   │
   ├─► Grade: A-F
   ├─► Overall Score: 0-1
   ├─► Quality Assessment
   └─► Performance Trace
```

### 2. Semantic Query Extraction (Natural Language)
```
User Input (Natural Language Query)
   │
   ├─► "Find me AI pricing information"
   │
   ▼
SemanticQueryProcessor
   │
   ├─► Parse Query Intent
   │   ├─► Extract keywords
   │   ├─► Determine intent
   │   ├─► Identify search strategy
   │   └─► Set quality requirements
   │
   ▼
WebExtractionAgent
   │
   ├─► Fetch & Parse HTML
   │
   ├─► Hybrid Extraction
   │   ├─► Use extracted keywords
   │   └─► Apply search strategy
   │
   ├─► LLM Semantic Understanding
   │   ├─► Context-aware extraction
   │   ├─► Intent-based filtering
   │   └─► Quality assessment
   │
   ├─► Quality Scoring
   │
   ▼
Semantically Relevant Results
   │
   ├─► Matches query intent
   ├─► Quality scored
   └─► Contextually relevant
```

### 3. Site-Wide Extraction (with Quality Tracking)
```
User Input (Start URL + Keywords)
   │
   ▼
WebCrawler
   │
   ├─► Check robots.txt
   │
   ├─► Discover URLs (BFS/DFS)
   │
   ├─► Respect depth/limits
   │
   ├─► For each page:
   │   │
   │   ├─► Fetch HTML
   │   │
   │   ├─► Hybrid Keyword Extraction
   │   │   └─► (Rule-based + LLM)
   │   │
   │   ├─► Hybrid Entity Extraction
   │   │   └─► (Pattern + LLM NER)
   │   │
   │   └─► Calculate Quality Metrics
   │       ├─► Relevance Score
   │       ├─► Quality Score
   │       ├─► Completeness Score
   │       └─► Overall Score + Grade
   │
   ▼
Aggregated Results with Quality Summary
   │
   ├─► All Page Results
   ├─► Quality Distribution
   ├─► Top Quality Pages
   ├─► Average Quality Score
   └─► Extraction Statistics
```

## Data Flow (Hybrid Extraction Mode)

```
┌──────────┐
│   URL    │
└────┬─────┘
     │
     ▼
┌──────────────┐
│ HTTP Request │
│  (requests)  │
│  + Headers   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ HTML Content │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ BeautifulSoup│
│ Parsing +    │
│ Cleaning     │
└──────┬───────┘
       │
       ├───────────────────┐
       │                   │
       ▼                   ▼
┌──────────────────┐  ┌──────────────────┐
│ Hybrid Keyword   │  │ Hybrid Entity    │
│ Extraction       │  │ Extraction       │
│                  │  │                  │
│ ┌──────────────┐│  │ ┌──────────────┐ │
│ │ Rule-based   ││  │ │ Pattern-based││ │
│ │ + LLM        ││  │ │ + LLM NER    ││ │
│ └──────────────┘│  │ └──────────────┘ │
└────────┬─────────┘  └────────┬─────────┘
         │                     │
         │   ┌─────────────────┤
         │   │                 │
         ▼   ▼                 ▼
┌─────────────────────────────────┐
│    Quality Scoring System       │
│                                 │
│  ├─► Relevance Score           │
│  ├─► Completeness Score        │
│  ├─► Quality Score (LLM)       │
│  ├─► Overall Score (weighted)  │
│  └─► Grade (A-F)               │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Structured Result JSON         │
│                                 │
│  ├─► Extracted Content          │
│  ├─► Quality Metrics            │
│  ├─► Performance Trace          │
│  └─► Metadata                   │
└─────────────────────────────────┘
```

## Module Dependencies

```
web_extractor.py (main)
    │
    ├─► config.py
    │   └─► .env (environment)
    │
    ├─► extractors/
    │   ├─► entity_extractor.py (Pattern matching)
    │   ├─► keyword_extractor.py (Keyword matching + scoring)
    │   └─► llm_extractor.py (LiteLLM client)
    │
    ├─► crawlers/
    │   └─► web_crawler.py
    │       ├─► robots.txt parsing
    │       └─► URL management
    │
    ├─► processors/
    │   └─► semantic_query_processor.py
    │       └─► Natural language query understanding
    │
    └─► utils/
        ├─► constants.py
        └─► logger.py
```

## Package Organization

```
src/
│
├─── Core Modules
│    ├─ web_extractor.py     (Main orchestrator)
│    ├─ config.py             (Configuration)
│    ├─ cli.py                (CLI interface)
│    ├─ app.py                (FastAPI application)
│    └─ api.py                (API endpoints)
│
├─── extractors/             (Extraction Layer)
│    ├─ __init__.py
│    ├─ entity_extractor.py   (Pattern-based NER)
│    ├─ keyword_extractor.py  (Keyword matching + scoring)
│    │   ├─► KeywordExtractor (Rule-based)
│    │   ├─► LLMKeywordExtractor (LLM-powered)
│    │   └─► HybridKeywordExtractor (Combined)
│    └─ llm_extractor.py      (LLM enhancement)
│        ├─► LLMEntityExtractor (LLM-powered)
│        └─► HybridEntityExtractor (Combined)
│
├─── crawlers/               (Crawling Layer)
│    ├─ __init__.py
│    └─ web_crawler.py        (Website crawler)
│
├─── processors/             (Processing Layer)
│    ├─ __init__.py
│    └─ semantic_query_processor.py (Natural language query understanding)
│
└─── utils/                  (Utilities)
     ├─ __init__.py
     ├─ constants.py          (Constants)
     └─ logger.py             (Logging)
```

## Execution Flow (CLI)

```
1. User runs: python -m src.cli --url example.com --keywords "AI" --use-llm
                │
                ▼
2. ArgumentParser processes command-line arguments
                │
                ▼
3. WebExtractionAgent initialized
                │
                ├─► Initialize rule-based extractors
                ├─► Initialize LLM extractors (if enabled)
                └─► Create hybrid extractors
                │
                ▼
4. Agent calls appropriate extraction method
                │
                ├─► extract_by_keywords() - Keyword-based
                ├─► extract_by_semantic_query() - Natural language
                └─► extract_from_site() - Site-wide crawling
                │
                ▼
5. Web content fetched and parsed
                │
                ├─► HTTP request with timeout
                ├─► BeautifulSoup parsing
                └─► Content cleaning
                │
                ▼
6. Hybrid extraction pipeline
                │
                ├─► Rule-based extraction
                │   ├─► Keyword matching
                │   └─► Pattern-based entities
                │
                ├─► LLM enhancement (if enabled)
                │   ├─► Semantic understanding
                │   ├─► Context enrichment
                │   └─► Additional entities
                │
                └─► Merge results
                │
                ▼
7. Quality scoring system
                │
                ├─► Calculate relevance score
                ├─► Calculate completeness score
                ├─► LLM quality assessment (if enabled)
                ├─► Compute overall score (weighted)
                └─► Assign grade (A-F)
                │
                ▼
8. Performance tracking
                │
                ├─► Fetch time
                ├─► Parse time
                ├─► Extraction time
                └─► Total duration
                │
                ▼
9. Output formatting and display
                │
                ├─► Quality metrics (grade, scores)
                ├─► Extracted content
                ├─► Performance trace
                └─► Save to JSON (if specified)
```

## Testing Architecture

```
tests/
│
├─── Unit Tests (isolated components)
│    ├─ test_entity_extractor.py
│    ├─ test_keyword_extractor.py
│    └─ test_web_extractor.py
│
├─── Integration Tests (component interaction)
│    ├─ test_extraction.py
│    └─ test_crawler.py
│
├─── End-to-End Tests
│    └─ test_full_suite.py
│
└─── Test Infrastructure
     └─ conftest.py (fixtures and configuration)
```

## Quality Scoring Pipeline

```
Raw Extraction Results
      │
      ├─► Relevance Score Calculation
      │   ├─ Keyword match frequency
      │   ├─ Match distribution
      │   └─ Context relevance
      │
      ├─► Completeness Score Calculation
      │   ├─ Content length
      │   ├─ Entities found
      │   ├─ Sections extracted
      │   └─ Coverage percentage
      │
      ├─► Quality Score (LLM Assessment)
      │   ├─ Semantic coherence
      │   ├─ Information value
      │   ├─ Context quality
      │   └─ Content reliability
      │
      ▼
Weighted Combination
      │
      ├─ Quality: 40%
      ├─ Relevance: 30%
      └─ Completeness: 30%
      │
      ▼
Overall Score (0.0-1.0)
      │
      ▼
Grade Assignment
      │
      ├─ A: 0.80-1.00 (Excellent)
      ├─ B: 0.65-0.80 (Good)
      ├─ C: 0.50-0.65 (Fair)
      ├─ D: 0.30-0.50 (Poor)
      └─ F: 0.00-0.30 (Failed)
      │
      ▼
Quality Assessment Message
      │
      └─► Actionable feedback
```

## Deployment Options

```
┌────────────────────────────────────────┐
│        Development                      │
│  python cli_keyword_extract.py         │
│  python -m src.cli                     │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│        Library Usage                    │
│  from src import WebExtractionAgent    │
│  agent = WebExtractionAgent()          │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│        REST API                         │
│  uvicorn src.app:app --reload          │
│  http://localhost:8000/docs            │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│        Package Installation             │
│  pip install -e .                      │
│  web-extractor --help                  │
└────────────────────────────────────────┘
```

## Configuration Hierarchy

```
Environment Variables (.env)
         │
         ▼
config.py (Defaults + env vars)
         │
         ▼
Application Code (Uses config)
         │
         ▼
Runtime Behavior
```

## Extension Points

Areas designed for easy extension:

1. **New Extractors**: Add to `src/extractors/`
   - Implement custom extraction logic
   - Add hybrid variants (rule-based + LLM)
   - Create specialized extractors for specific domains

2. **New Processors**: Add to `src/processors/`
   - Implement query understanding
   - Add semantic processing pipelines
   - Create domain-specific processors

3. **New Crawlers**: Add to `src/crawlers/`
   - Implement specialized crawling strategies
   - Add site-specific crawlers
   - Support different protocols

4. **Custom LLM Providers**: Extend `llm_extractor.py`
   - Add support for new LLM APIs
   - Implement custom prompting strategies
   - Create specialized LLM wrappers

5. **Quality Metrics**: Extend quality scoring
   - Add custom quality metrics
   - Implement domain-specific scoring
   - Create specialized assessment algorithms

6. **API Endpoints**: Add routes in `api.py`
   - Implement new extraction endpoints
   - Add batch processing endpoints
   - Create specialized API features

7. **CLI Commands**: Extend `cli.py`
   - Add new command-line options
   - Implement interactive features
   - Create specialized CLI workflows

## Key Features of New Architecture

### 🔄 Hybrid Extraction System
- **Rule-Based**: Fast, deterministic pattern matching
- **LLM-Enhanced**: Context-aware semantic understanding
- **Hybrid Mode**: Combines both for optimal results (recommended)
- **Automatic Fallback**: Gracefully handles LLM failures

### 📊 Comprehensive Quality Scoring
- **Multi-Dimensional Metrics**: Relevance, Quality, Completeness
- **A-F Grading System**: Instant quality assessment
- **Weighted Scoring**: Configurable metric weights
- **Actionable Feedback**: Clear quality improvement suggestions

### 🧠 Semantic Query Processing
- **Natural Language Queries**: "Find AI pricing information"
- **Intent Detection**: Understands query purpose
- **Strategy Selection**: Chooses optimal extraction strategy
- **Context-Aware**: Adapts to query requirements

### 🏗️ Modular Architecture
- **Organized Subdirectories**: extractors/, crawlers/, processors/
- **Clear Separation**: Each module has specific responsibility
- **Easy Testing**: Isolated components for unit tests
- **Flexible Integration**: Mix and match components

### ⚡ Performance Tracking
- **Detailed Traces**: Fetch, parse, extract timing
- **LLM Metrics**: Track LLM usage and performance
- **Quality Metrics**: Performance vs. quality tradeoffs
- **Error Handling**: Comprehensive error tracking

---

This architecture is designed to be:
- ✅ Modular and maintainable
- ✅ Easy to test and extend
- ✅ Production-ready with quality metrics
- ✅ Clear separation of concerns
- ✅ Industry-standard patterns
- ✅ Scalable and performant
- ✅ Flexible (rule-based or LLM-enhanced)
