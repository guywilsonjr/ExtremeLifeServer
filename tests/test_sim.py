import requests
from fastapi.testclient import TestClient

from main import app
from cells.cell_types import AttackCellData
from controller import GameState, Controller
from cells.cell import EMPTY_CELL



testun1 = 'test-user-1'


def test_cell():
    cell = AttackCellData(
        x_loc=0,
        y_loc=0,
        team_number=1,
        grid_length=6,
        grid_height=5)

    print(cell)
    assert cell.attack == 1.0


def test_sim():
    sim = Controller()
    empty_state = GameState()
    for cellrow in empty_state.cell_grid:
        for cell in cellrow:
            assert cell == EMPTY_CELL
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


