import pytest
import falcon
import logging

from falcon import testing
from main import app 


@pytest.fixture()
def client():
    return testing.TestClient(app)

def test_no_params(client):

    response = client.simulate_post("/api/v1/auth")
    assert response.status == falcon.HTTP_401