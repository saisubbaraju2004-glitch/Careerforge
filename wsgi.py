import logging
import os

from waitress import serve

from app import app
from config.config import Config


if __name__ == "__main__":
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())
    serve(app, host=Config.HOST, port=Config.PORT)
