import requests
from fastapi.testclient import TestClient

from main import app
from controller import GameState, Controller



testun1 = 'test-user-1'



def test_sim():
    sim = Controller()
    empty_state = GameState(0, [])
    sim.print_state(empty_state)


def test_profile():
    client = TestClient(app)
    resp = client.post("/profile/test-user-1")
    data = resp.json()
    print(data)
    assert data['username'] == 'test-user-1'
    resp = client.get("/profile")
    profile_list = resp.json()
    print(profile_list)
    assert any(list(filter(lambda profile: profile['username'] == 'test-user-1', profile_list)))


