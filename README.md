# Crypto Metrics Model Context Protocol (MCP)

A comprehensive framework for collecting and analyzing cryptocurrency metrics across multiple dimensions including market data, trading volume, social sentiment, and development activity.

## Features

- **Market Metrics**
  - Current price and market capitalization
  - Price trends and volatility analysis
  - Moving averages and anomaly detection

- **Volume Metrics**
  - Trading volume analysis
  - Exchange distribution metrics
  - Volume concentration indicators

- **Social Metrics**
  - Social media sentiment analysis
  - Community engagement tracking
  - Cross-platform social metrics

- **Development Metrics**
  - GitHub repository analytics
  - Development velocity metrics
  - Code impact analysis

## Installation

```bash
# Clone the repository
git clone https://github.com/liorshop/crypto-mcp-metrics.git
cd crypto-mcp-metrics

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Unix/macOS
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root with your API keys:

```env
COINGECKO_API_KEY=your_coingecko_api_key
COINMARKETCAP_API_KEY=your_coinmarketcap_api_key
SOCIAL_SEARCHER_API_KEY=your_social_searcher_api_key
GITHUB_TOKEN=your_github_personal_access_token
```

## Usage

### Command Line

```bash
# Collect metrics for a specific cryptocurrency
python main.py bitcoin

# Save results to a file
python main.py ethereum -o ethereum_metrics.json
```

### Python API

```python
import asyncio
from main import CryptoMetricsCollector

async def collect_metrics():
    async with CryptoMetricsCollector() as collector:
        metrics = await collector.collect_all_metrics('bitcoin')
        print(metrics)

asyncio.run(collect_metrics())
```

## Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Run with coverage
pytest --cov=metrics tests/
```

## Project Structure

```
crypto-mcp-metrics/
├── config.py                  # Configuration management
├── requirements.txt          # Project dependencies
├── metrics/
│   ├── market_metrics.py     # Market data collection
│   ├── volume_metrics.py     # Volume analysis
│   ├── social_metrics.py     # Social metrics
│   └── dev_metrics.py        # Development metrics
├── core/
│   ├── api_handler.py        # API interaction
│   └── data_processor.py     # Data processing
├── utils/
│   ├── logging.py           # Logging setup
│   └── error_handler.py      # Error handling
└── tests/
    ├── unit/                # Unit tests
    └── integration/         # Integration tests
```

## API Responses

### Market Metrics
```json
{
  "current_metrics": {
    "price": 50000,
    "market_cap": 1000000000,
    "volume_24h": 5000000
  },
  "trend_metrics": {
    "price_trend": 5.2,
    "volatility": 0.15
  }
}
```

### Volume Metrics
```json
{
  "current_metrics": {
    "current_volume": 5000000,
    "vs_average": 10.5
  },
  "exchange_metrics": {
    "distribution": {
      "Binance": 45.5,
      "Coinbase": 35.2
    }
  }
}
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Project Link: [https://github.com/liorshop/crypto-mcp-metrics](https://github.com/liorshop/crypto-mcp-metrics)