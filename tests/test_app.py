import pytest
import os
from app import app, db, User

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

def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json['message'] == "Welcome to the API!"

def test_register(client):
    response = client.post('/register', json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert response.json['message'] == "User registered successfully!"

    # Test duplicate user registration
    response = client.post('/register', json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 400
    assert response.json['message'] == "Username already exists"
