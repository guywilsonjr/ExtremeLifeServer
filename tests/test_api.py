import os.path
import shutil
import pytest
from hypothesis import given
from hypothesis.strategies import from_regex
from fastapi.testclient import TestClient
from main import app
from model import PlayerProfile, InitialPlacementRequest


@pytest.fixture(scope='module')
def client():
    if os.path.exists('./.db'):
        shutil.rmtree('./.db')
    client = TestClient(app)
    return client


@given(username=from_regex(r'^\w+\Z'))
def test_profile(username: str, client: TestClient):
    response = client.post(f'/profile/{username}')
    prof = PlayerProfile(**response.json())
    assert prof.username == username
    response = client.get(f'/profile')
    assert filter(
        lambda x: x.username == username and x.user_id == prof.user_id,
        [aprof for aprof in response.json()])


@given(username1=from_regex(r'^\w+\Z'), username2=from_regex(r'^\w+\Z'))
def test_create_match(username1: str, username2: str, client: TestClient):
    response = client.post(f'/profile/{username1}')
    prof = PlayerProfile(**response.json())
    assert prof.username == username1

    response = client.post(f'/profile/{username2}')
    prof = PlayerProfile(**response.json())
    assert prof.username == username2

    response = client.get(f'/profile')
    assert filter(
        lambda x: x.username == username1 and x.user_id == prof.user_id,
        [aprof for aprof in response.json()])
    assert filter(
        lambda x: x.username == username2 and x.user_id == prof.user_id,
        [aprof for aprof in response.json()])
    req = InitialPlacementRequest()
    response = client.get(f'/')
