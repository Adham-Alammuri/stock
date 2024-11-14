from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import pytest
from app.main import app

client = TestClient(app)

def test_basic_prediction():
    """Test basic prediction endpoint"""
    response = client.get("/api/prediction/AAPL/predict")
    
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        assert "predictions" in data["data"]
        assert "evaluation" in data["data"]

def test_cluster_parameters():
    """Test different clustering parameters"""
    response = client.get(
        "/api/prediction/AAPL/predict",
        params={"n_clusters": 3}
    )
    
    if response.status_code == 200:
        data = response.json()
        assert data["data"]["cluster_info"]["n_clusters"] == 3