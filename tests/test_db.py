import pytest
import logging
from components.dbaccess import db
from os import environ


logging.getLogger().setLevel(logging.DEBUG)


def test_setup_db_pass():
    # Arrange
    config_file = "configs/db_config"
    expected_result = {
        "host": "localhost", 
        "port": '', 
        "database": '',
        "user": "chatmanager", 
        "password": "chatpassword"}
    db.setup_db(config_file)
    # Act
    output = db._get_chat_db_config_from_environ()
    # Assert
    assert output == expected_result
    # Cleanup
    reset_environ_db_chat_config()


def reset_environ_db_chat_config():
    """Remove values from environment variables after test."""
    del environ["CHAT_HOST"]
    del environ["CHAT_DBNAME"]
    del environ["CHAT_USER"]
    del environ["CHAT_PASSWORD"]
    del environ["CHAT_PORT"]


def test_execute_validquery(setup_db):
    # Arrange
    expected_result = (("service_keys", 
                        "servicekeystring"),)
    # Act
    with db.execute("SELECT * FROM chat.configurations;") as curs:
        configs = curs.fetchall()
    # Assert
    assert configs[0][0] == expected_result[0][0]


def test_execute_invalidquery(setup_db):
    # Arrange
    expected_exception = db.pymysql.OperationalError
    # Assert
    with pytest.raises(expected_exception):
        # Act
        with db.execute("SELECT * FROM table_that_does_not_exist;") as res:
            pass


# def test_get_service_keys(setup_db):
#     # Arrange
#     expected_result = ("pubplaceholderkey:subplaceholderkey")
#     #Assert
#     output = db.get_service_keys()
#     # Assert
#     assert output == expected_result


def test_get_game_session_id(setup_db):
    # Arrange
    sessionname = "test_session_name"
    expected_result = 1
    # Act
    output = db.get_game_session_id(sessionname)
    # Assert
    assert output == expected_result


def test_get_channel_name_using_session_id(setup_db):
    # Arrange
    sessionid = 1
    expected_result = "test_channel_name"
    # Act
    output = db.get_channel_name_using_session_id(sessionid)
    # Assert
    assert output == expected_result


def test_insert_chat_channel(setup_db):
    # Arrange
    sessionid = 2
    channelname = "insert_new_channel"
    expected_result = channelname
    # Act
    output = db.insert_chat_channel(sessionid, channelname, True)
    # Assert
    assert output == expected_result
    # Cleanup (until a better solution is found)
    with db.execute("DELETE FROM chat.channels WHERE sid=%s", sessionid, True):
        # with required to operate the context manager decorated function.
        pass