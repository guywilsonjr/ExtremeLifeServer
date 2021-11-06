import requests

from cells.cell_types import AttackCellData
from simulator import GameState, Simulator, EMPTY_CELL



testun1 = 'test-user-1'


def test_cell():
    cell = AttackCellData(x_loc=0, y_loc=0, team_number=1, grid_length=6, grid_height=5)
    print(cell)
    assert cell.attack == 1.0


def test_sim():
    sim = Simulator()
    empty_state = GameState()
    for cellrow in empty_state.cell_grid:
        for cell in cellrow:
            assert cell == EMPTY_CELL
    sim.print_state(empty_state)


def test_profile():
    resp = requests.post('localhost:8000/profile', data={'username': testun1})
    assert resp.json()['username'] == 'test-user-1'
    resp = requests.get('localhost:8000/profile')
    assert any(filter(lambda profile: profile['username'] == 'test-user-1', resp.json()))

