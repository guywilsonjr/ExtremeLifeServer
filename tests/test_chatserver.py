import pytest
import logging
from components.chat import chatserver
from components.dbaccess import exceptions
from components.dbaccess import db
import pymysql


logging.getLogger().setLevel(logging.DEBUG)

MOCKED_GAME_ID = 9999999
MOCKED_CHANNEL_NAME = "mocked_channel_name"


@pytest.mark.parametrize('game_id', [MOCKED_GAME_ID])
def test_get_channel_found(setup_db, mock_game_session):
    # Arrange
    session_id = mock_game_session
    channel_name = "test_channel_name"
    expected_value = channel_name
    try:
        db.insert_chat_channel(session_id, channel_name)
    except exceptions.DatabaseError:
        logging.debug("record already inserted: %s, %s" % (session_id, channel_name))
    # Act
    output_value = chatserver.get_channel(session_id)
    # Assert
    assert output_value == expected_value
    # Clean up
    delete_channel_name(MOCKED_GAME_ID)


def test_get_channel_raises_sessionnamenotfound(setup_db):
    # Arrange
    session_id = 42
    ensure_session_not_found(session_id)
    # Assert
    with pytest.raises(exceptions.SessionNameNotFound):
        # Act
        output_value = chatserver.get_channel(session_id)
    delete_channel_name(session_id)


@pytest.mark.parametrize('game_id', [42])
@pytest.mark.parametrize('session_id,channel_name', [(MOCKED_GAME_ID, MOCKED_CHANNEL_NAME)])
def test_get_channel_raises_channelnameerror(setup_db, mock_uuid, mock_game_session, ensure_channel_name_already_exists):
    # Arrange
    session_id = mock_game_session
    channel_name = mock_uuid
    # Assert
    with pytest.raises(exceptions.ChannelNameError):
        # Act
        output_value = chatserver.get_channel(session_id)
        print(output_value)


@pytest.mark.parametrize('game_id', [MOCKED_GAME_ID])
@pytest.mark.parametrize('session_id,channel_name', [(MOCKED_GAME_ID, MOCKED_CHANNEL_NAME)])
def test_get_service_keys_success(setup_db, mock_game_session, ensure_channel_name_already_exists):
    # Arrange
    expected_result = (2, dict)
    # Act
    output = chatserver.get_chat_service_keys(MOCKED_CHANNEL_NAME)
    # Assert
    assert (len(output), type(output)) == expected_result


@pytest.mark.parametrize('game_id', [MOCKED_GAME_ID])
def test_get_service_keys_raiseinvalidkeyrequest(setup_db, mock_game_session):
    # Arrange
    expected_result = (2, dict)
    # Assert
    with pytest.raises(exceptions.InvalidKeyRequest):
        # Act
        output = chatserver.get_chat_service_keys(MOCKED_CHANNEL_NAME)

def ensure_session_not_found(session_id: int):
    from datamanager import DataManager
    logging.debug("Games removed: %s" % DataManager().remove_game(session_id))
    

@pytest.fixture
def mock_game_session(game_id: int):
    from datamanager import DataManager
    import model
    req1 = model.MatchRequestData(player_id=1, request_id=0, action_script_id=100, match_is_complete=None, game_id=None)
    req2 = model.MatchRequestData(player_id=2, request_id=0, action_script_id=200, match_is_complete=None, game_id=None)
    gamestate = model.GameState()
    game = model.GameData(game_id=game_id, player1_req=req1, player2_req=req2, current_state=gamestate)
    dm = DataManager()
    dm.create_game(game)
    yield game_id
    dm.remove_game(game_id)

    
def ensure_session_id_does_not_have_channel(session_id: int):
    with db.execute("DELETE FROM chat.channels WHERE sid=%s", [session_id], True) as curs:
        return curs.fetchall()


@pytest.fixture
def ensure_channel_name_already_exists(session_id, channel_name):
    try:
        with db.execute("INSERT INTO chat.channels (sid, channel_name) VALUES (%s, %s);", 
                        [session_id, channel_name], True) as curs:
            """curs.fetchall()"""
    except pymysql.err.IntegrityError:
        print("Channel name already exists.")
    
    yield
    
    with db.execute("DELETE FROM chat.channels WHERE sid=%s AND channel_name=%s;",
                    [session_id, channel_name], True) as curs:
        """curs.fetchall()"""


def delete_channel_name(session_id):
    with db.execute("DELETE FROM chat.channels WHERE sid=%s", [session_id], True):
        return session_id
