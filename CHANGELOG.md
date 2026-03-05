# Changelog

All notable changes to Web Extractor Agent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-23

### Added
- 🎉 Initial release of Web Extractor Agent
- ✨ Keyword-based extraction with relevance scoring
- ✨ LLM-enhanced semantic extraction
- ✨ Entity recognition (companies, people, dates, amounts)
- ✨ Site-wide crawling and extraction
- ✨ Quality scoring system with A-F grades
- ✨ Interactive CLI interface
- ✨ Command-line arguments support
- ✨ REST API with FastAPI
- ✨ Comprehensive test suite with pytest
- 📚 Full documentation and examples
- 📦 Proper Python package structure
- 🔧 Configuration via environment variables
- 🌐 Support for LiteLLM integration
- 📊 Detailed extraction metrics and tracing

### Project Structure
- Organized source code in `src/` directory
- Separated tests in `tests/` directory
- Added examples in `examples/` directory
- Created proper package structure with `__init__.py` files
- Added `setup.py` and `pyproject.toml` for packaging
- Included comprehensive documentation

### Features
- **Rule-based Extraction**: Fast, reliable pattern matching
- **LLM Enhancement**: AI-powered semantic understanding
- **Hybrid Mode**: Best of both worlds
- **Quality Metrics**: Overall score, relevance, completeness
- **Web Crawling**: Respect robots.txt, depth control
- **Flexible API**: Use as library or via CLI/REST API

### Documentation
- README with quick start guide
- API documentation
- Usage examples
- Contributing guidelines
- Health check report
- LiteLLM integration guide

## [Unreleased]

### Changed
- Improved extraction observability in `WebExtractionAgent` with lifecycle logs for initialization, extraction start/completion, keyword extraction, and fetch timing.
- Added safe log formatting helpers that sanitize URLs (drop query params/fragments) and limit logged keyword input to a short preview.
- Standardized short-content warnings to structured logging format for easier filtering in log pipelines.

### Planned Features
- [ ] Support for more LLM providers (OpenAI, Anthropic, etc.)
- [ ] Batch processing for multiple URLs
- [ ] Database integration for result storage
- [ ] Web UI dashboard
- [ ] Docker containerization
- [ ] Cloud deployment guides
- [ ] More entity types
- [ ] Advanced filtering options
- [ ] Export to multiple formats (CSV, Excel, etc.)
- [ ] Scheduled extractions
- [ ] Webhook notifications

### Future Improvements
- [ ] Performance optimizations
- [ ] Better error messages
- [ ] More comprehensive tests
- [ ] Internationalization support
- [ ] Plugin system for extensibility

---

## Version History

- **1.0.0** (2025-12-23): Initial release with core functionality
