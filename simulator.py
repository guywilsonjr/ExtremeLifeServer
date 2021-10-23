import copy
from pydantic.dataclasses import dataclass
from typing import List, Set

from cells.cell import Cell

GRID_LENGTH = 10



@dataclass
class CellGrid(List[List[Cell]]):
    def get_team_grid(self) -> TeamGrid:
        return [[cell.team_number for cell in row] for row in self]


@dataclass
class GameState:
    current_turn: int
    cell_grid: CellGrid
    team_grid: TeamGrid

    def __init__(self):
        # Initialize a GRID_LENGTH x GRID_LENGTH grid of empty cells
        self.cell_grid = [[Cell(x_loc, y_loc, 0) for x_loc in range(GRID_LENGTH)] for y_loc in range(GRID_LENGTH)]
        self.team_grid = [cell.team_number for row in self.cell_grid for cell in row]
        self.current_turn = 0

    def get_cell_grid(self) -> CellGrid:
        return self.cell_grid

    def get_team_grid(self) -> TeamGrid:
        return self.team_grid


class Simulator:
    game_states: List[GameState]
    latest_state: GameState

    def __init__(self):
        self.game_states = []
        initial_state = GameState()
        self.latest_state = initial_state
        self.game_states.append(initial_state)

    @staticmethod
    def transition_state(game_state: GameState) -> GameState:
        return game_state

    def get_simulated_cell_transitions(self, cell_grid) -> TeamGrid:
        next_updated_grid = TeamGrid()

        for row in cell_grid:
            next_updated_row = []
            for cell in row:
                next_updated_cell_output = cell.simulate_step(cell_grid)
                next_updated_row.append(next_updated_cell_output)
            next_updated_grid.append(next_updated_row)
        return next_updated_grid

    def simulate_step(self, game_state: GameState) -> GameState:
        game_state_copy = copy.deepcopy(game_state)
        # update game info then process each cell transition
        new_game_state = self.transition_state(game_state_copy)
        new_game_state.team_grid = self.get_simulated_cell_transitions(new_game_state.get_cell_grid())
        self.latest_state = new_game_state
        self.game_states.append(self.latest_state)
