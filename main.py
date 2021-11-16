import time
from typing import Dict, List
from fastapi import FastAPI, File, UploadFile

import datamanager as dm
from profile import Profile
from simulator import Simulator, ActionScript, GameData, ActionScriptResponse
from simulator import GameState


app = FastAPI()
sim = Simulator()
db = dm.start_new_db()


@app.get("/")
def healthcheck() -> Dict[str, str]:
    return {'status': 'healthy'}


@app.get("/state/initial")
def get_initial_game_state() -> GameState:
    sim = Simulator()
    return sim.latest_state


@app.get("/state")
def get_latest_game_state() -> GameState:
    return sim.latest_state


@app.get("/simulate", response_model=GameState)
def simulate_state(game_state: GameState) -> GameState:
    sim.simulate_step(game_state)
    return sim.latest_state


@app.post("/profile/{username}", response_model=Profile)
def create_user(username: str) -> Profile:
    userid = int(time.time())
    profile = Profile(userid, username)
    dm.create_player_profile(db, profile)
    return profile


@app.get("/profile", response_model=List[Profile])
def list_users() -> List[Profile]:
    return dm.list_player_profiles(db)


@app.post("/actionscript", response_model=None)
def validate_script(player_id: int, script_name: str, file: UploadFile = File(...)) -> None:
    ac = ActionScript(player_id, script_name, file)
    dm.create_actionscript(db, ac)


@app.get("/actionscript", response_model=List[ActionScriptResponse])
def list_predefined_actions() -> List[ActionScriptResponse]:
    return dm.list_action_scripts(db)


@app.get("/game/{game_id}", response_model=GameData)
def simulate_state(game_id: int) -> GameData:
    gameid = int(time.time())
    return dm.GameData()


@app.post("/game", response_model=GameData)
def create_game() -> GameData:
    gameid = int(time.time())
    game = GameData()
    dm.create_game(db, game)
    return game


@app.put("/game/{game_id}", response_model=GameData)
def simulate_step(game_id: int) -> GameData:
    game = sim.simulate_step(dm.get_game(db, game_id))
    return game


