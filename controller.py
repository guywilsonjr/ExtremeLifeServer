import copy
import time
from dataclasses import asdict
from random import Random
from typing import List, Optional, Tuple, Dict

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
    ActionScriptMeta, InitialPlacementRequest, CellInfo, ScoreCard, GRID_LENGTH)

from datamanager import DataManager


MAX_TURNS = 100
ATTACK_DAMAGE = np.float64(0.2)
REPLICATION_CHANCE = np.float64(ATTACK_DAMAGE / 2.0)
STANDARD_LIFE = 1.0
STANDARD_RESILIENCE = STANDARD_LIFE


def print_state(game_data: GameData):
    positions = {(cinf.x_loc, cinf.y_loc): str(cinf.life * cinf.team_number) +':'+str(cinf.cell_type)[0] for cinf in game_data.current_state.player_occupied_cells}
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


def get_cell_attack(cell_info: Optional[CellInfo]) -> np.float64:
    if not cell_info:
        return np.float64(0.0)
    cell_type = cell_types.CELL_MAPPINGS[cell_info.cell_type]
    return cell_type.get_stats().attack


def get_cell_defend_action(cell_action: Optional[CellAction]) -> np.float64:
    if not cell_action:
        return np.float64(0.0)
    defense = CELL_MAPPINGS[cell_action.cell_info.cell_type].get_stats().defense * 2
    if cell_action.effect_type == CellActionType.DEFEND_ACTION:
        return defense * 2
    else:
        return np.float64(0.0)


def get_cell_defense(cell_info: Optional[CellInfo]) -> np.float64:
    if not cell_info:
        return np.float64(0.0)
    else:
        return CELL_MAPPINGS[cell_info.cell_type].get_stats().defense


def get_cell_life(cell_info: Optional[CellInfo]) -> np.float64:
    return cell_info.life if cell_info else np.float64(0.0)


def get_cell_attack_action(cell_action: Optional[CellAction]) -> np.float64:
    if not cell_action:
        return np.float64(0.0)

    if cell_action.effect_type == CellActionType.ATTACK_ACTION:
        return ATTACK_DAMAGE # np.float64(CELL_MAPPINGS[cell_action.cell_info.cell_type].get_stats().attack) * random_gen.random()
    else:

        return np.float64(0.0)


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
attack_action_vec = np.vectorize(get_cell_attack_action, otypes=[np.float64])
life_vec = np.vectorize(get_cell_life)
random_gen = Random(time.time_ns())


def get_adjacent_loc_tuples(x_loc: int, y_loc: int) -> List[Tuple[int, int]]:
    adjacent_locs = []
    left_loc = (x_loc - 1, y_loc) if x_loc - 1 > 0 else None
    right_loc = (x_loc + 1, y_loc) if x_loc < GRID_LENGTH - 1 else None
    down_loc = (x_loc, y_loc - 1) if y_loc - 1 > 0 else None
    up_loc = (x_loc, y_loc + 1) if y_loc < GRID_LENGTH - 1 else None

    if left_loc:
        adjacent_locs.append(left_loc)
    if right_loc:
        adjacent_locs.append(right_loc)
    if down_loc:
        adjacent_locs.append(down_loc)
    if up_loc:
        adjacent_locs.append(up_loc)

    return adjacent_locs


def get_cells_by_team(occ_cell_list: List[CellInfo], team: int):
    ic(occ_cell_list)
    return [occ_cell for occ_cell in occ_cell_list if occ_cell.team_number == team]


def get_cells_by_type(occ_cell_list: List[CellInfo], cell_type: str):
    return [occ_cell for occ_cell in occ_cell_list if occ_cell.cell_type == cell_type]


