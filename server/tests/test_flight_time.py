import pytest
import sys
import os
import time
import json
from unittest.mock import patch
from pymongo import MongoClient
from flask import template_rendered
from contextlib import contextmanager

sys.path.append('../')
from app import create_app
from db import select_insurance_amount
from dotenv import load_dotenv
from config import TestingConfig
load_dotenv()

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app(TestingConfig)
    return app

@pytest.fixture
def client(app):
    """Create a test client for the Flask app."""
    with app.test_client() as client:
        yield client

@contextmanager
def captured_templates(app):
    recorded = []
    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)

@pytest.fixture
def database():
    print("Setting up the database...")
    client = MongoClient(os.getenv("MONGODB_URI_TEST"))
    db = client.test_db
    yield db
    print("Cleaning up the database...")

def test_depart_flight_time_success(client):
    with captured_templates(client.application) as templates:
        response = client.post('/depart_flight_time', data={
            'airline': 'UA',
            'flight_number': '123'
        }, follow_redirects=True)
        assert response.status_code == 200
    

def test_index_page(client):
    """測試首頁"""
    response = client.get('/')  
    assert response.status_code == 200
    
    
    
@patch('db.select_insurance_amount')
def test_fetch_insurance_amount_success(mock_select_insurance, client):
    response = client.post('/fetch_insurance_amount', data={
        'insuranceCompany': 'fubung',
        'plan': 'S方案',
        'insuranceAmount': '300',
        'insuranceDays': '4'
    })
    
    # Assert the response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['data']['insurance_price'] == 313
