import datamanager as testmodule
import logging
import model

req1 = model.MatchRequestData(user_id=1, username='testusername1', request_id=0, action_script_id=100, is_match_complete=None, game_id=None)
req2 = model.MatchRequestData(user_id=2, username='testusername2', request_id=0, action_script_id=200, is_match_complete=None, game_id=None)
gamestate = model.GameState(0,[])

logging.getLogger().setLevel(logging.DEBUG)

def test_get_game():
    # Arrange
    game_id = 0
    expected_value = model.GameData(**{
        'game_id': game_id,
        'awaiting_p1_placment': True,
        'awaiting_p2_placment': True,
        'player1_req': {
            'user_id': 1,
            'username': 'testusername1',
            'request_id': 0,
            'action_script_id': 100,
            'is_match_complete': None,
            'game_id': None
        },
        'player2_req': {
            'user_id': 2,
            'username': 'testusername2',
            'request_id': 0,
            'action_script_id': 200,
            'is_match_complete': None,
            'game_id': None
        },
        'current_state': {
            'current_turn': 0,
            'player_occupied_cells': []
        }
    })
    dm = testmodule.DataManager()
    thegame = model.GameData(game_id=game_id, player1_req=req1, player2_req=req2, current_state=gamestate)
    dm.create_game(thegame)
    # Act
    output_value = dm.get_game(game_id)
    logging.debug(repr(output_value))
    # Assert
    assert expected_value == output_value
    # Clean up
    print(f"removed database ids: {dm.remove_game(game_id)}")


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
    print(f"removed database ids: {dm.remove_game(game_id)}")


def test_validate_game_id_invalidated():
    # Arrange
    game_id = 0
    expected_value = False
    dm = testmodule.DataManager()
    print(f"removed database ids: {dm.remove_game(game_id)}")
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
