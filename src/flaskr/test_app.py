import pytest
from flaskr.db import get_db
#from flaskr.conftest import app, client


def test_index(client, auth):
    response = client.get('/')
    assert b"Login" in response.data

@pytest.mark.parametrize('path', (
    '/verwaltung',
    '/dienstplan',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "/login"
