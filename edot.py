from flask import Flask
import random
import time
import logging
import redis
import os

from dotenv import load_dotenv
load_dotenv()

# disable default flask logger
logger = logging.getLogger("werkzeug")
logger.setLevel(logging.ERROR)

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
logger.addHandler(handler)

# Flask app
app = Flask(__name__)

# Redis client
r = redis.Redis(host='redis', port=6379, db=0)

@app.route("/endpoint1")
def endpoint1():
    logger.info("Received request")

    logger.info("connecting to Redis 20 times")
    for _ in range(20):
        r.get("key1")

    # slow down the request 10% of the time
    if random.randint(0, 9) < 1:
        time.sleep(0.02)
        logger.info("ERR-1000,slow request")
    else:
        logger.info("INFO-1000,fast request")

    try:
        # 10% のリクエストでエラー（捕捉される）
        if random.randint(0, 9) < 1:
            time.sleep(0.1)
            raise RuntimeError("CRITICAL-1000,expected error, will be handled")
    except Exception as e:
        logger.error(e)
        return "CRITICAL-2000,endpoint1, error"

    # さらに 10% は未処理の例外で落とす
    if random.randint(0, 9) < 1:
        time.sleep(0.1)
        raise RuntimeError("unexpected error")

    return __file__

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5011)
