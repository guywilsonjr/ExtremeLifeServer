from typing import Dict, List
from icecream import ic
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from cells.cell_types import CellType
from datamanager import DataManager
from model import (
    FindMatchRequest,
    GameData,
    PlayerProfile,
    ActionScriptMetaResp,
    MatchRequestData,
    InitialPlacementRequest)
from controller import Controller


ic.configureOutput(includeContext=True)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
simulator = Controller()
dm = DataManager()


@app.get("/")
def healthcheck() -> Dict[str, str]:
    return {'status': 'healthy'}


@app.post("/profile/{username}", response_model=PlayerProfile)
def create_profile(username: str) -> PlayerProfile:
    return simulator.create_user(username)


@app.get("/profile", response_model=List[PlayerProfile])
def list_users() -> List[PlayerProfile]:
    return dm.list_player_profiles()


@app.get("/cell/types", response_model=List[PlayerProfile])
def list_users() -> List[PlayerProfile]:
    return [cell_type.value for cell_type in CellType]


@app.post("/actionscript", response_model=None)
def validate_script(script_name: str, file: UploadFile = File(...)) -> None:
    acmr = simulator.create_action_script(script_name, file)
    return acmr


@app.get("/actionscript", response_model=List[ActionScriptMetaResp])
def list_predefined_actions() -> List[ActionScriptMetaResp]:
    return [ActionScriptMetaResp(ac.resp.action_script_id, ac.resp.script_name) for ac in dm.list_action_scripts()]


@app.get("/game/{game_id}")
def simulate_state(game_id: int) -> GameData:
    return {
    "game_data": {
        "grid_length": 2,
        "grid_height": 2,
        "player_cells": [
            {
                "x_loc": 2,
                "y_loc": 2,
                "team_number": -1, # red
                "life": 1
            },
            {
                "x_loc": 0,
                "y_loc": 0,
                "team_number": 1, # green
                "life": 1
            },
            {
                "x_loc": 1,
                "y_loc": 1,
                "team_number": -1, # red
                "life": 1
            },
            {
                "x_loc": 0,
                "y_loc": 1,
                "team_number": 1, # green
                "life": 1
            }
        ]
    }
}


@app.put("/game/{game_id}", response_model=GameData)
def NOT_DONE_simulate_next_step(game_id: int) -> GameData:
    game = simulator.simulate_next_state(game_id)
    return game


@app.patch("/game/{game_id}")
def set_initial_cells(game_id: int, placements: InitialPlacementRequest) -> Dict[str, str]:
    simulator.update_placements(game_id, placements)
    return {'Message': 'OK'}


@app.post("/match", response_model=MatchRequestData)
def request_match(request: FindMatchRequest) -> MatchRequestData:
    match_request = simulator.process_match(request)
    return match_request


@app.get("/match/{request_id}", response_model=MatchRequestData)
def request_match(request_id: int) -> List[MatchRequestData]:
    return dm.get_match_request_by_request_id(request_id)

