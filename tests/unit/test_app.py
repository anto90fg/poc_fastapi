from unittest.mock import patch
from fastapi_webserver.entrypoint import users_db  # Assicurati che il nome del file sia corretto

def test_login_success(mock_client):
    response = mock_client.post("/token", data={"username": "test_user", "password": "pass"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_failure(mock_client):
    response = mock_client.post("/token", data={"username": "test_user", "password": "wrong"})
    assert response.status_code == 401

def test_home_page(mock_client):
    response = mock_client.get("/")
    assert response.status_code == 200

def test_login_page(mock_client):
    response = mock_client.get("/login")
    assert response.status_code == 200

def test_retrieve_user_success(mock_client):
    access_token = users_db["test_user"]["access_token"]
    response = mock_client.get(f"/retrive_user/{access_token}")
    assert response.status_code == 200
    assert response.json()["username"] == "test_user"

def test_retrieve_user_failure(mock_client):
    response = mock_client.get("/retrive_user/invalidtoken")
    assert response.status_code == 404

def test_account_details_success(mock_client):
    response = mock_client.get("/account/test_user")
    assert response.status_code == 200

def test_account_details_failure(mock_client):
    response = mock_client.get("/account/unknown_user")
    assert response.status_code == 404

@patch("fastapi_webserver.entrypoint.write_notification")
def test_transfer_success(mock_write_notification, mock_client):
    response = mock_client.post("/transfer", data={
        "sender": "test_user", "receiver": "user1", "amount": 50.0
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully transferred $50.0 from test_user to user1"
    mock_write_notification.assert_called_once()

def test_transfer_insufficient_funds(mock_client):
    response = mock_client.post("/transfer", data={
        "sender": "test_user", "receiver": "user2", "amount": 1000.0
    })
    assert response.status_code == 400

def test_transfer_invalid_receiver(mock_client):
    response = mock_client.post("/transfer", data={
        "sender": "test_user", "receiver": "unknown", "amount": 50.0
    })
    assert response.status_code == 404

def test_transfer_same_user(mock_client):
    response = mock_client.post("/transfer", data={
        "sender": "test_user", "receiver": "test_user", "amount": 50.0
    })
    assert response.status_code == 400
