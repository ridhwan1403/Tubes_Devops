import pytest
import os
from app import app, db, User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'<title>Home</title>' in response.data  # Check if the HTML contains the expected title

def test_register(client):
    # Test user registration
    response = client.post('/register', data={"username": "testuser", "password": "testpass"})
    assert response.status_code == 302  # Should redirect to the home page
    assert User.query.filter_by(username="testuser").first() is not None

    # Test duplicate registration
    response = client.post('/register', data={"username": "testuser", "password": "testpass"})
    assert response.status_code == 302  # Should redirect to the registration page
    follow_response = client.get(response.location)  # Follow the redirect
    assert b"Username already exists!" in follow_response.data  # Check for the error message
