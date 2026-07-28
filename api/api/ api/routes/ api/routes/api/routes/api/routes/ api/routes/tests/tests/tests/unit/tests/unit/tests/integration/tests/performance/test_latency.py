"""
Performance tests for latency.
"""

import pytest
import time
import numpy as np
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

@pytest.mark.performance
def test_processing_latency(sample_request_data):
    """
    Test that processing latency is under 20ms.
    """
    response_times = []
    
    for _ in range(10):
        start_time = time.perf_counter()
        response = client.post("/process/", json=sample_request_data)
        end_time = time.perf_counter()
        
        elapsed_ms = (end_time - start_time) * 1000
        response_times.append(elapsed_ms)
        
        assert response.status_code == 200
    
    average_latency = np.mean(response_times)
    print(f"Average latency: {average_latency:.2f}ms")
    
    # Check if meets requirement
    assert average_latency < 20, f"Average latency {average_latency:.2f}ms exceeds 20ms limit"
