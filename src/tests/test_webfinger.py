import pytest
import falcon
from falcon import testing
from main import app 

from settings import DOMAIN

@pytest.fixture()
def client():
    return testing.TestClient(app)

def test_no_resource(client):
    response = client.simulate_get("/.well-known/webfinger")
    assert response.status == falcon.HTTP_400

def test_no_domain(client):
    response = client.simulate_get("/.well-known/webfinger", query_string=f"resource=@{DOMAIN}")
    assert response.status == falcon.HTTP_400

def test_no_acct(client):
    response = client.simulate_get("/.well-known/webfinger", query_string=f"resource=@{DOMAIN}")
    assert response.status == falcon.HTTP_400

def test_wrong_domain(client):
    response = client.simulate_get("/.well-known/webfinger", query_string=f"resource=@zinat.social")

def test_no_user(client):
    response = client.simulate_get("/.well-known/webfinger", query_string=f"resource=test200@{DOMAIN}")
    assert response.status == falcon.HTTP_404

def test_get_resource(client):
    "The ok case"

    response = client.simulate_get("/.well-known/webfinger", query_string=f'resource=@test@{DOMAIN}')  
    assert response.status == falcon.HTTP_200
