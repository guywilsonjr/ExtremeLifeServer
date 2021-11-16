import os
import time
from dataclasses import asdict
from tinydb import TinyDB
from profile import Profile
from simulator import ActionScript, GameData

DB_LOCATION = '.db/'
os.makedirs(DB_LOCATION) if not os.path.exists(DB_LOCATION) else None

PROFILE_TN = 'profile'
ACTIONSCRIPT_TN = 'actionscripts'
GAME_TN = 'games'


def create_entity(db: TinyDB, entity: object, table_name: str):
    table = db.table(table_name)
    table.insert(asdict(entity))


def list_entity(db: TinyDB, table_name: str):
    return db.table(table_name).all()


def create_player_profile(db: TinyDB, profile: Profile):
    create_entity(db, profile, PROFILE_TN)


def create_actionscript(db: TinyDB, actionscript: ActionScript):
    create_entity(db, actionscript, ACTIONSCRIPT_TN)


def create_game(db: TinyDB, game: GameData):
    create_entity(db, game, GAME_TN)

def get_game(db: TinyDB, game_id: int):
    return db.table(GAME_TN).get(f'game_id = {game_id}')

def list_player_profiles(db: TinyDB):
    return list_entity(db, PROFILE_TN)


def list_action_scripts(db: TinyDB):
    return list_entity(db, ACTIONSCRIPT_TN)


def start_new_db() -> TinyDB:
    return TinyDB(f'.db/data_0.json')
