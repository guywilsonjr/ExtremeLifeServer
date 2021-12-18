#!/usr/bin/env bash


echo Starting game API
screen -dmS "gameAPI" bash -c '/home/ubuntu/ExtremeLifeServer/venv/bin/uvicorn main:app --host=0.0.0.0 --ssl-keyfile /etc/letsencrypt/live/comp680elgame.tk/privkey.pem --ssl-certfile /etc/letsencrypt/live/comp680elgame.tk/fullchain.pem --port 443 --debug --workers 3; exec bash'


echo Starting chat API
screen -dmS "chatAPI" bash -c '/home/ubuntu/ExtremeLifeServer/venv/bin/uvicorn chatapi:app --host=0.0.0.0 --ssl-keyfile /etc/letsencrypt/live/comp680elgame.tk/privkey.pem --ssl-certfile /etc/letsencrypt/live/comp680elgame.tk/fullchain.pem --port=8000 --debug; exec bash'