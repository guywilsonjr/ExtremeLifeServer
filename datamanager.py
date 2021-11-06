import os
import time
from tinydb import TinyDB
from profile import Profile


DB_LOCATION = '.db/'
os.makedirs(DB_LOCATION) if not os.path.exists(DB_LOCATION) else None

PROFILE_TN = 'profile'


def create_player_profile(db: TinyDB, profile: Profile):
    profile_table = db.table(PROFILE_TN)
    profile_table.insert(profile)


def list_player_profiles(db: TinyDB):
    profile_table = db.table(PROFILE_TN)
    return profile_table.all()


def start_new_db() -> TinyDB:
    cur_time = int(time.time())
    return TinyDB(f'.db/data_{cur_time}.json')
