# Stock Analysis Dashboard

A full-stack web application that analyzes stock market data and generates trading signals using unsupervised machine learning clustering techniques. The application identifies market patterns through technical indicators and groups similar market conditions to generate trading signals.

## Features

- Machine Learning-Based Analysis:
  - K-means clustering of market conditions
  - Feature engineering using technical indicators
  - Automated trading signal generation based on cluster performance
  - Dynamic cluster analysis and performance metrics

- Technical Analysis:
  - RSI (Relative Strength Index)
  - Bollinger Bands
  - Volatility metrics (including Garman-Klass)
  - Momentum indicators
  - Volume analysis

- Additional Features:
  - Real-time stock data via yfinance
  - Sentiment analysis using Alpha Vantage API
  - Interactive charts and visualizations
  - Custom date range analysis
  - Performance metrics (Sharpe ratio, win rate, drawdown)

## Tech Stack

Frontend:
- React 18
- Vite
- TailwindCSS
- React Query v5
- Recharts for data visualization
- Lucide React for icons
- React DatePicker

Backend:
- FastAPI
- Python 3.12+
- pandas for data manipulation
- scikit-learn for machine learning
- yfinance for market data
- NumPy for numerical computations

## Live site example
Website: [Stock Analysis](https://stock.adhamalammuri.com/) 

## Getting Started


### Prerequisites
- Node.js (Latest LTS version)
- Python 3.12 or higher
- Alpha Vantage API key for sentiment analysis

### Installation

1. Clone the repository
```bash
git clone https://github.com/Adham-Alammuri/stock.git
```

2. Frontend setup
```bash
cd frontend
npm install
```

3. Backend setup
```bash
cd backend
pip install -r requirements.txt
```

4. Environment setup
```bash
# Create .env file in backend directory
ALPHA_VANTAGE=your_api_key_here
```

### Running Locally

1. Start the backend server:
```bash
cd backend
uvicorn main:app --reload
```

2. Start the frontend development server:
```bash
cd frontend
npm run dev
```

Visit `http://localhost:5173` in your browser.

## API Documentation

### Key Endpoints

- `/api/prediction/{ticker}/predict`
  - Returns trading signals based on clustering analysis
  - Parameters:
    - `ticker`: Stock symbol (e.g., AAPL)
    - `start_date` (optional): Analysis start date (YYYY-MM-DD)
    - `end_date` (optional): Analysis end date (YYYY-MM-DD)
    - `n_clusters` (optional): Number of clusters (2-10, default: 5)
    - `min_cluster_size` (optional): Minimum size per cluster (≥3, default: 5)
    - `lookback_window` (optional): Historical data window (≥60, default: 252)
  - Returns comprehensive analysis including:
    - Current trading signal (BUY/HOLD/SELL)
    - Strategy performance metrics
    - Technical indicators
    - Clustering visualization

- `/api/sentiment/{ticker}/analyze`
  - Provides sentiment analysis from news and social media
  - Headers required:
    - `X-API-KEY`: Alpha Vantage API key
  - Returns:
    - Overall sentiment score
    - News volume and trends
    - Sentiment category
    - Historical sentiment data

## Contact

Adham Alammuri
- LinkedIn: [Adham Alammuri](https://www.linkedin.com/in/adham-alammuri-38b684214)

## Notes

This is a portfolio project created for educational and demonstration purposes. The trading signals and analysis provided should not be used as financial advice.
