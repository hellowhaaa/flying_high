
import pytest
import sys
import os
import time
from pymongo import MongoClient
from werkzeug.security import generate_password_hash

sys.path.append('../')
from app import create_app
from dotenv import load_dotenv
from config import TestingConfig
load_dotenv()

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app(TestingConfig)
    # app.config.update({
    #     "TESTING": True,
    #     "WTF_CSRF_ENABLED": False, 
    #     "DATABASE_URI": os.getenv("MONGODB_URI_TEST"),
    # })
    return app

@pytest.fixture
def client(app):
    print("Creating test client.")
    return app.test_client()

@pytest.fixture
def database():
    print("Setting up the database...")
    client = MongoClient(os.getenv("MONGODB_URI_TEST"))
    db = client.test_db
    test_user = {
        "username": "testuser",
        "password_hash": generate_password_hash("correctpassword"),
        "email": "test@example.com",
        "address": "123 New St"
    }
    db.users.insert_one(test_user)

    yield db

    
    print("Cleaning up the test user from the database...")
    db.users.delete_one({"username": test_user['username']})


def test_user_registration(client, database):
    username = f"newuser_{int(time.time())}"  # 使用基于时间的唯一用户名
    new_user = {
        "username": username,
        "password": "newpassword",
        "email": f"{username}@example.com",
        "address": "123 New St"
    }
    response = client.post('/user/sign_up', data=new_user, follow_redirects=True)
    assert response.status_code == 200
    cookies = response.headers.get('Set-Cookie', '')
    assert 'access_token' in cookies, f"Expected 'access_token' in cookies, got {cookies}"

    try:
        delete_result = database.user.delete_one({"username": username})
        print(f"Attempting to delete user '{username}'. Deleted count: {delete_result.deleted_count}")
    except Exception as e:
        print(f"Error when trying to delete user: {e}")


def test_login_success(client, database):
    """Test successful login."""
    response = client.post('/user/log_in', data={
        'username': 'testuser',
        'password': 'correctpassword'
    }, follow_redirects=True)
    assert response.status_code == 200


def test_login_failure(client, database):
    """Test login with wrong credentials."""
    response = client.post('/user/log_in', data={
        'username': 'testuser',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert response.status_code == 200