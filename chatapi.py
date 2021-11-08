from fastapi import FastAPI
from typing import Dict
from components.chat import chatserver

app = FastAPI()


@app.get("/")
def healthcheck() -> Dict[str, str]:
    return {'status': 'healthy'}


@app.get("/getchannel")
def get_channel(session_name: str) -> str:
    channel_name = chatserver.get_channel(session_name)
    return channel_name


@app.get("/getkeys")
def get_keys() -> Dict[str, str]:
    keys = chatserver.get_chat_service_keys()
    return keys