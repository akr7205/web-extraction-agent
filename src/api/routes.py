"""FastAPI REST API server for the Web Extraction Agent."""
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
import uvicorn

from agent.web_extractor import create_agent

# Initialize FastAPI app
app = FastAPI(
    title="Keyword-Based Web Extraction API",
    description="Universal keyword-focused content extraction API - works like Perplexity. Extract relevant information from any web page by specifying keywords. Supports both URL fetching and direct HTML processing with optional LLM enhancement.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance (reused across requests)
agent = None


# Pydantic models for request/response validation
class EntityModel(BaseModel):
    """Extracted entity model."""
    name: str = Field(..., description="Entity name/text")
    type: str = Field(..., description="Entity type (COMPANY, PERSON, AMOUNT, DATE, etc.)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    source: str = Field(..., description="Extraction source (rule-based or llm)")


class TraceModel(BaseModel):
    """Processing trace model."""
    duration_ms: float = Field(..., description="Total processing time in milliseconds")
    fetch_ms: Optional[float] = Field(None, description="Fetch time in milliseconds")
    parse_ms: Optional[float] = Field(None, description="Parse time in milliseconds")
    extract_ms: Optional[float] = Field(None, description="Extraction time in milliseconds")
    errors: List[str] = Field(default_factory=list, description="List of errors encountered")
    warnings: List[str] = Field(default_factory=list, description="List of warnings")


class MetadataModel(BaseModel):
    """Extraction metadata model."""
    source_url: str = Field(..., description="Source URL")
    extraction_profile: str = Field(..., description="Profile used (news, filing, product)")
    timestamp: str = Field(..., description="Extraction timestamp")
    content_length: int = Field(..., description="Content length in characters")
    entity_count: int = Field(..., description="Number of entities extracted")


class ExtractionResultModel(BaseModel):
    """Complete extraction result model."""
    title: str = Field(..., description="Extracted page title")
    content: str = Field(..., description="Cleaned main content")
    entities: List[EntityModel] = Field(..., description="Extracted entities with confidence scores")
    metadata: MetadataModel = Field(..., description="Extraction metadata")
    trace: TraceModel = Field(..., description="Processing trace information")


class ExtractURLRequest(BaseModel):
    """Request model for URL extraction."""
    url: HttpUrl = Field(..., description="URL to extract from", examples=["https://example.com/article"])
    profile: str = Field(
        default="news",
        description="Extraction profile to use",
        pattern="^(news|filing|product)$"
    )


class ExtractHTMLRequest(BaseModel):
    """Request model for HTML extraction."""
    url: str = Field(..., description="URL to associate with the HTML", examples=["https://example.com"])
    html: str = Field(..., description="Raw HTML content to extract from")
    profile: str = Field(
        default="news",
        description="Extraction profile to use",
        pattern="^(news|filing|product)$"
    )


class ExtractKeywordsRequest(BaseModel):
    """Request model for keyword-based extraction."""
    url: HttpUrl = Field(..., description="URL to extract from", examples=["https://example.com/article"])
    keywords: List[str] = Field(..., description="Keywords to focus extraction on", min_length=1, examples=[["AI", "technology", "startup"]])
    use_llm: bool = Field(
        default=True,
        description="Whether to use LLM for enhanced keyword extraction"
    )


class ExtractKeywordsHTMLRequest(BaseModel):
    """Request model for keyword-based extraction from HTML."""
    url: str = Field(..., description="URL to associate with the HTML", examples=["https://example.com"])
    html: str = Field(..., description="Raw HTML content to extract from")
    keywords: List[str] = Field(..., description="Keywords to focus extraction on", min_length=1, examples=[["AI", "technology", "startup"]])
    use_llm: bool = Field(
        default=True,
        description="Whether to use LLM for enhanced keyword extraction"
    )


class ExtractSiteRequest(BaseModel):
    """Request model for site-wide extraction."""
    url: HttpUrl = Field(..., description="Starting URL to crawl from", examples=["https://example.com"])
    keywords: List[str] = Field(..., description="Keywords to focus extraction on", min_length=1, examples=[["AI", "technology", "startup"]])
    max_pages: int = Field(
        default=50,
        ge=1,
        le=200,
        description="Maximum number of pages to crawl (1-200)"
    )
    max_depth: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Maximum crawl depth (1-5)"
    )
    use_llm: bool = Field(
        default=True,
        description="Whether to use LLM for enhanced keyword extraction"
    )


class SiteExtractionSummaryModel(BaseModel):
    """Site extraction summary model."""
    total_pages: int = Field(..., description="Total pages extracted")
    avg_relevance: float = Field(..., description="Average relevance score")
    total_matches: int = Field(..., description="Total keyword matches")
    keywords_used: List[str] = Field(..., description="Keywords used for extraction")
    top_relevant_pages: List[Dict[str, Any]] = Field(..., description="Top most relevant pages")


class SiteExtractionResultModel(BaseModel):
    """Site-wide extraction result model."""
    start_url: str = Field(..., description="Starting URL that was crawled")
    total_pages_crawled: int = Field(..., description="Total pages discovered and crawled")
    successful_extractions: int = Field(..., description="Number of successful extractions")
    failed_extractions: int = Field(..., description="Number of failed extractions")
    keywords: List[str] = Field(..., description="Keywords used for extraction")
    extraction_profile: Optional[str] = Field(None, description="Extraction profile used (if any)")
    pages: List[Dict[str, Any]] = Field(..., description="Extraction results from each page")
    metadata: Dict[str, Any] = Field(..., description="Extraction metadata")
    summary: Dict[str, Any] = Field(..., description="Aggregated summary of results")


class KeywordExtractionModel(BaseModel):
    """Keyword extraction results model."""
    matched_sections: List[Dict[str, Any]] = Field(..., description="Sections matching the keywords")
    summary: str = Field(..., description="Summary of keyword-relevant content")
    relevance_score: float = Field(..., description="Overall relevance score")
    total_matches: int = Field(..., description="Total number of matches found")


class KeywordExtractionResultModel(BaseModel):
    """Complete keyword extraction result model."""
    title: str = Field(..., description="Extracted page title")
    keywords: List[str] = Field(..., description="Keywords used for extraction")
    keyword_extraction: KeywordExtractionModel = Field(..., description="Keyword-based extraction results")
    keyword_entities: Dict[str, List[str]] = Field(..., description="Entities found for each keyword")
    full_content: str = Field(..., description="Full cleaned content")
    llm_extraction: Optional[Dict[str, Any]] = Field(None, description="LLM extraction results if enabled")
    metadata: Dict[str, Any] = Field(..., description="Extraction metadata")
    trace: Dict[str, Any] = Field(..., description="Processing trace information")


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current server timestamp")
    agent_ready: bool = Field(..., description="Whether extraction agent is ready")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize the extraction agent on startup."""
    global agent
    agent = create_agent()
    print("🚀 Web Extraction Agent API started")
    print("📖 API documentation: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    global agent
    if agent:
        agent.close()
        agent = None
    print("👋 Web Extraction Agent API shutdown")


# API Endpoints
@app.get(
    "/",
    summary="Root endpoint",
    description="Returns basic API information and available endpoints"
)
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Keyword-Based Web Extraction API",
        "version": "2.0.0",
        "description": "Universal keyword-focused content extraction - works on any content type",
        "features": [
            "Keyword-based content extraction (primary)",
            "Site-wide extraction with crawling",
            "LLM-enhanced extraction (LiteLLM)",
            "Entity recognition and extraction",
            "Relevance scoring and ranking"
        ],
        "endpoints": {
            "health": "/health",
            "extract_by_keywords": "/extract/keywords (recommended)",
            "extract_by_keywords_html": "/extract/keywords/html",
            "extract_from_site": "/extract/site (NEW - crawl entire site)",
            "legacy_extract_url": "/api/v1/extract/url (legacy)",
            "legacy_extract_html": "/api/v1/extract/html (legacy)",
            "docs": "/docs"
        },
        "example": {
            "endpoint": "/extract/keywords",
            "method": "POST",
            "body": {
                "url": "https://example.com/article",
                "keywords": ["AI", "technology", "innovation"],
                "use_llm": True
            }
        },
        "site_extraction_example": {
            "endpoint": "/extract/site",
            "method": "POST",
            "body": {
                "url": "https://example.com",
                "keywords": ["AI", "technology"],
                "max_pages": 50,
                "max_depth": 3,
                "use_llm": True
            }
        }
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check if the API service is running and ready"
)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        timestamp=datetime.utcnow().isoformat(),
        agent_ready=agent is not None
    )


@app.post(
    "/api/v1/extract/url",
    response_model=ExtractionResultModel,
    summary="[LEGACY] Extract from URL",
    description="Legacy endpoint: Basic extraction without keyword focus. Use /extract/keywords instead for better results.",
    deprecated=True,
    responses={
        200: {"description": "Successful extraction"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Extraction failed"}
    },
    tags=["Legacy Endpoints"]
)
async def extract_from_url(request: ExtractURLRequest):
    """
    Extract structured data from a URL.
    
    This endpoint:
    1. Fetches the HTML content from the provided URL
    2. Parses and cleans the content
    3. Extracts entities using hybrid extraction (rule-based + optional LLM)
    4. Returns structured JSON with title, content, entities, and metadata
    
    Args:
        request: ExtractURLRequest with URL and profile
        
    Returns:
        ExtractionResultModel with extracted data
        
    Raises:
        HTTPException: If extraction fails
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Extraction agent not initialized")
    
    try:
        result = agent.extract(
            url=str(request.url),
            extraction_profile=request.profile
        )
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {str(e)}"
        )


