# import psycopg2
import pymysql
import contextlib
import configparser
import logging
from os import environ
from typing import List, Any, Dict
from components.dbaccess import exceptions


def setup_db(config_path: str):
    """Set DB config from file."""
    # Maybe use IP-based security instead (or both).
    # Save host info to environment.
    # Targetting to use RDS database.
    if not environ.get("CHAT_HOST"):
        config = parse_configuration_file(config_path)
        environ["CHAT_HOST"] = config.get("host", "Not Set")
        environ["CHAT_DBNAME"] = config.get("dbname")
        environ["CHAT_PORT"] = config.get("port")
        environ["CHAT_USER"] = config.get("user")
        environ["CHAT_PASSWORD"] = config.get("password")
    
    if environ["CHAT_HOST"] == "Not Set":
        raise Exception("Host for chat database is not set.")


def parse_configuration_file(config_path: str) -> Dict[str, str]:
    """Open configuration file at given path and return values as a dictionary."""
    config = dict()
    parser = configparser.ConfigParser()
    parser.read(config_path)
    for s in parser:
        for c in parser[s]:
            config[c] = parser[s][c]
    return config


def _get_chat_db_config_from_environ():
    return {
        'host': environ["CHAT_HOST"],
        "user": environ["CHAT_USER"],
        "database": environ["CHAT_DBNAME"],
        "password": environ["CHAT_PASSWORD"],
        "port": environ["CHAT_PORT"]
    }


@ contextlib.contextmanager
def execute(query: str, params: List[Any]=[], commit: bool=None):
    with pymysql.connect(**_get_chat_db_config_from_environ()) as conn:
        with conn.cursor() as curs:
            query = curs.mogrify(query, params)
            logging.debug("QUERY: %s" % query)
            curs.execute(query)
            yield curs
        if commit:
            conn.commit()


def get_service_keys(channelname: str) -> str:
    """Query chat configuration table for chat service keys."""
    setup_db('configs/db_config')
    with execute(
            "SELECT var_value FROM chat.channels JOIN chat.configurations "
            "WHERE var_name='service_keys' AND channel_name=%s LIMIT 1;",
            [channelname]) as curs:
        res = curs.fetchone()
        if res:
            return res[0]
    raise exceptions.InvalidKeyRequest("Something went wrong when requesting service keys.")


def get_channel_name_using_session_id(sessionid: str) -> str:
    """Query chat channels table for channel name using session ID."""
    try:
        with execute("SELECT channel_name FROM chat.channels WHERE sid=%s;", [sessionid]) as db:
            channel_name = db.fetchone()
            logging.debug("Channel Name: %s" % channel_name)
            return channel_name[0]
    except TypeError as err:
        logging.debug(err)
        raise exceptions.ChannelNameError("Session ID not found: %s" % sessionid)


def insert_chat_channel(sessionid: str, channelname: str, commit: bool=True) -> str:
    """Insert chat channel to chat channels table when new channel is created."""
    try:
        with execute("INSERT INTO chat.channels (sid, channel_name) VALUES (%s, %s);", 
                     [sessionid, channelname], commit):
            return channelname
    except Exception as ex:
        logging.error("Exception while inserting chat channel: %s" % ex)
        raise exceptions.DatabaseError(
            "Session ID: %s, Channel Name: %s, Commit: %s" % (sessionid, channelname, commit))


def remove_chat_channel(sessionid: str) -> str:
    """Remove channel associated to session ID."""
    with execute("DELETE FROM chat.channels WHERE sid=%s "
                    "RETURNING channel_name AS deleted_channel;", [sessionid], True) as curs:
        res = curs.fetchall()
    if res:
        return res[0]
    raise exceptions.SessionNameNotFound("Channel associated to the session ID was not found.")
