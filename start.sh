echo Starting game API
uvicorn main:app --host=0.0.0.0 --ssl-keyfile /etc/letsencrypt/live/comp680elgame.tk/privkey.pem --ssl-certfile /etc/letsencrypt/live/comp680elgame.tk/fullchain.pem --port 443 --debug --workers 3
echo Starting chat API
uvicorn chatapi:app --host=0.0.0.0 --port=8000 --debug