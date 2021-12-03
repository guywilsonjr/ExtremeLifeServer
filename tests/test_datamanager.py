import datamanager as testmodule
import logging
import model

req1 = model.MatchRequestData(player_id=1, request_id=0, action_script_id=100, match_is_complete=None, game_id=None)
req2 = model.MatchRequestData(player_id=2, request_id=0, action_script_id=200, match_is_complete=None, game_id=None)
gamestate = model.GameState()

logging.getLogger().setLevel(logging.DEBUG)

def test_get_game():
    # Arrange
    game_id = 0
    expected_value = {
        'game_id': game_id, 'player1_req': {'player_id': 1, 'request_id': 0, 'action_script_id': 100, 'match_is_complete': None, 'game_id': None}, 'player2_req': {'player_id': 2, 'request_id': 0, 'action_script_id': 200, 'match_is_complete': None, 'game_id': None}, 'current_state': {'current_turn': 0, 'cell_grid': [[None, None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None, None], [
        None, None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None, None]]}}
    dm = testmodule.DataManager()
    thegame = model.GameData(game_id=game_id, player1_req=req1, player2_req=req2, current_state=gamestate)
    dm.create_game(thegame)
    # Act
    output_value = dm.get_game(game_id)
    logging.debug(repr(output_value))
    # Assert
    assert expected_value == output_value
    # Clean up
    print(f"removed game ids: {dm.remove_game(game_id)}")

def test_validate_game_id_validated():
    # Arrange
    game_id = 0
    expected_value = True
    dm = testmodule.DataManager()
    thegame = model.GameData(game_id=game_id, player1_req=req1, player2_req=req2, current_state=gamestate)
    dm.create_game(thegame)
    # Act
    output_value = dm.validate_game_id(game_id)
    # Assert
    assert output_value == expected_value
    # Clean up
    print(f"removed game ids: {dm.remove_game(game_id)}")

def test_validate_game_id_invalidated():
    # Arrange
    game_id = 0
    expected_value = False
    dm = testmodule.DataManager()
    print(f"removed game ids: {dm.remove_game(game_id)}")
    # Act
    output_value = dm.validate_game_id(game_id)
    print(f"output_value: {output_value}")
    # Assert
    assert output_value == expected_value
    # Clean up

def test_get_games():
    dm = testmodule.DataManager()
    game_id = 99
    thegame = model.GameData(game_id=game_id, player1_req=req1, player2_req=req2, current_state=gamestate)
    dm.create_game(thegame)
    games = dm.get_games()
    print("Games: %s" % games)
    