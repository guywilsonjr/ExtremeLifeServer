import copy
import random
import time
from dataclasses import asdict
from random import Random
from typing import List, Optional

from fastapi import UploadFile, File
from icecream import ic
from fastapi import HTTPException

import numpy as np

from cells import cell_types
from cells.cell_types import CellActionType, CellAction, CELL_MAPPINGS
from model import (
    GameState,
    GameData,
    FindMatchRequest,
    MatchRequestData,
    PlayerProfile,
    ActionScriptMetaResp,
    ActionScriptMeta, InitialPlacementRequest, CellInfo, ScoreCard)

from datamanager import DataManager

MAX_TURNS = 100


def print_state(game_data: GameData):
    positions = {(cinf.x_loc, cinf.y_loc): str(cinf.life * cinf.team_number) +':'+str(cinf.cell_type)[0] for cinf in game_data.current_state.player_occupied_cells}
    #ic(positions)
    glen = game_data.grid_length
    grid = [[0 for i in range(glen)] for j in range(glen)]
    for (x_loc, y_loc), team_number in positions.items():
        grid[x_loc][y_loc] = team_number
    ic(grid)


def is_neighbor(cell_info_1: CellInfo, cell_info_2: CellInfo) -> bool:
    if cell_info_1.x_loc == cell_info_2.x_loc and cell_info_1.y_loc == cell_info_2.y_loc:
        return False
    else:
        return abs(cell_info_2.x_loc - cell_info_1.x_loc) <= 1 and abs(cell_info_2.y_loc - cell_info_1.y_loc) <= 1


def get_cell_neighbors(cell_info: CellInfo, player_occupied_cells: List[CellInfo]) -> List[CellInfo]:
    return [potential_neighbor for potential_neighbor in player_occupied_cells if
            is_neighbor(cell_info, potential_neighbor)]


def get_cell_attack(cell_info: Optional[CellInfo]) -> float:
    if not cell_info:
        return 0
    cell_type = cell_types.CELL_MAPPINGS[cell_info.cell_type]
    return cell_type.get_stats().attack


def get_cell_defend_action(cell_action: Optional[CellAction]) -> float:
    if not cell_action:
        return 0
    defense = CELL_MAPPINGS[cell_action.cell_info.cell_type].get_stats().defense * 2
    if cell_action.effect_type == CellActionType.DEFEND_ACTION:
        return defense * 2
    else:
        return 0


def get_cell_defense(cell_info: Optional[CellInfo]) -> float:
    if not cell_info:
        return 0
    else:
        return CELL_MAPPINGS[cell_info.cell_type].get_stats().defense



def get_cell_life(cell_info: Optional[CellInfo]) -> float:
    return cell_info.life if cell_info else 0



def get_cell_attack_action(cell_action: Optional[CellAction]) -> float:
    if not cell_action:
        return 0

    if cell_action.effect_type == CellActionType.ATTACK_ACTION:
        return 0.2 # float(CELL_MAPPINGS[cell_action.cell_info.cell_type].get_stats().attack) * random_gen.random()
    else:
        return 0


def get_cell_matrices(game_data: GameData):
    grid_length = game_data.grid_length
    player_occupied_cells = game_data.current_state.player_occupied_cells
    cell_info_mat = np.array([[None] * grid_length] * grid_length)
    cell_action_mat = np.array([[None] * grid_length] * grid_length)

    for cur_cell in player_occupied_cells:
        cell_type = cell_types.CELL_MAPPINGS[cur_cell.cell_type]
        cell_info_mat[cur_cell.x_loc][cur_cell.y_loc] = cur_cell
        neighbors = get_cell_neighbors(cur_cell, player_occupied_cells)
        action = cell_type.get_action(cur_cell, neighbors)
        cell_action_mat[action.effect_x_loc][action.effect_y_loc] = action

    return cell_info_mat, cell_action_mat


defense_vec = np.vectorize(get_cell_defense)
defense_action_vec = np.vectorize(get_cell_defend_action)
attack_action_vec = np.vectorize(get_cell_attack_action)
life_vec = np.vectorize(get_cell_life)
random_gen = Random(time.time_ns())

