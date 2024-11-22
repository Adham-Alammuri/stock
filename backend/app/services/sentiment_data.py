import os
import requests
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class SentimentDataFetcher:
    """
    Fetches sentiment data from Alpha Vantage API.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE')
        if not self.api_key:
            raise ValueError("API key is required")
        
        self.base_url = 'https://www.alphavantage.co/query'

    def fetch_sentiment_data(self, ticker: str, days_back: int = 30) -> Dict[str, any]:
        """
        Fetches sentiment data for a specified ticker.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            days_back: Days of historical data to fetch

        Returns:
            Dictionary of news items with sentiment scores and analysis
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        params = {
            'function': 'NEWS_SENTIMENT',
            'tickers': ticker,
            'time_from': start_date.strftime('%Y%m%dT0000'),
            'limit': 1000,
            'apikey': self.api_key
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch sentiment data: {str(e)}")

class SentimentProcessor:
    """
    Processes raw sentiment data into structured format.
    """
    def __init__(self, ticker: str):
        self.ticker = ticker
    
    def process_raw_sentiment(self, raw_data: Dict) -> pd.DataFrame:
        """
        Converts raw API sentiment data into structured DataFrame.

        Args:
            raw_data: Raw sentiment data from Alpha Vantage API

        Returns:
            DataFrame with processed sentiment and topic metrics
        """
        processed_data = []

        for article in raw_data['feed']:
            timestamp = datetime.strptime(
                article['time_published'],
                '%Y%m%dT%H%M%S'
            )

            ticker_sentiment = next(
                (s for s in article['ticker_sentiment'] 
                 if s['ticker'] == self.ticker),
                None
            )

            if ticker_sentiment is None:
                continue

            topics = {
                topic['topic']: float(topic['relevance_score'])
                for topic in article['topics']
            }

            processed_data.append({
                'timestamp': timestamp,
                'date': timestamp.date(),
                'overall_sentiment': float(article['overall_sentiment_score']),
                'ticker_sentiment': float(ticker_sentiment['ticker_sentiment_score']),
                'relevance': float(ticker_sentiment['relevance_score']),
                'earnings_relevance': topics.get('Earnings', 0.0),
                'market_relevance': topics.get('Financial Markets', 0.0)
            })
            
        return pd.DataFrame(processed_data)
    
    def prepare_features(self, sentiment_data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepares features for sentiment analysis.

        Args:
            sentiment_data: Processed sentiment DataFrame

        Returns:
            DataFrame with momentum, volume, and sentiment features
        """
        daily_features = sentiment_data.groupby('date').agg({
            'overall_sentiment': ['mean', 'count'],
            'ticker_sentiment': ['mean', 'std'],
            'relevance': 'mean',
            'earnings_relevance': 'max',
            'market_relevance': 'max'
        }).reset_index()

        daily_features.columns = [
            'date', 'avg_sentiment', 'news_count',
            'ticker_sentiment', 'sentiment_std',
            'avg_relevance', 'earnings_importance',
            'market_importance'
        ]

        daily_features.set_index('date', inplace=True)
        features = pd.DataFrame(index=daily_features.index)
        
        # Sentiment momentum
        features['sentiment_ma3'] = daily_features['ticker_sentiment'].rolling(3).mean()
        features['sentiment_ma7'] = daily_features['ticker_sentiment'].rolling(7).mean()
        features['sentiment_momentum'] = features['sentiment_ma3'] - features['sentiment_ma7']
        
        # Volume features
        features['volume_ma3'] = daily_features['news_count'].rolling(3).mean()
        features['volume_ratio'] = (
            daily_features['news_count'] / 
            daily_features['news_count'].rolling(7).mean()
        )
        
        # Importance-weighted sentiment
        features['weighted_sentiment'] = (
            daily_features['ticker_sentiment'] * 
            (1 + daily_features['earnings_importance'] * 0.5)
        )
        
        return features