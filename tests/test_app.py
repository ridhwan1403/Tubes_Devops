import pytest
import os
from app import app, db, User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['WTF_CSRF_ENABLED'] = False  # Nonaktifkan CSRF untuk pengujian
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome to the Home Page" in response.data  # Sesuaikan dengan konten halaman

def test_register(client):
    # Test pendaftaran pengguna baru
    response = client.post('/register', data={"username": "testuser", "password": "testpass"})
    assert response.status_code == 302  # Redirect ke halaman home
    assert User.query.filter_by(username="testuser").first() is not None

    # Test pendaftaran ulang pengguna yang sama
    response = client.post('/register', data={"username": "testuser", "password": "testpass"})
    assert response.status_code == 302  # Redirect karena error
    assert b"Username already exists!" in response.data
