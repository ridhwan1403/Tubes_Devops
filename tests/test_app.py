# tests/test_app.py
import os
import pytest
from app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()
            
def test_invalid_api_key(client):
    """Test access with invalid API key."""
    response = client.get('/api/todos', headers={"X-API-KEY": "invalid_key"})
    assert response.status_code == 401
    assert b"Unauthorized" in response.data

def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome" in response.data

def test_register(client):
    """Test user registration."""
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 302  # Redirect after registration

def test_login(client):
    """Test user login."""
    # Register a user first
    client.post('/register', data={
        'username': 'testuser',
        'password': 'testpassword'
    })

    # Log in the user
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Your To-Do List" in response.data

def test_dashboard(client):
    """Test access to the dashboard."""
    # Register and log in a user
    client.post('/register', data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    })

    # Access the dashboard
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b"Your To-Do List" in response.data
