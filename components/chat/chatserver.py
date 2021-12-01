import os
import logging
from uuid import uuid4
from typing import Dict

from components.dbaccess import exceptions
from components.dbaccess import db


NUM_OF_ATTEMPTS = 3


def get_channel(session_name: str) -> str:
    """Query DB with sessionid to get channel name, if none create."""
    # we can probably cut out session name and just recieve session id/name for simplicity.
    sid = db.get_game_session_id(session_name)

    channel_name = db.get_channel_name_using_session_id(sid)
    if channel_name:
        return channel_name
    
    # attempt to create unique channel_name upto NUM_OF_ATTEMPTS times.
    for _ in range(NUM_OF_ATTEMPTS):
        channel_name = uuid4().hex
        logging.debug("Generated channel_name: %s" % channel_name)
        try:
            return db.insert_chat_channel(sid, channel_name)
        # assuming primary key issue
        except db.pymysql.Error as err:
            logging.debug("Error while inserting channel name into channels table: %s" % err)        
    
    # could not generate a unique channel name...
    raise exceptions.ChannelNameError("Unique channel name not generated (Session ID %s)." % session_name)


def get_chat_service_keys() -> Dict[str, str]:
    # get service keys from db and send it to requesting client.
    service_keys = db.get_service_keys()
    return {k: v for (k, v) in zip(["pub", "sub"], service_keys.split(':'))}