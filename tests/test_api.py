import os.path
import random
import shutil
import time
from dataclasses import asdict
from typing import Tuple, List, Dict

import pytest
from hypothesis import given, settings
from hypothesis.strategies import from_regex
from fastapi.testclient import TestClient
from icecream import ic

from controller import print_state
from main import app
from model import PlayerProfile, InitialPlacementRequest, CellPlacement, FindMatchRequest, MatchRequestData, \
    GRID_LENGTH, GameData


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


def get_updated_available_locs(available_locs: List[Tuple[int, int]], grid_length=10) -> Dict[str, int]:
    myrandom = random.randint(0, 9)
    next_locs = available_locs

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
    cell_range = int(GRID_LENGTH * 5 / 7) + 1

    available_locs = [(i, j) for i in range(cell_range) for j in range(cell_range)]
    cell_type_map = {1: 'ATTACK', 0: 'DEFEND'}
    p1_placements = []
    p2_placements = []
    for i in range(len(available_locs)):
        max_index = len(available_locs) - 1
        if max_index == 0:
            break
        x, y = available_locs.pop(random.randint(0, max_index) if max_index > 0 else 0)
        p1_placements.append(
            CellPlacement(
                cell_type=cell_type_map[random.randint(0, 1)],
                team_number=0,
                x_loc=x,
                y_loc=y))

        max_index -= 1
        if max_index == 0:
            break
        x, y = available_locs.pop(random.randint(0, max_index) if max_index > 0 else 0)
        p2_placements.append(
            CellPlacement(
                cell_type=cell_type_map[random.randint(0, 1)],
                team_number=0,
                x_loc=x,
                y_loc=y))

    p1_placements = [CellPlacement(
                cell_type=cell_type_map[random.randint(0, 1)],
                team_number=1,
                x_loc=0,
                y_loc=0)]

    p2_placements = [CellPlacement(
        cell_type=cell_type_map[random.randint(0, 1)],
        team_number=-1,
        x_loc=1,
        y_loc=0)]
    req1 = InitialPlacementRequest(
        user_id=user_id1,
        cell_placements=p1_placements)


    req2 = InitialPlacementRequest(
        user_id=user_id2,
        cell_placements=p2_placements)

    ic(asdict(req1))
    ic(asdict(req2))
    client.patch(f'/game/{md2.game_id}', json=asdict(req1))
    gresp = client.get(f'/game/{md2.game_id}')
    print_state(GameData(**gresp.json()))

    client.patch(f'/game/{md2.game_id}', json=asdict(req2))
    gresp = client.get(f'/game/{md2.game_id}')
    print_state(GameData(**gresp.json()))
    gresp = client.get(f'/game/{md2.game_id}')
    ic(gresp.json())
    print_state(GameData(**gresp.json()))

    for i in range(100):
        client.put(f'/game/{md2.game_id}')
        gresp = client.get(f'/game/{md2.game_id}')
        data_json = gresp.json()

        data = GameData(**data_json)
        if data.is_game_over:
            break
        print_state(data)
    print("Turn ended at turn: ", data.current_state.current_turn)


def test_simulate_next_step():
    input_value = 10719
    expected_value = {
        "game_id": 10719,
        "max_turns": 100,
        "p1_user_id": 43625,
        "p2_user_id": 59881,
        "current_state": {
            "current_turn": 2,
            "player_occupied_cells": [
                {
                    "x_loc": 2,
                    "y_loc": 9,
                    "team_number": -1,
                    "cell_type": "ATTACK",
                    "life": 1.0,
                    "resilience": 1.0
                },
                {
                    "x_loc": 3,
                    "y_loc": 9,
                    "team_number": -1,
                    "cell_type": "ATTACK",
                    "life": 1.0,
                    "resilience": 1.0
                },
                {
                    "x_loc": 5,
                    "y_loc": 0,
                    "team_number": -1,
                    "cell_type": "ATTACK",
                    "life": 1.0,
                    "resilience": 1.0
                },
                {
                    "x_loc": 8,
                    "y_loc": 0,
                    "team_number": -1,
                    "cell_type": "ATTACK",
                    "life": 1.0,
                    "resilience": 1.0
                },
                {
                    "x_loc": 5,
                    "y_loc": 0,
                    "team_number": 1,
                    "cell_type": "ATTACK",
                    "life": 1.0,
                    "resilience": 1.0
                },
                {
                    "x_loc": 8,
                    "y_loc": 0,
                    "team_number": 1,
                    "cell_type": "ATTACK",
                    "life": 1.0,
                    "resilience": 1.0
                }
            ]
        },
        "awaiting_p1": False,
        "awaiting_p2": False,
        "awaiting_placements": True,
        "score_card": {
            "p1_score": 0.0,
            "p2_score": 0.0
        },
        "grid_length": 10,
        "is_game_over": True
    }
    output_value = app.simulate_next_step(input_value)
    assert output_value == expected_value