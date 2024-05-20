
import pytest
import sys
import os
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
def setup_database():
    print("Setting up the database...")
    client = MongoClient(os.getenv("MONGODB_URI_TEST"))
    db = client.test_db
    try:
        result = db.command("ping")
        print("Ping result:", result)
    except Exception as e:
        print("Failed to connect to the database:", e)
        raise
    db.users.insert_one({
        "username": "testuser",
        "password_hash": generate_password_hash("correctpassword"),
        "email": "test@example.com"
    })
    yield
    # print("Cleaning up the database...")
    # db.users.delete_many({})


def test_user_registration(client, setup_database):
    new_user = {
        "username": "newuser",
        "password": "newpassword",
        "email": "newuser@example.com",
        "address": "123 New St"
    }
    response = client.post('/user/sign_up', data=new_user, follow_redirects=True)
    assert response.status_code == 200
    cookies = response.headers.get('Set-Cookie', '')
    print(f"Cookies after redirect: {cookies}")
    assert 'access_token' in cookies, f"Expected 'access_token' in cookies, got {cookies}"



# def test_login_success(client, setup_database):
#     """Test successful login."""
#     response = client.post('/user/log_in', data={
#         'username': 'testuser',
#         'password': 'correctpassword'
#     }, follow_redirects=True)
#     assert response.status_code == 200

# def test_login_failure(client, setup_database):
#     """Test login with wrong credentials."""
#     response = client.post('/user/log_in', data={
#         'username': 'testuser',
#         'password': 'wrongpassword'
#     }, follow_redirects=True)
#     assert response.status_code == 200