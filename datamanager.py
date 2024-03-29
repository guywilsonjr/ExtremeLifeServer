import os
import time
from dataclasses import asdict
from typing import Union, List, Optional, Dict
from tinydb import TinyDB, Query
from model import ActionScriptMeta, GameData, MatchRequestData, PlayerProfile

DB_LOCATION = '.db/'
os.makedirs(DB_LOCATION) if not os.path.exists(DB_LOCATION) else None
PROFILE_TN = 'profile'
ACTIONSCRIPT_TN = 'actionscripts'
GAME_TN = 'games'
OLD_GAME_TN = 'old_game_data'
MATCH_REQUEST_TN = 'matchrequests'

GameDataType = Union[ActionScriptMeta, MatchRequestData, GameData, PlayerProfile]
lock_file = 'lockfile'


def write_locked(f):
    def wrapper(*args, **kwargs):
        with open(lock_file, 'w'):
            return f(*args, **kwargs)
    return wrapper


def read_locked(f):
    def wrapper(*args, **kwargs):
        with open(lock_file, 'r'):
            return f(*args, **kwargs)
    return wrapper


class DataManager:
    def __init__(self):
        self.db = self.start_new_db()

    @write_locked
    def create_entity(self, entity: GameDataType, table_name: str) -> None:
        table = self.db.table(table_name)
        table.insert(asdict(entity))

    @write_locked
    def update_match_requests(self, req1: MatchRequestData, req2: MatchRequestData) -> None:
        table = self.db.table(MATCH_REQUEST_TN)
        check = Query()
        table.upsert(asdict(req1), check.user_id == req1.user_id)
        table.upsert(asdict(req2), check.user_id == req2.user_id)

    @read_locked
    def list_entity(self, table_name: str) -> List[Dict]:
        return self.db.table(table_name).all()

    @write_locked
    def create_player_profile(self, profile: PlayerProfile) -> None:
        self.create_entity(profile, PROFILE_TN)

    @write_locked
    def create_actionscript(self, actionscript: ActionScriptMeta) -> None:
        self.create_entity(actionscript, ACTIONSCRIPT_TN)

    @write_locked
    def create_match_request(self, match_request_data: MatchRequestData) -> MatchRequestData:
        self.create_entity(match_request_data, MATCH_REQUEST_TN)
        return match_request_data

    @write_locked
    def create_game(self, game: GameData) -> None:
        self.create_entity(game, GAME_TN)

    @write_locked
    def create_old_game(self, game: GameData) -> None:
        self.create_entity(game, OLD_GAME_TN)

    @write_locked
    def update_game(self, game: GameData) -> None:
        while(self.get_game(game.game_id)):
            self.remove_game(game.game_id)
        self.create_entity(game, GAME_TN)

    @read_locked
    def get_game(self, game_id: int) -> Optional[GameData]:
        gq = Query()
        game_data = self.db.table(GAME_TN).search(gq.game_id == game_id)
        return GameData(**game_data[-1]) if game_data else None

    @read_locked
    def get_games(self) -> List[GameData]:
        return [GameData(**game) for game in self.db.table(GAME_TN).all()]

    @read_locked
    def validate_game_id(self, game_id: int) -> bool:
        return bool(self.get_game(game_id))

    @write_locked
    def remove_game(self, game_id: int) -> List[str]:
        gq = Query()
        removed_entry_id = self.db.table(GAME_TN).remove(gq.game_id == game_id)
        return removed_entry_id if removed_entry_id else None

    @read_locked
    def get_profile_by_user_id(self, user_id: int) -> Optional[PlayerProfile]:
        gq = Query()
        data = self.db.table(PROFILE_TN).get(gq.user_id == user_id)
        if data:
            return PlayerProfile(**data)
        else:
            return None

    @read_locked
    def get_match_request_by_user_id(self, user_id: int) -> Optional[MatchRequestData]:
        gq = Query()
        match_request = self.db.table(MATCH_REQUEST_TN).get(gq.user_id == user_id)
        return MatchRequestData(**match_request) if match_request else None

    @read_locked
    def get_match_request_by_request_id(self, request_id: int) -> Optional[MatchRequestData]:
        gq = Query()
        match_request = self.db.table(MATCH_REQUEST_TN).get(gq.request_id == request_id)
        return MatchRequestData(**match_request) if match_request else None

    @read_locked
    def get_actionscript(self, actionscript_id: int) -> Optional[ActionScriptMeta]:
        gq = Query()
        action_script_data = self.db.table(ACTIONSCRIPT_TN).get(gq.resp.action_script_id == actionscript_id)
        return ActionScriptMeta(**action_script_data) if action_script_data else None

    @read_locked
    def list_match_requests(self) -> List[MatchRequestData]:
        return [MatchRequestData(**req) for req in self.list_entity(MATCH_REQUEST_TN)]

    @read_locked
    def list_player_profiles(self) -> List[PlayerProfile]:
        return [PlayerProfile(**prof) for prof in self.list_entity(PROFILE_TN)]

    @read_locked
    def list_action_scripts(self) -> List[ActionScriptMeta]:
        return [ActionScriptMeta(**script) for script in self.list_entity(ACTIONSCRIPT_TN)]

    @write_locked
    def delete_match_request(self, req: MatchRequestData) -> None:
        pid = req.user_id
        match_req_query = Query()
        self.db.table(MATCH_REQUEST_TN).remove(match_req_query.user_id == pid)

    @write_locked
    def start_new_db(self) -> TinyDB:
        return TinyDB(f'.db/data_0.json')

