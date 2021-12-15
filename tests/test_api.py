import json
from io import BytesIO

from hypothesis import given, assume
from hypothesis.strategies import text, from_regex
from fastapi.testclient import TestClient
from main import app
client = TestClient(app)

from model import PlayerProfile


@given(from_regex(r'^\w+\Z'))
def test_profile(username: str):
    response = client.post(f'/profile/{username}')
    print(response.content)
    prof = PlayerProfile(**response.json())
    print(prof)
    assert prof.username == username
    response = client.get(f'/profile')
    assert filter(lambda x: x.username == username and x.user_id == prof.user_id ,[aprof for aprof in response.json()])


