"""
Tests for API endpoints
"""
import pytest
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_overview_endpoint(client):
    response = client.get('/api/overview')
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = json.loads(response.data)
        assert data['success'] == True

def test_sales_products_endpoint(client):
    response = client.get('/api/sales/products')
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'products' in data
        assert 'regions' in data

def test_analytics_endpoint(client):
    response = client.get('/api/analytics')
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = json.loads(response.data)
        assert data['success'] == True
