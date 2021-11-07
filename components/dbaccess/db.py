# import psycopg2
import pymysql
import contextlib
import configparser
import logging
from typing import List, Any, Dict
from components.dbaccess import exceptions
# Using RDS database.

# Get db info from protected file
HOST = None
DBNAME = None
PORT = None
# Maybe use IP-based security instead (or both).
USER = None
PASSWORD = None


def setup_db(config_path: str) -> Dict[str, str]:
    """Set DB config from file."""
    global HOST, DBNAME, PORT, USER, PASSWORD
    config = dict()
    parser = configparser.ConfigParser()
    parser.read(config_path)
    for s in parser:
        for c in parser[s]:
            config[c] = parser[s][c]
    HOST = config.get("host")
    DBNAME = config.get("dbname")
    PORT = config.get("port")
    USER = config.get("user")
    PASSWORD = config.get("password")
    return config


@ contextlib.contextmanager
def execute(query: str, params: List[Any]=[], commit: bool=None):
    with pymysql.connect(host=HOST, database=DBNAME, user=USER, password=PASSWORD, port=PORT) as conn:
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
