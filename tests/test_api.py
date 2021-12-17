import os.path
import shutil
from dataclasses import asdict

import pytest
from hypothesis import given, settings
from hypothesis.strategies import from_regex
from fastapi.testclient import TestClient
from icecream import ic

from cells.cell_types import CellInfo
from main import app
from model import PlayerProfile, InitialPlacementRequest, CellPlacement, FindMatchRequest, MatchRequestData


@pytest.fixture(scope='module')
def client():
    if os.path.exists('./.db'):
        shutil.rmtree('./.db')
    client = TestClient(app)
    return client


@given(username=from_regex(r'^\w+\Z'))
@settings(max_examples=1)
def test_profile(username: str, client: TestClient):
    response = client.post(f'/profile/{username}')
    prof = PlayerProfile(**response.json())
    assert prof.username == username
    response = client.get(f'/profile')
    assert filter(
        lambda x: x.username == username and x.user_id == prof.user_id,
        [aprof for aprof in response.json()])


@given(username1=from_regex(r'^\w+\Z'), username2=from_regex(r'^\w+\Z'))
@settings(max_examples=1, deadline=None)
def test_create_match(username1: str, username2: str, client: TestClient):
    response = client.post(f'/profile/{username1}')
    prof = PlayerProfile(**response.json())
    user_id1 = prof.user_id
    assert prof.username == username1
    response = client.post(f'/profile/{username2}')
    prof = PlayerProfile(**response.json())
    user_id2 = prof.user_id
    assert prof.username == username2

    response = client.get(f'/profile')
    assert filter(
        lambda x: x.username == username1 and x.user_id == prof.user_id,
        [aprof for aprof in response.json()])
    assert filter(
        lambda x: x.username == username2 and x.user_id == prof.user_id,
        [aprof for aprof in response.json()])

    fmr1 = FindMatchRequest(user_id=user_id1, action_script_id=0)
    fmr2 = FindMatchRequest(user_id=user_id2, action_script_id=0)

    fmr1resp = client.post('/match', json=asdict(fmr1))
    md1 = MatchRequestData(**fmr1resp.json())
    fmr2resp = client.post('/match', json=asdict(fmr2))
    md2 = MatchRequestData(**fmr2resp.json())
    print(asdict(md1), asdict(md2))

    req1 = InitialPlacementRequest(
        user_id=user_id1,
        cell_placements=[CellPlacement(x_loc=i, y_loc=i, cell_type='ATTACK', team_number=0) for i in range(3)])


    req2 = InitialPlacementRequest(
        user_id=user_id2,
        cell_placements=[CellPlacement(x_loc=i, y_loc=i+1, cell_type='ATTACK', team_number=0) for i in range(3)])

    ic(asdict(req1))
    ic(asdict(req2))
    client.patch(f'/game/{md2.game_id}', json=asdict(req1))
    gresp = client.get(f'/game/{md2.game_id}')
    ic(gresp.json())
    p2resp = client.patch(f'/game/{md2.game_id}', json=asdict(req2))
    ic(p2resp.json())
    gresp = client.get(f'/game/{md2.game_id}')
    ic(gresp.json())
