# Contributing to Web Extractor Agent

Thank you for your interest in contributing to Web Extractor Agent! This document provides guidelines and instructions for contributing.

## Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/web-extractor-agent.git
   cd web-extractor-agent
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e ".[dev]"  # Install in development mode with dev dependencies
   ```

4. **Set Up Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Code Style

We follow Python best practices and PEP 8 guidelines:

- Use **Black** for code formatting (line length: 100)
- Use **isort** for import sorting
- Use **flake8** for linting
- Use **mypy** for type checking

Run all formatters:
```bash
black src tests
isort src tests
flake8 src tests
mypy src
```

## Testing

We use **pytest** for testing. All new features should include tests.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_web_extractor.py

# Run with verbose output
pytest -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files as `test_*.py`
- Name test functions as `test_*`
- Use fixtures from `tests/conftest.py`
- Aim for high code coverage (>80%)

Example test:
```python
def test_extraction(sample_url):
    agent = WebExtractionAgent(use_llm=False)
    result = agent.extract_by_keywords(
        url=sample_url,
        keywords=['test']
    )
    assert 'title' in result
    assert result['trace']['duration_ms'] > 0
```

## Project Structure

```
web-extractor-agent/
├── src/                    # Source code
│   ├── __init__.py
│   ├── web_extractor.py   # Main agent
│   ├── config.py          # Configuration
│   ├── cli.py             # CLI interface
│   ├── extractors/        # Extractor modules
│   ├── crawlers/          # Crawler modules
│   ├── processors/        # Processor modules
│   └── utils/             # Utilities
├── tests/                 # Test files
├── examples/              # Usage examples
├── docs/                  # Documentation
└── scripts/               # Helper scripts
```

## Pull Request Process

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write clean, documented code
   - Add tests for new features
   - Update documentation as needed

3. **Run Tests and Linting**
   ```bash
   pytest
   black src tests
   flake8 src tests
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add awesome feature"
   ```
   
   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `test:` Test changes
   - `refactor:` Code refactoring
   - `style:` Formatting changes
   - `chore:` Maintenance tasks

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub.

## Areas for Contribution

We welcome contributions in these areas:

### 🐛 Bug Fixes
- Fix reported issues
- Improve error handling
- Enhance stability

### ✨ New Features
- New extraction methods
- Additional entity types
- Performance optimizations
- New LLM integrations

### 📚 Documentation
- Improve README
- Add more examples
- Write tutorials
- API documentation

### 🧪 Testing
- Add more test cases
- Improve test coverage
- Integration tests
- Performance tests

### 🎨 Code Quality
- Refactoring
- Type hints
- Better abstractions
- Performance improvements

## Reporting Issues

When reporting issues, please include:

1. **Description**: Clear description of the problem
2. **Steps to Reproduce**: Minimal steps to reproduce the issue
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**:
   - OS and version
   - Python version
   - Package versions
6. **Code Sample**: Minimal code that reproduces the issue

## Questions?

Feel free to:
- Open an issue for discussion
- Ask questions in pull requests
- Contact maintainers

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help others learn and grow

Thank you for contributing to Web Extractor Agent! 🎉
