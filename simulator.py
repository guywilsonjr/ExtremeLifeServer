import copy
from pydantic.dataclasses import dataclass
from typing import List, Set

GRID_LENGTH = 10
TeamGrid = List[List[int]]


@dataclass
class Cell:
    x_loc: int
    y_loc: int
    team_number: int

    def __init__(self, x_loc, y_loc, team_number):
        self.x_loc = x_loc
        self.y_loc = y_loc
        self.team_number = team_number

    def get_neighbors(self, grid: TeamGrid) -> Set:
        # Search the 3x3 grid around cell or 3x2 or 2x2 if at an edge or corner
        x_start = self.x_loc - 1 if self.x_loc > 0 else self.x_loc
        x_end = self.x_loc + 1 if self.x_loc < GRID_LENGTH - 1 else self.x_loc
        y_start = self.y_loc - 1 if self.y_loc > 0 else self.y_loc
        y_end = self.y_loc + 1 if self.y_loc < GRID_LENGTH - 1 else self.y_loc

        neighbors = grid[x_start:x_end, y_start:y_end]
        # Remove self
        neighbors.remove(self)
        return neighbors

    def simulate_step(self, grid: TeamGrid) -> int:
        neighbors = self.get_neighbors(grid)
        num_neighbors = len(neighbors)
        if self.team_number == 0:
            return 0

        if num_neighbors < 2:
            return 0
        elif num_neighbors > 4:
            return 0
        else:
            return 1

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