def get_replicated_cell(repl_loc: tuple, occ_cell_list: List[CellInfo], team_num: int):
    team_cells = get_cells_by_team(occ_cell_list, team_num)
    if len(team_cells) == 0:
        return None

    number_of_team_neighbors = len(team_cells)
    chance_to_replicate = REPLICATION_CHANCE * number_of_team_neighbors

    attack_cells = get_cells_by_type(team_cells, "ATTACK")
    defend_cells = get_cells_by_type(team_cells, "DEFEND")
    num_attack_cells = len(attack_cells)
    num_defend_cells = len(defend_cells)
    new_cell_type = "DEFEND"
    if num_attack_cells > 0 and num_defend_cells > 0:
        new_cell_type = "DEFEND"
        if random_gen.random() < num_attack_cells/number_of_team_neighbors:
            new_cell_type = "ATTACK"
    elif num_defend_cells < 1:
        new_cell_type = "ATTACK"
    elif num_attack_cells > 0:
        new_cell_type = "ATTACK"
    elif num_defend_cells > 0:
        new_cell_type = "DEFEND"

    # chance to replicate. More cells nearby means more chance
    if random_gen.random() < chance_to_replicate:
        new_cell = CellInfo(
            x_loc=repl_loc[0],
            y_loc=repl_loc[1],
            team_number=team_num,
            life=STANDARD_LIFE,
            resilience=STANDARD_RESILIENCE,
            cell_type=new_cell_type)
        return new_cell
    else:
        return None


def get_replicated_cells(occupied_cells: List[CellInfo]):
    occ_cell_map = dict()
    # Map cell locations to occupied cells
    for occ_cell in occupied_cells:
        occ_cell_map[(occ_cell.x_loc, occ_cell.y_loc)] = occ_cell

    # get the locations surrounding all occupied cells
    locs_to_check = []
    for loc_tuple, occ_cell in occ_cell_map.items():
        x_loc = loc_tuple[0]
        y_loc = loc_tuple[1]
        adjacent_locs = get_adjacent_loc_tuples(x_loc, y_loc)
        locs_to_check.extend(adjacent_locs)

    # From those locations select the non-occupied locations
    replicatable_locs = [loc for loc in locs_to_check if not loc in occ_cell_map]

    # Now create a map to map the replicatable locations to a list of their surrounding occupied cells
    open_loc_map_to_occ_neighbors: Dict[Tuple[int, int], List[CellInfo]] = dict()
    for open_repl_loc in replicatable_locs:
        x_loc = open_repl_loc[0]
        y_loc = open_repl_loc[1]
        spots_to_check_for_cells = get_adjacent_loc_tuples(x_loc, y_loc)
        open_loc_map_to_occ_neighbors[open_repl_loc] = [occ_cell_map[spot] for spot in spots_to_check_for_cells if spot in occ_cell_map]

    ic(open_loc_map_to_occ_neighbors)
    replicated_cells = []
    for repl_loc, occ_cell_list in open_loc_map_to_occ_neighbors.items():
        first_dibs_team = 1 if random_gen.random() < 0.5 else -1
        second_dibs_team = 1 if first_dibs_team == -1 else 1
        potential_first_dibs_cell = get_replicated_cell(repl_loc, occ_cell_list, first_dibs_team)
        if potential_first_dibs_cell:
            # First team got it. Continue on to try again at the next location
            ic(f'Adding replication for team {first_dibs_team}')
            replicated_cells.append(potential_first_dibs_cell)
            continue
        else:
            ic(f'Adding replication for team {second_dibs_team}')
            potential_second_dibs_cell = get_replicated_cell(repl_loc, occ_cell_list, second_dibs_team)
            if potential_second_dibs_cell:
                replicated_cells.append(potential_second_dibs_cell)

    for rep_cell in replicated_cells:

        if (rep_cell.x_loc, rep_cell.y_loc) in occ_cell_map:
            conflicting_cell = occ_cell_map[(rep_cell.x_loc, rep_cell.y_loc)]
            ic(f"ISSUE FOUND REPLICATION CELL: {rep_cell} conflicting with existing cell {conflicting_cell}")

    return replicated_cells


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
                life=STANDARD_LIFE,
                resilience=STANDARD_RESILIENCE
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
        #ic(cell_action_mat)
        defense_mat = defense_vec(cell_info_mat)
        attack_target_mat = attack_action_vec(cell_action_mat)
        #ic(attack_target_mat)
        life_mat = life_vec(cell_info_mat) * defense_mat
        #ic(life_mat)
        rem_life_mat = life_mat - attack_target_mat
        #ic(rem_life_mat)
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

        # If game is not over Do replication step
        next_replicated_cells = get_replicated_cells(next_cells)
        for repl_cell in next_replicated_cells:
            if repl_cell == None:
                ic('ISSUE: Some replicated cells are null')
            else:
                next_cells.append(repl_cell)
                if repl_cell.team_number == 1:
                    p1_score += repl_cell.life
                else:
                    p2_score += repl_cell.life

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




