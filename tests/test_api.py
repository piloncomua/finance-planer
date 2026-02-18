"""
API tests for Flask application
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
import json

def test_api_calculate():
    """Test /api/calculate endpoint"""
    client = app.test_client()
    
    data = {
        'initial_capital': 1600000,
        'monthly_income': 25000,
        'monthly_expenses': 0,
        'interest_rate': 8,
        'inflation_rate': 2,
        'current_age': 35,
        'retirement_age': 45,
        'max_age': 90
    }
    
    response = client.post('/api/calculate',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 200
    result = json.loads(response.data)
    
    assert 'success' in result
    assert result['success'] == True
    assert 'data' in result
    assert len(result['data']) > 0

def test_api_validation():
    """Test API validation"""
    client = app.test_client()
    
    # Missing required field
    data = {
        'initial_capital': 1000000,
        'monthly_income': 10000
        # Missing other required fields
    }
    
    response = client.post('/api/calculate',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 400
    result = json.loads(response.data)
    assert 'error' in result

def test_api_invalid_ages():
    """Test API with invalid age parameters"""
    client = app.test_client()
    
    data = {
        'initial_capital': 1000000,
        'monthly_income': 10000,
        'monthly_expenses': 5000,
        'interest_rate': 8,
        'inflation_rate': 2,
        'current_age': 50,
        'retirement_age': 40,  # Invalid: retirement < current
        'max_age': 90
    }
    
    response = client.post('/api/calculate',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 400
    result = json.loads(response.data)
    assert 'error' in result

if __name__ == '__main__':
    test_api_calculate()
    test_api_validation()
    test_api_invalid_ages()
    print("✅ All API tests passed!")
