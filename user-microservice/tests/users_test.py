import pytest
from starlette.testclient import TestClient

from src.server import app

client = TestClient(app)

import os

import pytest

from tortoise.contrib.test import finalizer, initializer


@pytest.fixture(scope="session", autouse=True)
def initialize_tests(request):
    db_url = os.environ.get("TORTOISE_TEST_DB", "sqlite://:memory:")
    initializer(["src.db"], db_url=db_url)
    request.addfinalizer(finalizer)


@pytest.fixture
def set_test_env(monkeypatch):
    monkeypatch.setenv("ENV", "testing")


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200

def test_new_user(set_test_env):

    data = {
        "username": "testing2",
        "password": "testing",
        "password_confirmation": "testing",
        "email": "testing2@example.com"
    }
    
    response = client.post(
        "/api/v1/accounts/create",
        json = data,
        headers = {
            'Content-Type': "application/json",
            'cache-con1trol': "no-cache",
        }
    )
    assert response.status_code == 200
