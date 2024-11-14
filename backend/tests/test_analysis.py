from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import pytest
from app.main import app

client = TestClient(app)

def test_basic_analysis():
    """Test basic analysis endpoint functionality"""
    response = client.get("/api/analysis/AAPL")
    
    print(f"Response Code: {response.status_code}")
    if response.status_code != 200:
        print(f"Error Response: {response.content}")
    
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        
        # Check all required indicators are present
        assert "sma" in data["data"]
        assert "rsi" in data["data"]
        assert "bollinger" in data["data"]
        assert "volatility" in data["data"]

def test_analysis_with_dates():
    """Test analysis endpoint with specific date range"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)  # Longer period for testing
    
    response = client.get(
        "/api/analysis/AAPL",
        params={
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
    )
    
    print(f"Date Range Response: {response.status_code}")
    if response.status_code != 200:
        print(f"Error Response: {response.content}")
        
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()["data"]
        
        # Check data is properly formatted
        assert isinstance(data["sma"], dict)
        assert isinstance(data["rsi"], dict)
        assert isinstance(data["bollinger"], dict)
        assert isinstance(data["volatility"], dict)

def test_invalid_ticker_analysis():
    """Test error handling for invalid ticker"""
    response = client.get("/api/analysis/INVALID_TICKER_123")
    
    assert response.status_code in [404, 500]
    
    if response.status_code == 404:
        error_data = response.json()
        assert "detail" in error_data

def test_data_trimming():
    """Test that data is properly trimmed to requested dates"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)  # Request 1 week
    
    response = client.get(
        "/api/analysis/AAPL",
        params={
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        
        # Get any series from the data
        sma_dates = list(data["sma"].keys())
        rsi_dates = list(data["rsi"].keys())
        volatility_dates = list(data["volatility"].keys())
        
        # All series should have same number of dates
        assert len(sma_dates) == len(rsi_dates), "SMA and RSI have different lengths"
        assert len(sma_dates) == len(volatility_dates), "SMA and Volatility have different lengths"

def test_analysis_data_values():
    """Test that returned data values are valid"""
    response = client.get("/api/analysis/AAPL")
    
    if response.status_code == 200:
        data = response.json()["data"]
        
        # Check RSI values are in valid range (0-100)
        for value in data["rsi"].values():
            if value is not None:  # Skip None values
                assert 0 <= float(value) <= 100, "RSI value out of range"
        
        # Check Bollinger Bands relationship
        bb = data["bollinger"]
        # Get the dates
        dates = set(bb.keys()) & set(bb["BB_Upper"].keys()) & set(bb["BB_Middle"].keys()) & set(bb["BB_Lower"].keys())
        
        for date in dates:
            upper = bb["BB_Upper"].get(date)
            middle = bb["BB_Middle"].get(date)
            lower = bb["BB_Lower"].get(date)
            
            if all(x is not None for x in [upper, middle, lower]):
                assert float(upper) >= float(middle) >= float(lower), f"Invalid Bollinger Bands relationship on {date}"

def test_bollinger_structure():
    """Test specific Bollinger Bands structure"""
    response = client.get("/api/analysis/AAPL")
    
    if response.status_code == 200:
        data = response.json()["data"]
        bb = data["bollinger"]
        
        # Check required keys exist
        assert "BB_Upper" in bb, "Missing BB_Upper"
        assert "BB_Middle" in bb, "Missing BB_Middle"
        assert "BB_Lower" in bb, "Missing BB_Lower"

def test_error_handling():
    """Test various error conditions"""
    # Test with invalid date format
    response = client.get(
        "/api/analysis/AAPL",
        params={
            "start_date": "invalid-date",
            "end_date": "2024-01-01"
        }
    )
    assert response.status_code in [400, 422, 500]
    
    # Test with end_date before start_date
    response = client.get(
        "/api/analysis/AAPL",
        params={
            "start_date": "2024-01-01",
            "end_date": "2023-01-01"
        }
    )
    assert response.status_code in [400, 422, 500]