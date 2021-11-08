# import psycopg2
import pymysql
import contextlib
import configparser
import logging
from typing import List, Any, Dict
from components.dbaccess import exceptions
from os import environ


def setup_db(config_path: str):
    """Set DB config from file."""
    # Maybe use IP-based security instead (or both).
    # Save host info to environment.
    # Targetting to use RDS database.
    if not environ.get("CHAT_HOST"):
        config = parse_configuration_file(config_path)
        environ["CHAT_HOST"] = config.get("host", "Not Set")
        # DBNAME = config.get("dbname")
        environ["CHAT_DBNAME"] = config.get("dbname")
        # PORT = config.get("port")
        environ["CHAT_PORT"] = config.get("port")
        # USER = config.get("user")
        environ["CHAT_USER"] = config.get("user")
        # PASSWORD = config.get("password")
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


def get_service_keys() -> str:
    setup_db('configs/db_config')
    with execute("SELECT var_value FROM chat.configurations "
                 "WHERE var_name='service_keys' LIMIT 1;") as curs:
        return curs.fetchone()[0]


def get_game_session_id(sessionname: str) -> str:
    with execute("SELECT id FROM game.sessions WHERE session_name=%s", [sessionname]) as db:
        try:
            sid = db.fetchone()[0]
            logging.debug("Session ID: %s" % sid)
            return sid
        except TypeError as err:
            raise exceptions.SessionNameNotFound("Session name not found: %s" % sessionname)


def get_channel_name_using_session_id(sessionid: str) -> str:
    try:
        with execute("SELECT channel_name FROM chat.channels WHERE sid=%s;", 
                        [sessionid]) as db:
            return db.fetchone()[0]
            # channel_name = res[0] if res else None
    except TypeError as err:
        logging.debug(err)


def insert_chat_channel(sessionid: str, channelname: str, commit: bool=True) -> str:
    with execute("INSERT INTO chat.channels (sid, channel_name) VALUES (%s, %s);", 
                 [sessionid, channelname], commit):
        return channelname
