import logging
import os
import socket
import sys

from flask import Flask, jsonify, request

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

APP_PORT = int(os.environ.get("APP_PORT", "5000"))

app = Flask(__name__)

@app.after_request
def log_request(response):
    logger.info("%s %s -> %s", request.method, request.path, response.status_code)
    return response

@app.route("/")
def index():
    return jsonify(message="Hello DevOps", host=socket.gethostname())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=APP_PORT)