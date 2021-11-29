import copy

from cells.cell import CellEffectType, CellData
import numpy as np

from model import GameState, GameData


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

    def simulate_step(self, game: GameData) -> GameData:
        game_state = game
        game_state_copy = copy.deepcopy(game_state)
        # update game info then process each cell transition
        new_game_state = self.transition_state(game_state_copy)
        new_game_state.team_grid = self.get_simulated_cell_transitions(new_game_state.get_cell_grid())
        self.latest_state = new_game_state
        self.game_states.append(self.latest_state)




