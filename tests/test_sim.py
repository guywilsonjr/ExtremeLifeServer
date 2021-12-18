import requests
import logging
from fastapi.testclient import TestClient

from main import app
from controller import GameState, Controller
from model import GameData

import pytest
from pytest_mock import MockFixture
import datamanager

logging.getLogger().setLevel(logging.DEBUG)


testun1 = 'test-user-1'



def test_sim():
    sim = Controller()
    empty_state = GameState(0, [])
    sim.print_state(empty_state)


def test_profile():
    client = TestClient(app)
    resp = client.post("/username/test-user-1")
    data = resp.json()
    print(data)
    assert data['username'] == 'test-user-1'
    resp = client.get("/username")
    profile_list = resp.json()
    print(profile_list)
    assert any(list(filter(lambda profile: profile['username'] == 'test-user-1', profile_list)))


@pytest.fixture
def mock_db(mocker: MockFixture):
    dm = mocker.patch("controller.DataManager").return_value
    logging.debug(f'datamanager.DataManager: {datamanager.DataManager()}')
    dm.update_game = lambda x: x
    dm.get_game.return_value = GameData(**{
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
        "is_game_over": False
    })
    logging.debug(
        f'datamanager.DataManager().get_game(): {datamanager.DataManager().get_game(10719)}')

    return dm.get_game.return_value
    

def test_simulate_next_state(mock_db):
    input_value = 10719
    logging.debug(f'mock_db.current_state.current_turn: {mock_db.current_state.current_turn}')
    import copy
    original_gamedata = copy.deepcopy(mock_db)
    original_gamedata.current_state.current_turn += 1
    expected_value = original_gamedata
    output_value = Controller().simulate_next_state(input_value)
    logging.debug(f'mock_db.current_state.current_turn1: {mock_db.current_state.current_turn}')
    logging.debug(f'output_value.current_state.current_turn: {output_value.current_state.current_turn}')
    logging.debug(f'expected_value.current_state.current_turn: {expected_value.current_state.current_turn}')
    assert output_value == expected_value