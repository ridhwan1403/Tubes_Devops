import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home(client):
    """Test the home page."""
    response = client.get('/')
    assert response.status_code == 200

def test_login(client):
    """Test the login page."""
    response = client.get('/login?type=user')
    assert response.status_code == 200

def test_register(client):
    """Test the register page."""
    response = client.get('/register')
    assert response.status_code == 200

def test_logout(client):
    """Test the logout functionality."""
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome" in response.data  # Pastikan halaman home muncul setelah logout
