from cells.cell_types import AttackCell, AttackCellData
from simulator import GameState, Simulator, EMPTY_CELL


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



