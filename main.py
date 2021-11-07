import time
from typing import Dict

from fastapi import FastAPI, File, UploadFile

import datamanager as dm
import simulator
from profile import Profile
from simulator import GameState


app = FastAPI()
sim = simulator.Simulator()
db = dm.start_new_db()


@app.get("/")
def healthcheck() -> Dict[str, str]:
    return {'status': 'healthy'}


@app.get("/state/initial")
def get_initial_game_state() -> GameState:
    sim = simulator.Simulator()
    return sim.latest_state


@app.get("/state")
def get_latest_game_state() -> GameState:
    return sim.latest_state


@app.get("/simulate")
def simulate_state(game_state: GameState) -> GameState:
    sim.simulate_step(game_state)
    return sim.latest_state


@app.post("/profile/{username}")
def create_profile(username: str) -> Profile:
    userid = int(time.time())
    profile = Profile(username, userid)
    dm.create_player_profile(db, profile)
    return profile


@app.get("/profile")
def list_profiles() -> GameState:
    return dm.list_player_profiles(db)


@app.post("/actionscript")
def add_actionscript(file: UploadFile = File(...)) -> None:
    return None


"""
    
@app.get("/actionscript")
def simulate_state(game_state: GameState) -> GameState:
    sim.simulate_step(game_state)
    return sim.latest_state


@app.post("/game")
def simulate_state(game_state: GameState) -> GameState:
    sim.simulate_step(game_state)
    return sim.latest_state


@app.patch("/game")
def simulate_state(game_state: GameState) -> GameState:
    sim.simulate_step(game_state)
    return sim.latest_state
"""
