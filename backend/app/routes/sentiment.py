from fastapi import APIRouter, HTTPException
from app.services.sentiment_data import SentimentDataFetcher, SentimentProcessor
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/{ticker}/analyze")
async def analyze_sentiment(ticker: str):
    try:
        fetcher = SentimentDataFetcher()
        processor = SentimentProcessor(ticker)
        
        print(f"Fetching sentiment data for {ticker}")
        raw_data = fetcher.fetch_sentiment_data(ticker, days_back=30)
        
        # Check for rate limit response
        if 'Information' in raw_data and 'rate limit' in raw_data['Information'].lower():
            raise HTTPException(
                status_code=429,  # Too Many Requests status code
                detail="Alpha Vantage API rate limit reached. Please try again tomorrow or upgrade to a premium plan."
            )
        
        if not raw_data or 'feed' not in raw_data:
            print(f"No sentiment data available for {ticker}")
            return {
                "success": True,
                "data": {
                    "overall_sentiment": 0,
                    "sentiment_category": "No Data",
                    "news_count": 0,
                    "sentiment_trend": "Neutral",
                    "sentiment_history": {},
                    "sentiment_score_definition": {
                        "Bearish": "x <= -0.35",
                        "Somewhat-Bearish": "-0.35 < x <= -0.15",
                        "Neutral": "-0.15 < x < 0.15",
                        "Somewhat-Bullish": "0.15 <= x < 0.35",
                        "Bullish": "x >= 0.35"
                    }
                }
            }
        
        print("Processing sentiment data")
        processed_data = processor.process_raw_sentiment(raw_data)
        features = processor.prepare_features(processed_data)
        
        current_sentiment = features['weighted_sentiment'].iloc[-1]
        
        return {
            "success": True,
            "data": {
                "overall_sentiment": current_sentiment,
                "sentiment_category": get_sentiment_category(current_sentiment),
                "news_count": len(processed_data),
                "sentiment_trend": "Positive" if features['sentiment_momentum'].iloc[-1] > 0 else "Negative",
                "sentiment_history": features['weighted_sentiment'].tail(30).to_dict(),
                "sentiment_score_definition": {
                    "Bearish": "x <= -0.35",
                    "Somewhat-Bearish": "-0.35 < x <= -0.15",
                    "Neutral": "-0.15 < x < 0.15",
                    "Somewhat-Bullish": "0.15 <= x < 0.35",
                    "Bullish": "x >= 0.35"
                }
            }
        }

    except HTTPException as he:
        raise he  
    except Exception as e:
        print(f"Error in sentiment endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_sentiment_category(score):
    # Definitions from Alpha Vantage documentation
    if score <= -0.35:
        return "Bearish"
    elif -0.35 < score <= -0.15:
        return "Somewhat-Bearish"
    elif -0.15 < score < 0.15:
        return "Neutral"
    elif 0.15 <= score < 0.35:
        return "Somewhat-Bullish"
    else:
        return "Bullish"