import logging
import os
import socket
import sys

import redis
from flask import Flask, jsonify, request

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

APP_PORT = int(os.environ.get("APP_PORT", "5000"))
REDIS_HOST = os.environ.get("REDIS_HOST","localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT",6379))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    socket_connect_timeout=2,
    socket_timeout=2,
    decode_responses=True,
)

app = Flask(__name__)

@app.after_request
def log_request(response):
    logger.info("%s %s -> %s", request.method, request.path, response.status_code)
    return response

@app.route("/")
def index():
    return jsonify(message="Hello DevOps", host=socket.gethostname())

@app.route("/visits")
def visits():
    count = redis_client.incr("visits")
    return jsonify(visits=count)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=APP_PORT)