@app.post(
    "/api/v1/extract/html",
    response_model=ExtractionResultModel,
    summary="[LEGACY] Extract from HTML",
    description="Legacy endpoint: Basic extraction without keyword focus. Use /extract/keywords/html instead for better results.",
    deprecated=True,
    responses={
        200: {"description": "Successful extraction"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Extraction failed"}
    },
    tags=["Legacy Endpoints"]
)
async def extract_from_html(request: ExtractHTMLRequest):
    """
    Extract structured data from HTML content.
    
    This endpoint:
    1. Parses the provided HTML content
    2. Cleans the content (removes boilerplate)
    3. Extracts entities using hybrid extraction
    4. Returns structured JSON with title, content, entities, and metadata
    
    Args:
        request: ExtractHTMLRequest with HTML content, URL, and profile
        
    Returns:
        ExtractionResultModel with extracted data
        
    Raises:
        HTTPException: If extraction fails
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Extraction agent not initialized")
    
    try:
        result = agent.extract(
            url=request.url,
            raw_html=request.html,
            extraction_profile=request.profile
        )
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {str(e)}"
        )


@app.get(
    "/api/v1/profiles",
    summary="[LEGACY] List extraction profiles",
    description="Get available extraction profiles for legacy endpoints. Note: Keyword extraction doesn't require profiles.",
    deprecated=True,
    tags=["Legacy Endpoints"]
)
async def list_profiles():
    """List available extraction profiles (for legacy endpoints only)."""
    return {
        "note": "Profiles are only used by legacy endpoints. The recommended /extract/keywords endpoint works on any content without profiles.",
        "profiles": [
            {
                "name": "news",
                "description": "Optimized for news articles",
                "entities": ["COMPANY", "PERSON", "AMOUNT", "DATE", "LOCATION", "ORGANIZATION"]
            },
            {
                "name": "filing",
                "description": "Optimized for financial filings and regulatory documents",
                "entities": ["COMPANY", "REGULATION", "AMOUNT", "DATE", "FILING_TYPE"]
            },
            {
                "name": "product",
                "description": "Optimized for product pages and e-commerce",
                "entities": ["PRODUCT", "PRICE", "BRAND", "FEATURE", "RATING"]
            }
        ]
    }


@app.post(
    "/extract/keywords",
    response_model=KeywordExtractionResultModel,
    summary="🎯 Extract by Keywords (Primary)",
    description="Universal keyword-based extraction that works on any content type - no profile needed. This is the recommended endpoint for all extractions.",
    responses={
        200: {"description": "Successful keyword extraction"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Extraction failed"}
    },
    tags=["Keyword Extraction (Primary)"]
)
async def extract_by_keywords(request: ExtractKeywordsRequest):
    """
    Extract content focused on specific keywords from a URL.
    Works universally on any content type - just like Perplexity.
    
    This is the PRIMARY and RECOMMENDED endpoint for all web extraction tasks.
    
    This endpoint:
    1. Fetches the HTML content from the provided URL
    2. Identifies sections relevant to the specified keywords
    3. Extracts entities associated with each keyword
    4. Optionally uses LLM (LiteLLM) for enhanced keyword-focused extraction
    5. Returns keyword-focused results with relevance scores
    
    Args:
        request: ExtractKeywordsRequest with URL, keywords, and LLM flag
        
    Returns:
        KeywordExtractionResultModel with keyword-focused extraction results
        
    Raises:
        HTTPException: If extraction fails
        
    Example:
        ```json
        {
            "url": "https://techcrunch.com/article",
            "keywords": ["AI", "startup", "funding", "technology"],
            "use_llm": true
        }
        ```
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Extraction agent not initialized")
    
    try:
        result = agent.extract_by_keywords(
            url=str(request.url),
            keywords=request.keywords,
            use_llm=request.use_llm
        )
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Keyword extraction failed: {str(e)}"
        )


