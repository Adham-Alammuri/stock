from fastapi.testclient import TestClient
import pytest
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from main import app

client = TestClient(app)

def test_chart_endpoint_basic():
    """Test basic chart endpoint functionality with a known good ticker"""
    response = client.get("/api/visualization/AAPL/chart")
    
    print(f"Response Code: {response.status_code}")
    if response.status_code != 200:
        print(f"Error Response: {response.content}")
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] == True
    assert "data" in data
    assert "dates" in data["data"]
    assert "ohlc" in data["data"]
    assert "indicators" in data["data"]
    assert "volume" in data["data"]
    
    # Check indicator data structure
    indicators = data["data"]["indicators"]
    if "sma" in indicators:
        assert "sma20" in indicators["sma"]
        assert "sma50" in indicators["sma"]
    if "bb" in indicators:
        assert "upper" in indicators["bollinger"]
        assert "middle" in indicators["bollinger"]
        assert "lower:" in indicators["bollinger"]

def test_performance_endpoint():
    """Test performance endpoint functionality"""
    response = client.get("/api/visualization/AAPL/performance")
    
    print(f"Performance Response Code: {response.status_code}")
    if response.status_code != 200:
        print(f"Error Response: {response.content}")
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] == True
    assert "data" in data
    assert "metrics" in data["data"]
    
    metrics = data["data"]["metrics"]
    assert "returns" in metrics
    assert "sharpe" in metrics
    assert "win_rate" in metrics
    assert "max_drawdown" in metrics

def test_invalid_ticker():
    """Test error handling for invalid ticker"""
    response = client.get("/api/visualization/INVALID_TICKER_123/chart")
    assert response.status_code == 500
    
def test_chart_endpoint_date_range():
    """Test chart endpoint with specific date range"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    response = client.get(
        "/api/visualization/AAPL/chart",
        params={
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]["dates"]) > 0

def test_chart_types():
    """Test different chart types"""
    for chart_type in ["candlestick", "technical"]:
        response = client.get(
            "/api/visualization/AAPL/chart",
            params={"chart_type": chart_type}
        )
        assert response.status_code == 200
        
def test_different_indicators():
    """Test different indicator combinations"""
    indicators = ["sma,bb", "sma,rsi", "bb,rsi", "sma,bb,rsi"]
    for indicator_list in indicators:
        response = client.get(
            "/api/visualization/AAPL/chart",
            params={"indicators": indicator_list}
        )
        assert response.status_code == 200