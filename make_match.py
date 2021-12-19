from dataclasses import asdict
import random

import requests
from model import PlayerProfile, FindMatchRequest, MatchRequestData, GRID_LENGTH, CellPlacement, \
    InitialPlacementRequest, GameData

num_cells_per_player = 3
site_url = 'http://localhost:8000'
site_url = 'https://www.comp680elgame.tk'
username1 = 'test_user1'
username2 = 'test_user2'
response = requests.post(f'{site_url}/profile/{username1}')
print(response.json())
prof = PlayerProfile(**response.json())
user_id1 = prof.user_id
assert prof.username == username1
response = requests.post(f'{site_url}/profile/{username2}')
prof = PlayerProfile(**response.json())
user_id2 = prof.user_id
assert prof.username == username2

response = requests.get(f'{site_url}/profile')
assert filter(
    lambda x: x.username == username1 and x.user_id == prof.user_id,
    [aprof for aprof in response.json()])
assert filter(
    lambda x: x.username == username2 and x.user_id == prof.user_id,
    [aprof for aprof in response.json()])

fmr1 = FindMatchRequest(user_id=user_id2, action_script_id=0)
fmr2 = FindMatchRequest(user_id=user_id1, action_script_id=0)

fmr1resp = requests.post(f'{site_url}/match', json=asdict(fmr1))
md1 = MatchRequestData(**fmr1resp.json())
fmr2resp = requests.post(f'{site_url}/match', json=asdict(fmr2))
md2 = MatchRequestData(**fmr2resp.json())
gresp = requests.get(f'{site_url}/game/{md2.game_id}')
print('Setup game', gresp.json())
