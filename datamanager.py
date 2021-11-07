import os
import time
from dataclasses import asdict

from tinydb import TinyDB
from profile import Profile

from simulator import ActionScript

DB_LOCATION = '.db/'
os.makedirs(DB_LOCATION) if not os.path.exists(DB_LOCATION) else None

PROFILE_TN = 'profile'

ACTIONSCRIPT_TN = 'actionscripts'


def create_player_profile(db: TinyDB, profile: Profile):
    profile_table = db.table(PROFILE_TN)
    profile_table.insert(asdict(profile))



def add_action_script(db: TinyDB, actionscript: ActionScript):
    script_table = db.table(ACTIONSCRIPT_TN)
    script_table.insert(asdict(actionscript))

def list_player_profiles(db: TinyDB):
    profile_table = db.table(PROFILE_TN)
    return profile_table.all()

def list_action_scripts(db: TinyDB):
    script_table = db.table(ACTIONSCRIPT_TN)
    return script_table.all()


def start_new_db() -> TinyDB:
    cur_time = int(time.time())
    return TinyDB(f'.db/data_0.json')
