import copy
import time

from icecream import ic

from cells.cell import CellEffectType
import numpy as np

from model import GameState, GameData, FindMatchRequest, MatchRequestData

from datamanager import DataManager

class Controller:
    def __init__(self):
        self.dm = DataManager()
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
    def update_placements(placements):
        '''

        :return: None
        '''
        return

    @staticmethod
    def transition_state(game_state: GameState) -> GameState:
        return game_state

    def get_special_effect_grid(self):
        return

    def create_match(self, req1: FindMatchRequest, req2: FindMatchRequest) -> int:
        new_game_id = int(time.time())
        game_data = GameData(
            game_id=new_game_id,
            player1_req=req1,
            player2_req=req2,
            current_state=GameState())
        self.dm.create_game(game_data)
        return new_game_id

    def process_match(self, init_req: FindMatchRequest) -> FindMatchRequest:
        existing_player_req = self.dm.get_match_request_by_user_id(init_req.user_id)
        if existing_player_req:
            return existing_player_req
        else:
            prof = self.dm.get_profile_by_user_id(init_req.user_id)
            existing_player_req = self.dm.create_match_request(init_req, prof.username)
        existing_reqs = self.dm.list_match_requests()
        other_player_reqs = list(
            filter(
                lambda req: req.request_id != existing_player_req.request_id and not req.is_match_complete,
                existing_reqs))

        if other_player_reqs:
            matching_req = other_player_reqs[0] if other_player_reqs else None
            if matching_req:
                if existing_player_req:
                    ic(
                        'Found Existing player req\n',
                        existing_player_req,
                        '\n Matching req\n',
                        matching_req)
                    new_game_id = self.create_match(existing_player_req, matching_req)
                    ic('Setting new game ids to', new_game_id)
                    existing_player_req = MatchRequestData(
                        user_id=existing_player_req.user_id,
                        username=existing_player_req.username,
                        request_id=existing_player_req.request_id,
                        action_script_id=existing_player_req.action_script_id,
                        is_match_complete=True,
                        game_id=new_game_id
                    )
                    matching_req = MatchRequestData(
                        user_id=matching_req.user_id,
                        username=matching_req.username,
                        request_id=matching_req.request_id,
                        action_script_id=matching_req.action_script_id,
                        is_match_complete=True,
                        game_id=new_game_id
                    )
                    self.dm.update_match_requests(matching_req, existing_player_req)
                    ic('Matches updated')
        return existing_player_req

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
                if cell_effect.effect_type == CellEffectType.ATTACK_EFFECT:
                    attack_matrix[cell_effect.effect_x_loc, cell_effect.effect_y_loc] = cell_effect
                elif cell_effect.effect_type == CellEffectType.DEFEND_EFFECT:
                    defense_matrix[cell_effect.effect_x_loc, cell_effect.effect_y_loc] = cell_effect
                elif cell_effect.effect_type == CellEffectType.REPLICATE_EFFECT:
                    replication_matrix[cell_effect.effect_x_loc, cell_effect.effect_y_loc] = cell_effect
                elif cell_effect.effect_type == CellEffectType.INFECT_EFFECT:
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




