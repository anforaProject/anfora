import pytest
import falcon
import logging

from base64 import b64encode

from falcon import testing
from main import app 

@pytest.fixture()
def client():
    return testing.TestClient(app)

def test_missing_auth_header(client):
    params = {
        'username': 'test',
        'password': 'test'
    }
    response = client.simulate_get("/api/v1/auth", params=params)
    assert response.status == falcon.HTTP_401

def test_missing_user(client):
    params = {
        'username': 'noTest',
        'password': 'test'
    }

    data = b64encode(':'.join([params['username'],params['password']]).encode()).decode('utf8')

    headers = {
        'authorization': f'Basic {data}'
    }

    response = client.simulate_get("/api/v1/auth", params=params, headers=headers)
    assert response.status == falcon.HTTP_401

def test_wrong_password(client):
    params = {
        'username': 'test',
        'password': 'test2'
    }

    data = b64encode(':'.join([params['username'],params['password']]).encode()).decode('utf8')

    headers = {
        'authorization': f'Basic {data}'
    }

    response = client.simulate_get("/api/v1/auth", params=params, headers=headers)
    assert response.status == falcon.HTTP_401

def test_correct_auth(client):
    params = {
        'username': 'test',
        'password': 'test'
    }

    data = b64encode(':'.join([params['username'],params['password']]).encode()).decode('utf8')

    headers = {
        'authorization': f'Basic {data}'
    }

    response = client.simulate_get("/api/v1/auth", params=params, headers=headers)
    assert response.status == falcon.HTTP_200