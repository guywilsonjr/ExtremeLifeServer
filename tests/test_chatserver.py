import pytest
import logging
from components.chat import chatserver
from components.dbaccess import exceptions
from components.dbaccess import db


logging.getLogger().setLevel(logging.DEBUG)


def test_get_channel_found(setup_db):
    # Arrange
    session_name = "test_session_name"
    # Act
    output = chatserver.get_channel(session_name)
    # Assert
    assert output == 'test_channel_name'


def test_get_channel_raises_sessionnamenotfound(setup_db):
    # Arrange
    session_name = "session_name_not_found"
    # ensure_session_name_not_found(session_name)
    # Assert
    with pytest.raises(exceptions.SessionNameNotFound):
        # Act
        output = chatserver.get_channel(session_name)


def test_get_channel_raises_channelnameerror(mock_uuid):
    # Arrange
    session_name = 'mocked_session_name'
    channel_name = mock_uuid
    # Assert
    with pytest.raises(exceptions.ChannelNameError):
        # Act
        output = chatserver.get_channel(session_name)


def test_get_service_keys(setup_db):
    # Arrange
    expected_result = 2
    # Act
    output = chatserver.get_chat_service_keys()
    # Assert
    assert len(output) == expected_result


# def ensure_session_name_not_found(session_name):
#     with db.execute("SELECT id FROM game.sessions "
#                     "WHERE session_name=%s;", [session_name]) as curs:
#         logging.debug(curs.fetchone())