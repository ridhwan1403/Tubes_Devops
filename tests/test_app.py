# tests/test_app.py
import os
import pytest
from app import app, db

@pytest.fixture
def client():
    # Set up the Flask test client and initialize the database
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:password@127.0.0.1:3306/tubes_devsecop_app'
    app.config['SECRET_KEY'] = 'test_secret_key'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

        # Tear down database
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_invalid_api_key(client):
    """Test access with invalid API key."""
    response = client.get('/api/todos', headers={"X-API-KEY": "invalid_key"})
    assert response.status_code == 401
    assert b"Unauthorized" in response.data

def test_home_route():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome" in response.data

def test_home_page(client):
    """Test if the home page is accessible."""
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
    # First register a user
    client.post('/register', data={
        'username': 'testuser',
        'password': 'testpassword'
    })

    # Then log in
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
