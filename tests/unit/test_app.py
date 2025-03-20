from unittest.mock import MagicMock, patch
from pyspark.sql import DataFrame
from fastapi_webserver.entrypoint import create_token
import pandas as pd

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
    token = create_token('test_user')
    response = mock_client.get(f"/retrive_user", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "test_user"

def test_retrieve_user_failure(mock_client):
    response = mock_client.get("/retrive_user", headers={"Authorization": f"Bearer fake_token"})
    assert response.status_code == 401

def test_account_details_success(mock_client):
    response = mock_client.get("/account/test_user")
    assert response.status_code == 200

def test_account_details_failure(mock_client):
    response = mock_client.get("/account/unknown_user")
    assert response.status_code == 404

@patch("fastapi_webserver.entrypoint.write_notification")
def test_transfer_success(mock_write_notification, mock_client):
    token = create_token("test_user")
    response = mock_client.post(
        "/transfer",
        data={"receiver": 'test_user_2', "amount": 50},
        headers={"Authorization": f"Bearer {token}"}
    )    
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully transferred $50.0 from test_user to test_user_2"
    mock_write_notification.assert_called_once()

def test_transfer_insufficient_funds(mock_client):
    token = create_token("test_user")
    response = mock_client.post(
        "/transfer", 
        data={"receiver": "test_user_2", "amount": 1000.0},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400

def test_transfer_invalid_receiver(mock_client):
    token = create_token("test_user")
    response = mock_client.post(
        "/transfer", 
        data={"receiver": "unknown", "amount": 50.0},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404

def test_transfer_same_user(mock_client):
    token = create_token("test_user")
    response = mock_client.post(
        "/transfer", 
        data={"receiver": "test_user", "amount": 50.0},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400


def test_analyze_today_success(mock_client):
    sender = "test_user"
    token = create_token(sender)
    headers = {"Authorization": f"Bearer {token}"}
    
    with patch("fastapi_webserver.entrypoint.spark") as mock_spark:
        df: DataFrame = MagicMock(spec=DataFrame)
        mock_spark.read.option.return_value.option.return_value.csv.return_value = df
        df.filter.return_value.describe.return_value.toPandas.return_value = pd.DataFrame({"summary": [{"metric": "count", "value": "5"}]})
        response = mock_client.post("/analyze", headers=headers)
        assert response.status_code == 200
        assert response.json()["username"] == sender
        assert "summary" in response.json()

def test_analyze_today_no_file(mock_client):
    sender = "test_user"
    token = create_token(sender)
    headers = {"Authorization": f"Bearer {token}"}
    
    with patch("fastapi_webserver.entrypoint.spark") as mock_spark:
        mock_spark.read.option.return_value.option.return_value.csv.side_effect = Exception("File not found")
        response = mock_client.post("/analyze", headers=headers)
        
        assert response.status_code == 200
        assert "details" in response.json()
        assert response.json()["details"] == 'File not found'

def test_analyze_today_unauthorized(mock_client):
    response = mock_client.post("/analyze")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"