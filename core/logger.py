import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "app.log")

formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s"
)

console_handler = logging.StreamHandler()
file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=1_000_000, backupCount=10, encoding='utf-8'
)
file_handler.setFormatter(formatter)

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.propagate = False