class Controller:
    def __init__(self):
        self.dm = DataManager()


    def update_placements(self, game_id: int, placements: InitialPlacementRequest):
        game_data = self.dm.get_game(game_id)
        if not game_data:
            raise HTTPException(status_code=404, detail=f'Game not found: {game_id}')
        gcopy = asdict(copy.deepcopy(game_data))
        team_number = 1 if game_data.p1_user_id == placements.user_id else -1
        info_placements = [
            CellInfo(
                x_loc=pl.x_loc,
                y_loc=pl.y_loc,
                team_number=team_number,
                cell_type=pl.cell_type,
                life=1.0,
                resilience=1.0
            ) for pl in placements.cell_placements]
        info_placements.extend(game_data.current_state.player_occupied_cells)
        gcopy['current_state']['player_occupied_cells'] = info_placements
        if placements.user_id == game_data.p1_user_id:
            gcopy['awaiting_p1'] = False
        elif placements.user_id == game_data.p2_user_id:
            gcopy['awaiting_p2'] = False

        updated_game = GameData(**gcopy)
        print('Inserting update:')
        print(updated_game)
        self.dm.update_game(updated_game)
        print('Retrieved:')
        print(self.dm.get_game(game_id))

    def get_random_id(self):
        return random_gen.randint(0, 2 ** 16)

    def create_user(self, username: str):
        user_id = self.get_random_id()
        profile = PlayerProfile(user_id, username)

        self.dm.create_player_profile(profile)
        return profile

    def create_action_script(self, script_name: str, file: UploadFile = File(...)):
        acmr = ActionScriptMetaResp(action_script_id=self.get_random_id(), script_name=script_name)
        pathname = script_name + str(self.get_random_id()) + '.py'
        with open(pathname, 'wb') as acfile:
            data = file.read()
            acfile.write(data)
        ac = ActionScriptMeta(
            resp=acmr,
            path=pathname)
        self.dm.create_actionscript(ac)
        return acmr

    def create_game(self, p1_user_id: int, p2_user_id: int) -> int:
        new_game_id = self.get_random_id()
        game_data = GameData(
            game_id=new_game_id,
            p1_user_id=p1_user_id,
            p2_user_id=p2_user_id,
            awaiting_placements=True,
            current_state=GameState(0,[]),
            awaiting_p1=True,
            awaiting_p2=True,
            max_turns=100,
            score_card=None
        )
        self.dm.create_game(game_data)
        return new_game_id

    def validate_find_match_request(self, req: FindMatchRequest) -> None:
        user_profile = self.dm.get_profile_by_user_id(req.user_id)
        # action_script = self.dm.get_actionscript(req.action_script_id)
        messages = []
        if not user_profile:
            messages.append(f'Invalid user_id: {req.user_id}')

        if messages:
            raise HTTPException(status_code=404, detail='\n'.join(messages))

    def process_match(self, init_req: FindMatchRequest) -> FindMatchRequest:
        self.validate_find_match_request(init_req)
        existing_player_req = self.dm.get_match_request_by_user_id(init_req.user_id)

        if existing_player_req:
            return existing_player_req
        else:
            prof = self.dm.get_profile_by_user_id(init_req.user_id)
            match_request_data = MatchRequestData(
                action_script_id=init_req.action_script_id,
                user_id=init_req.user_id,
                username=prof.username,
                is_match_complete=False,
                game_id=None,
                request_id=self.get_random_id())
            existing_player_req = self.dm.create_match_request(match_request_data)
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
                    new_game_id = self.create_game(existing_player_req.user_id, matching_req.user_id)
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


    def simulate_next_state(self, game_id: int) -> GameData:
        game_data = self.dm.get_game(game_id)
        if not game_data:
            raise HTTPException(status_code=404, detail=f'Game not found: {game_id}')

        if game_data.is_game_over:
            return game_data

        occupied_cells = copy.deepcopy(game_data.current_state.player_occupied_cells)
        cell_info_mat, cell_action_mat = get_cell_matrices(game_data)
        # print(cell_info_mat)
        print(cell_action_mat)
        defense_mat = defense_vec(cell_info_mat)
        attack_target_mat = attack_action_vec(cell_action_mat)
        ic(attack_target_mat)
        defense_target_mat = defense_action_vec(cell_action_mat)
        #effective_defense_mat = defense_mat * defense_target_mat
        #calc_mat = effective_defense_mat - (attack_target_mat + 5)
        #ic(calc_mat)
        #calc_exp_mat = np.exp2(calc_mat)
        #ic(calc_exp_mat)
        # Also could consider using defense*life in calculation
        life_mat = life_vec(cell_info_mat) * defense_mat
        ic(life_mat)
        rem_life_mat = life_mat - attack_target_mat
        ic(rem_life_mat)
        next_cells = []
        p1_score = 0
        p2_score = 0
        for occ_cell in occupied_cells:
            cell_dict_copy = asdict(copy.deepcopy(occ_cell))
            rem_life = rem_life_mat[occ_cell.x_loc][occ_cell.y_loc]
            if rem_life > 10 ** -3:
                cell_dict_copy['life'] = rem_life
                next_cells.append(CellInfo(**cell_dict_copy))
                if occ_cell.team_number == 1:
                    p1_score += rem_life
                else:
                    p2_score += rem_life


        is_game_over = False
        if p1_score == 0:
            is_game_over = True
        elif p2_score == 0:
            is_game_over = True
        elif game_data.current_state.current_turn >= game_data.max_turns:
            is_game_over = True

        game_data_dict = asdict(copy.deepcopy(game_data))

        game_data_dict['current_state']['player_occupied_cells'] = next_cells
        game_data_dict['current_state']['current_turn'] = game_data.current_state.current_turn + 1
        game_data_dict['score_card'] = ScoreCard(**{'p1_score': p1_score, 'p2_score': p2_score})
        game_data_dict['is_game_over'] = is_game_over
        game_data_dict['awaiting_p1'] = False
        game_data_dict['awaiting_p2'] = False
        print(game_data_dict)
        new_game_data = GameData(**game_data_dict)
        self.dm.update_game(new_game_data)
        return new_game_data




