from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from components.chat import chatserver


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
chatserver.db.setup_db("configs/db_config")


@app.get("/")
def healthcheck() -> Dict[str, str]:
    return {'status': 'healthy'}


@app.get("/getchannel")
def get_channel(sessionid: str) -> str:
    """Get chat channel name using session name."""
    channel_name = chatserver.get_channel(int(sessionid))
    return channel_name


@app.get("/getkeys")
def get_keys(channelname: str) -> Dict[str, str]:
    """Get keys for chat service."""
    # Consider using encryption to prevent leaking keys to users.
    keys = chatserver.get_chat_service_keys(channelname)
    return keys
