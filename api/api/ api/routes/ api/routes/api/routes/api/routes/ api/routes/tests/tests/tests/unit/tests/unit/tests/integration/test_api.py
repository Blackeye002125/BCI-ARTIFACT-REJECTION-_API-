"""
Integration tests for API endpoints.
"""

import pytest
import numpy as np
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "2.0.0"

def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "BCI Artifact Rejection API" in data["message"]

def test_process_endpoint(sample_request_data):
    """Test process endpoint."""
    response = client.post("/process/", json=sample_request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "cleaned_data" in data
    assert "artifacts_removed" in data

def test_model_status_endpoint():
    """Test model status endpoint."""
    response = client.get("/model/status")
    assert response.status_code == 200
    data = response.json()
    assert "model_type" in data
    assert "loaded" in data
