from fastapi.testclient import TestClient
import pytest
import sys
import os
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from main import app  

client = TestClient(app)

def test_basic_prediction():
    """Test basic prediction endpoint"""
    response = client.get("/api/prediction/AAPL/predict")
    
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        
        sections = [
            "overview",
            "strategy_performance",
            "baseline_comparison",
            "recent_performance",
            "technical_indicators",
            "clustering_visualization"
        ]
        for section in sections:
            assert section in data["data"]
        
        overview = data["data"]["overview"]
        assert all(key in overview for key in ["ticker", "analysis_period", "current_prediction"])
        assert all(key in overview["current_prediction"] for key in ["date", "signal", "confidence"])
        
        strategy_metrics = data["data"]["strategy_performance"]["metrics"]
        expected_metrics = ["sharpe_ratio", "annual_return", "win_rate", "max_drawdown", "total_trades"]
        assert all(metric in strategy_metrics for metric in expected_metrics)

def test_invalid_ticker_prediction():
    """Test error handling for invalid ticker"""
    response = client.get("/api/prediction/INVALID_TICKER_123/predict")
    
    assert response.status_code == 404
    error_data = response.json()
    assert "detail" in error_data
    assert "Could not find any data for ticker" in error_data["detail"]

def test_date_range_prediction():
    """Test prediction with custom date range"""
    response = client.get(
        "/api/prediction/AAPL/predict",
        params={
            "start_date": "2023-01-01",
            "end_date": "2023-12-31"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        assert data["data"]["overview"]["analysis_period"]["start"] == "2023-01-01"
        assert data["data"]["overview"]["analysis_period"]["end"] == "2023-12-31"

def test_clustering_parameters():
    """Test clustering parameters"""
    response = client.get(
        "/api/prediction/AAPL/predict",
        params={
            "n_clusters": 3,
            "min_cluster_size": 5
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        assert "clustering_visualization" in data["data"]
        assert data["data"]["clustering_visualization"] is not None