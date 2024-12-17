# Synthetic Portfolio Manager (SPM)

SPM is an autonomous financial analysis system that combines market data collection, LLM-driven analysis, and Bayesian-like updating to provide comprehensive market insights.

## Current Status: Iteration 0

Currently implementing foundational data infrastructure with a focus on:
- Robust data collection from multiple sources
- Standardized data processing and storage
- Comprehensive testing and error handling

## Features

### Implemented
- Modular data fetching framework
- Support for Binance spot and futures markets
- Standardized data processing pipeline
- Efficient caching system with metadata
- Comprehensive logging system

### Planned
- Coinglass integration
- LLM-driven analysis via OpenRouter
- Bayesian-like updating system
- Vector database for historical context
- Cost-aware query optimization

## Installation

1. Clone the repository:
```bash
git clone https://github.com/qeinfinity/spm.git
cd spm
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up configuration:
```bash
cp synthetic_portfolio_manager/config/config.example.yaml synthetic_portfolio_manager/config/config.yaml
# Edit config.yaml with your API keys and preferences
```

## Usage

Basic usage:
```bash
python -m synthetic_portfolio_manager.main --symbol BTCUSDT --market-type spot
```

Options:
- `--config`: Path to configuration file (default: config/config.yaml)
- `--log-level`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `--symbol`: Trading symbol to fetch data for (default: BTCUSDT)
- `--market-type`: Market type to fetch data from (spot or futures)

## Project Structure

```
synthetic_portfolio_manager/
├── config/              # Configuration files
├── scripts/             # Core implementation
│   ├── base/           # Base classes
│   ├── binance/        # Binance integration
│   └── ...             # Other integrations
├── tests/              # Test suite
├── utilities/          # Utility functions
└── main.py            # Application entry point
```

## Development

### Setting Up Development Environment

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

2. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

### Running Tests

Run the full test suite:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=synthetic_portfolio_manager
```

### Code Standards

- Use type hints
- Write comprehensive docstrings
- Follow modular design principles
- Implement proper error handling
- Include tests for new functionality

## Configuration

See `config/config.example.yaml` for detailed configuration options including:
- API credentials
- Rate limits
- Logging settings
- Cache configuration
- Data collection parameters

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests
5. Submit a pull request

Please ensure your changes:
- Follow the established code style
- Include appropriate tests
- Update documentation as needed
- Pass all existing tests

## Error Handling

The system implements comprehensive error handling:
- API failures are retried with exponential backoff
- Rate limiting is handled automatically
- Data validation ensures consistency
- All errors are properly logged

## Caching System

Data is cached in a structured way:
- Raw API responses preserved for auditing
- Processed data stored in standardized format
- Automatic cleanup of old cache files
- Metadata tracking for all cached data

## Logging

Logging is implemented throughout:
- Rotating file logs with size limits
- Console output for development
- Different log levels for flexibility
- Structured log format for parsing

## Future Development

Upcoming features in next iterations:
1. Integration with Coinglass API
2. LLM-driven market analysis
3. Bayesian probability updates
4. Enhanced data visualization
5. Performance optimizations

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Binance API Documentation
- OpenRouter Documentation
- Project contributors

## Support

For support:
1. Check existing documentation
2. Search GitHub issues
3. Open a new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior

## Changelog

See CHANGELOG.md for detailed version history.