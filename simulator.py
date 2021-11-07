import copy
import dataclasses

from pydantic.dataclasses import dataclass
from typing import List

from cells.cell import Cell, CellGrid, CellEffectType
import numpy as np
from fastapi import File
from profile import Profile

GRID_LENGTH = 10
EMPTY_CELL: Cell = None


@dataclasses.dataclass
class ActionScript:
    profile: Profile
    script_name: str
    file: File


@dataclass
class GameState:
    current_turn: int
    cell_grid: CellGrid

    def __init__(self):
        # Initialize a GRID_LENGTH x GRID_LENGTH grid of empty cells
        self.cell_grid = [[EMPTY_CELL for y_loc in range(GRID_LENGTH)] for x_loc in range(GRID_LENGTH)]
        self.current_turn = 0

    def get_cell_grid(self) -> CellGrid:
        return self.cell_grid


class Simulator:
    def __init__(self):
        self.game_states = []
        initial_state = GameState()
        self.current_turn = 0
        self.latest_state = initial_state
        self.game_states.append(initial_state)

    def print_state(self, state: GameState):
        print()
        for row in state.cell_grid:
            print(row)
        print()

    @staticmethod
    def transition_state(game_state: GameState) -> GameState:
        return game_state

    def get_special_effect_grid(self):
        return

    def get_simulated_cell_transitions(self, cell_grid) -> np.ndarray:
        num_rows = len(cell_grid)
        num_cols = len(cell_grid[0])
        attack_matrix = np.ndarray(shape=(num_rows, num_cols), dtype=np.float)
        defense_matrix = np.ndarray(shape=(num_rows, num_cols), dtype=np.float)
        replication_matrix = np.ndarray(shape=(num_rows, num_cols), dtype=np.float)
        infection_matrix = np.ndarray(shape=(num_rows, num_cols), dtype=np.float)

        for i in range(num_rows):
            row = cell_grid[i]
            for j in range(num_cols):
                cell = row[j]
                cell_effect = cell.simulate_step(cell_grid)
                if cell_effect.effect_type == CellEffectType.ATTACK:
                    attack_matrix[cell_effect.effect_x_loc, cell_effect.effect_y_loc] = cell_effect
                elif cell_effect.effect_type == CellEffectType.DEFEND:
                    defense_matrix[cell_effect.effect_x_loc, cell_effect.effect_y_loc] = cell_effect
                elif cell_effect.effect_type == CellEffectType.REPLICATE:
                    replication_matrix[cell_effect.effect_x_loc, cell_effect.effect_y_loc] = cell_effect
                elif cell_effect.effect_type == CellEffectType.INFECT:
                    infection_matrix[cell_effect.effect_x_loc, cell_effect.effect_y_loc] = cell_effect

        return attack_matrix

    def simulate_step(self, game_state: GameState) -> GameState:
        game_state_copy = copy.deepcopy(game_state)
        # update game info then process each cell transition
        new_game_state = self.transition_state(game_state_copy)
        new_game_state.team_grid = self.get_simulated_cell_transitions(new_game_state.get_cell_grid())
        self.latest_state = new_game_state
        self.game_states.append(self.latest_state)


@dataclass
class Game:
    game_id: str
    player1: Profile
    player2: Profile
    game_states: List[GameState]
    current_state: GameState

