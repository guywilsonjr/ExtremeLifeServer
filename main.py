from typing import Dict, List
from icecream import ic
import time
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from datamanager import DataManager
from model import (
    FindMatchRequest,
    GameData,
    GameState,
    ActionScriptMeta,
    Profile,
    ActionScriptMetaResp,
    MatchRequestData,
    InitialPlacementRequest)
from controller import Controller


ic.configureOutput(includeContext=True)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost.tiangolo.com",
        "https://localhost.tiangolo.com",
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:8000",
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


@app.post("/profile/{username}", response_model=Profile)
def create_user(username: str) -> Profile:
    userid = int(time.time())
    profile = Profile(userid, username)
    dm.create_player_profile(profile)
    return profile


@app.get("/profile", response_model=List[Profile])
def list_users() -> List[Profile]:
    return dm.list_player_profiles()


@app.post("/actionscript", response_model=None)
async def validate_script(script_name: str, file: UploadFile = File(...)) -> None:
    acmr = ActionScriptMetaResp(script_id=int(time.time()), script_name=script_name)
    pathname = script_name + str(int(time.time())) + '.py'
    with open(pathname, 'wb') as acfile:
        acfile.write(await file.read())
    ac = ActionScriptMeta(resp=acmr, path=pathname)
    dm.create_actionscript(ac)
    return acmr


@app.get("/actionscript", response_model=List[ActionScriptMetaResp])
def list_predefined_actions() -> List[ActionScriptMetaResp]:
    return [ActionScriptMetaResp(ac.resp.script_id, ac.resp.script_name) for ac in dm.list_action_scripts()]


@app.get("/game/{game_id}", response_model=GameData)
def simulate_state(game_id: int) -> GameData:
    return dm.get_game(game_id)


@app.put("/game/{game_id}", response_model=GameData)
def simulate_step(game_id: int) -> GameData:
    game = simulator.simulate_step(dm.get_game(game_id))
    return game


@app.patch("/game/{game_id}")
def set_initial_cells(placment: InitialPlacementRequest) -> None:
    simulator.update_placements()


def create_match(req1: FindMatchRequest, req2: FindMatchRequest) -> int:
    new_game_id = int(time.time())
    game_data = GameData(
        game_id=new_game_id,
        player1_req=req1,
        player2_req=req2,
        current_state=GameState())
    dm.create_game(game_data)

    return new_game_id


def process_match(existing_player_req: FindMatchRequest) -> FindMatchRequest:
    existing_reqs = dm.list_match_requests()
    other_player_reqs = list(filter(lambda req: req.request_id != existing_player_req.request_id, existing_reqs))
    existing_player_req = list(
        filter(
            lambda req: req.request_id == existing_player_req.request_id and not req.game_id,
            existing_reqs))[0]

    if other_player_reqs:
        matching_req = other_player_reqs[0] if other_player_reqs else None
        if matching_req:
            if existing_player_req:
                ic(
                    'Found Existing player req\n',
                    existing_player_req,
                    '\n Matching req\n',
                    matching_req)
                new_game_id = create_match(existing_player_req, matching_req)
                ic('Setting new game ids to', new_game_id)
                existing_player_req = MatchRequestData(
                    player_id=existing_player_req.player_id,
                    request_id=existing_player_req.request_id,
                    action_script_id =existing_player_req.action_script_id,
                    match_is_complete=True,
                    game_id=new_game_id
                )
                matching_req = MatchRequestData(
                    player_id=matching_req.player_id,
                    request_id=matching_req.request_id,
                    action_script_id=matching_req.action_script_id,
                    match_is_complete=True,
                    game_id=new_game_id
                )

                dm.update_match_requests(matching_req, existing_player_req)
    return existing_player_req


@app.post("/match", response_model=MatchRequestData)
def request_match(request: FindMatchRequest) -> MatchRequestData:
    existing_req = dm.get_match_request_by_player_id(request.player_id)
    if existing_req:
        return existing_req

    request = dm.create_match_request(request)
    request = process_match(request)
    return request


@app.get("/match/{request_id}", response_model=MatchRequestData)
def request_match(request_id: int) -> List[MatchRequestData]:
    return dm.get_match_request_by_request_id(request_id)






