from dataclasses import asdict
import random

import requests
from model import PlayerProfile, FindMatchRequest, MatchRequestData, GRID_LENGTH, CellPlacement, \
    InitialPlacementRequest, GameData

num_cells_per_player = 3
site_url = 'http://localhost:8000'
username1 = 'test_user1'
username2 = 'test_user2'
response = requests.post(f'{site_url}/profile/{username1}')
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

fmr1 = FindMatchRequest(user_id=user_id1, action_script_id=0)
fmr2 = FindMatchRequest(user_id=user_id2, action_script_id=0)

fmr1resp = requests.post(f'{site_url}/match', json=asdict(fmr1))
md1 = MatchRequestData(**fmr1resp.json())
fmr2resp = requests.post(f'{site_url}/match', json=asdict(fmr2))
md2 = MatchRequestData(**fmr2resp.json())


available_locs = [(i, j) for i in range(num_cells_per_player) for j in range(num_cells_per_player)]
cell_type_map = {1: 'ATTACK', 0: 'DEFEND'}
p1_placements = []
p2_placements = []
for i in range(len(available_locs)):
    max_index = len(available_locs) - 1
    if max_index == 0:
        break
    x, y = available_locs.pop(random.randint(0, max_index) if max_index > 0 else 0)
    p1_placements.append(
        CellPlacement(
            cell_type=cell_type_map[random.randint(0, 1)],
            team_number=0,
            x_loc=x,
            y_loc=y))

    max_index -= 1
    if max_index == 0:
        break
    x, y = available_locs.pop(random.randint(0, max_index) if max_index > 0 else 0)
    p2_placements.append(
        CellPlacement(
            cell_type=cell_type_map[random.randint(0, 1)],
            team_number=0,
            x_loc=x,
            y_loc=y))


req1 = InitialPlacementRequest(
    user_id=user_id1,
    cell_placements=p1_placements)


req2 = InitialPlacementRequest(
    user_id=user_id2,
    cell_placements=p2_placements)

requests.patch(f'{site_url}/game/{md2.game_id}', json=asdict(req1))
gresp = requests.get(f'{site_url}/game/{md2.game_id}')

requests.patch(f'{site_url}/game/{md2.game_id}', json=asdict(req2))
gresp = requests.get(f'{site_url}/game/{md2.game_id}')

game_data = GameData(**gresp.json())
with open('InsertedGameData.json', 'w') as file:
    file.write(str(game_data))

print('GameId: ', game_data.game_id)
