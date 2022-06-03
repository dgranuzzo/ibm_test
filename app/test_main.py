from fastapi.testclient import TestClient

from main import app
from messages import  * 

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"response": "try /url"}


def test_read_url():
    response = client.get("/url")
    assert response.status_code == 200
    assert {"response": "send your url via post"}


def test_search_bad_url():
    url_search = "jklgmgmg"
    response = client.post(
        "/url",
        json={"url": url_search},
    )
    assert response.status_code == 400
    assert response.json() == {"message": MSG_SERVICE_UNAVAILABLE,"status":577}


def test_search_url():
    url_search = "https://www.google.com"
    response = client.post(
        "/url",
        json={"url": url_search},
    )
    assert response.status_code == 200
    assert response.json()['status'] == 200