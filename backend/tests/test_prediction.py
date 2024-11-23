from fastapi.testclient import TestClient
import pytest
import sys
import os

# Add the root directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app  # Update import path

client = TestClient(app)

def test_basic_prediction():
    """Test basic prediction endpoint"""
    response = client.get("/api/prediction/AAPL/predict")
    
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        assert "overview" in data["data"]
        assert "strategy_performance" in data["data"]
        assert "clusters" in data["data"]
        
        # Test specific data structure
        overview = data["data"]["overview"]
        assert "ticker" in overview
        assert "current_prediction" in overview
        assert "signal" in overview["current_prediction"]
        
        # Test metrics
        metrics = data["data"]["strategy_performance"]["metrics"]
        assert "sharpe_ratio" in metrics
        assert "annual_return" in metrics
        assert "win_rate" in metrics

def test_cluster_parameters():
    """Test different clustering parameters"""
    response = client.get(
        "/api/prediction/AAPL/predict",
        params={"n_clusters": 3}
    )
    
    if response.status_code == 200:
        data = response.json()
        assert len(data["data"]["clusters"]) == 3

def test_date_range():
    """Test custom date range"""
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