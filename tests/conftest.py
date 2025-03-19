import pytest
from fastapi.testclient import TestClient
from fastapi_webserver.entrypoint import app

@pytest.fixture(scope='session')
def mock_client():
    client = TestClient(app)
    yield client