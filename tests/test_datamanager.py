import datamanager as testmodule
import logging
import model

gamestate = model.GameState(0,[])

logging.getLogger().setLevel(logging.DEBUG)

def test_get_game():
    # Arrange
    game_id = 0
    expected_value = model.GameData(**{
        'game_id': game_id,
        'awaiting_p1': True,
        'awaiting_p2': True,
        'max_turns': 100,
        'awaiting_placements': True,
        'p1_user_id': 0,
        'p2_user_id': 1,
        'current_state': {
            'current_turn': 0,
            'player_occupied_cells': []
        }
    })
    dm = testmodule.DataManager()
    thegame = model.GameData(
        game_id=game_id,
        current_state=gamestate,
        awaiting_p1=True,
        awaiting_p2=True,
        awaiting_placements=True,
        p1_user_id=0,
        p2_user_id=1,
        max_turns=100
    )
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
    thegame = model.GameData(
        game_id=game_id,
        awaiting_placements=True,
        current_state=gamestate,
        awaiting_p1=True,
        awaiting_p2=True,
        p1_user_id=0,
        p2_user_id=1,
        max_turns=100
    )
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
    thegame = model.GameData(
        game_id=game_id,
        awaiting_placements=True,
        current_state=gamestate,
        awaiting_p1=True,
        awaiting_p2=True,
        p2_user_id=1,
        p1_user_id=0,
        max_turns=100
    )
    dm.create_game(thegame)
    games = dm.get_games()
    print("Games: %s" % games)
