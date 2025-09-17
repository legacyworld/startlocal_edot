from flask import Flask
import random
import time
import logging
import redis
import os

from dotenv import load_dotenv
load_dotenv()

# OpenTelemetry SDK
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter

# =====================================
# OpenTelemetry Logger 設定
# =====================================

logger_provider = LoggerProvider()

# Collector に gRPC 経由で送信
otlp_exporter = OTLPLogExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317"),
    insecure=True,
)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_exporter))

# Python logging と統合
otel_handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)

# werkzeug の logger を抑制
logging.getLogger("werkzeug").setLevel(logging.ERROR)

# アプリ用 logger
logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)
logger.addHandler(otel_handler)         # OpenTelemetry に送る
logger.addHandler(logging.StreamHandler())  # ローカルにも出す（任意）

# =====================================
# Flask アプリ
# =====================================
app = Flask(__name__)
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
        # 10% のリクエストでエラー
        if random.randint(0, 9) < 1:
            time.sleep(0.1)
            raise RuntimeError("CRITICAL-1000,expected error, will be handled")
    except Exception as e:
        logger.error(e)
        return "CRITICAL-2000,endpoint1, error"

    if random.randint(0, 9) < 1:
        time.sleep(0.1)
        raise RuntimeError("unexpected error")

    return __file__

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5011)
