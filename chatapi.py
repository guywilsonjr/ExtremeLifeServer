from fastapi import FastAPI
from typing import Dict
from components.chat import chatserver

app = FastAPI()
chatserver.db.setup_db("configs/db_config")


@app.get("/")
def healthcheck() -> Dict[str, str]:
    return {'status': 'healthy'}


@app.get("/getchannel")
def get_channel(sname: str) -> str:
    """Get chat channel name using session name."""
    channel_name = chatserver.get_channel(sname)
    return channel_name


@app.get("/getkeys")
def get_keys() -> Dict[str, str]:
    """Get keys for chat service."""
    # Consider using encryption to prevent leaking keys to users.
    keys = chatserver.get_chat_service_keys()
    return keys