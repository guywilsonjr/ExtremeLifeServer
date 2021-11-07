import pytest
import logging
from components.dbaccess import db


logging.getLogger().setLevel(logging.DEBUG)


def test_setup_db_pass():
    # Arrange
    config_file = "configs/db_config"
    expected_result = {"host": "localhost", "port": '', "dbname": '',
                       "user": 'chatmanager', "password": 'chatpassword'}
    # Act
    output = db.setup_db(config_file)
    # Assert
    assert output == expected_result


def test_execute_validquery(setup_db):
    # Arrange
    expected_result = (("service_keys", 
                        "pubplaceholderkey:subplaceholderkey"),)
    # Act
    with db.execute("SELECT * FROM chat.configurations;") as curs:
        configs = curs.fetchall()
    # Assert
    assert configs == expected_result


def test_execute_invalidquery(setup_db):
    # Arrange
    expected_exception = db.pymysql.OperationalError
    # Assert
    with pytest.raises(expected_exception):
        # Act
        with db.execute("SELECT * FROM table_that_does_not_exist;") as res:
            pass


def test_get_service_keys(setup_db):
    # Arrange
    expected_result = ("pubplaceholderkey:subplaceholderkey")
    #Assert
    output = db.get_service_keys()
    # Assert
    assert output == expected_result


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