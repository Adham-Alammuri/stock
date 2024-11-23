from fastapi.testclient import TestClient
import pytest
import sys
import os
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from main import app 

client = TestClient(app)

def test_sentiment_analysis():
    """Test sentiment analysis endpoint"""
    response = client.get(
        "/api/sentiment/AAPL/analyze",
        headers={"X-API-KEY": "dummy-key"}
    )
    
    assert response.status_code in [200, 401, 429]
    
    if response.status_code == 200:
        data = response.json()
        assert "success" in data
        assert "data" in data
        sentiment_data = data["data"]
        assert all(key in sentiment_data for key in [
            "overall_sentiment",
            "sentiment_category",
            "news_count",
            "sentiment_trend"
        ])

def test_sentiment_without_api_key():
    """Test sentiment analysis without API key"""
    response = client.get("/api/sentiment/AAPL/analyze")
    assert response.status_code == 422
    error_data = response.json()
    assert "detail" in error_data