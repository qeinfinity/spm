# Contributing to SPM

Thank you for your interest in contributing to the Synthetic Portfolio Manager (SPM) project! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include as many details as possible:

- Clear and descriptive title
- Exact steps to reproduce the issue
- Expected vs actual behavior
- Code samples or error messages
- Environment details (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- Clear and descriptive title
- Detailed explanation of the proposed feature
- Examples of how it would be used
- Why this enhancement would be useful

### Pull Requests

1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes
4. Add or update tests as needed
5. Update documentation if required
6. Ensure all tests pass
7. Submit a pull request

## Development Process

### Setting Up Development Environment

1. Clone your fork:
```bash
git clone https://github.com/your-username/spm.git
cd spm
```

2. Set up virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write comprehensive docstrings
- Keep functions focused and modular
- Use meaningful variable names

### Testing

- Write tests for new functionality
- Ensure all tests pass:
```bash
pytest
```
- Check code coverage:
```bash
pytest --cov=synthetic_portfolio_manager
```

### Documentation

- Update docstrings for modified code
- Update README.md if needed
- Add notes to CHANGELOG.md
- Include examples for new features

## Project Structure

Understand where different components belong:

- `config/`: Configuration files
- `scripts/`: Core implementation
  - `base/`: Base classes
  - `binance/`: Binance integration
- `tests/`: Test suite
- `utilities/`: Helper functions

## Questions?

Feel free to open an issue for:
- Questions about contributing
- Clarification on development process
- Technical questions

Thank you for contributing to SPM!