@app.post(
    "/extract/keywords/html",
    response_model=KeywordExtractionResultModel,
    summary="🎯 Extract by Keywords from HTML",
    description="Universal keyword-based extraction from provided HTML content - ideal when you already have the HTML.",
    responses={
        200: {"description": "Successful keyword extraction"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Extraction failed"}
    },
    tags=["Keyword Extraction (Primary)"]
)
async def extract_by_keywords_html(request: ExtractKeywordsHTMLRequest):
    """
    Extract content focused on specific keywords from provided HTML.
    Works universally on any content type - just like Perplexity.
    
    Use this endpoint when you already have the HTML content and want to
    extract keyword-focused information without fetching from a URL.
    
    This endpoint:
    1. Parses the provided HTML content
    2. Identifies sections relevant to the specified keywords
    3. Extracts entities associated with each keyword
    4. Optionally uses LLM (LiteLLM) for enhanced keyword-focused extraction
    5. Returns keyword-focused results with relevance scores
    
    Args:
        request: ExtractKeywordsHTMLRequest with HTML, URL, keywords, and LLM flag
        
    Returns:
        KeywordExtractionResultModel with keyword-focused extraction results
        
    Raises:
        HTTPException: If extraction fails
        
    Example:
        ```json
        {
            "url": "https://example.com/article",
            "html": "<html><body>...</body></html>",
            "keywords": ["AI", "startup", "funding"],
            "use_llm": true
        }
        ```
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Extraction agent not initialized")
    
    try:
        result = agent.extract_by_keywords(
            url=request.url,
            raw_html=request.html,
            keywords=request.keywords,
            use_llm=request.use_llm
        )
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Keyword extraction failed: {str(e)}"
        )


@app.post(
    "/extract/site",
    response_model=SiteExtractionResultModel,
    summary="🕷️ Extract from Entire Site",
    description="Crawl and extract content from all pages of a website based on keywords. Discovers pages via sitemap and link crawling.",
    responses={
        200: {"description": "Successful site-wide extraction"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Extraction failed"}
    },
    tags=["Site-Wide Extraction"]
)
async def extract_from_site(request: ExtractSiteRequest):
    """
    Extract content from all pages of a website.
    
    This endpoint:
    1. Crawls the website starting from the provided URL
    2. Discovers pages via sitemap.xml and link following
    3. Extracts keyword-focused content from each page
    4. Aggregates results with relevance scoring
    5. Returns combined results with summary statistics
    
    Args:
        request: ExtractSiteRequest with URL, keywords, crawl settings, and LLM flag
        
    Returns:
        SiteExtractionResultModel with aggregated extraction results
        
    Raises:
        HTTPException: If extraction fails
        
    Example:
        ```json
        {
            "url": "https://example.com",
            "keywords": ["AI", "machine learning", "technology"],
            "max_pages": 50,
            "max_depth": 3,
            "use_llm": true
        }
        ```
        
    Note:
        - This operation may take several minutes depending on site size
        - Respects robots.txt
        - Only crawls pages on the same domain
        - Maximum limits: 200 pages, depth 5
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Extraction agent not initialized")
    
    try:
        result = agent.extract_from_site(
            start_url=str(request.url),
            keywords=request.keywords,
            max_pages=request.max_pages,
            max_depth=request.max_depth,
            use_llm=request.use_llm
        )
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Site extraction failed: {str(e)}"
        )


# Run server (for development)
def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """
    Run the FastAPI server.
    
    Args:
        host: Host to bind to (default: 0.0.0.0)
        port: Port to bind to (default: 8000)
        reload: Enable auto-reload for development (default: False)
    """
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    # Run the server when executed directly
    run_server(host="127.0.0.1", port=8000, reload=True)
