import logging
import os
from datetime import datetime
from config import LOGS_PATH

def setup_logger(guild_name, channel_name):
    now = datetime.now()
    guild_path = os.path.join(LOGS_PATH, guild_name)
    channel_path = os.path.join(guild_path, channel_name)
    os.makedirs(channel_path, exist_ok=True)

    log_file = os.path.join(channel_path, f"{now.strftime('%Y-%m-%d')}.log")
    logger = logging.getLogger(f"{guild_name}-{channel_name}")

    if not logger.hasHandlers():
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        stream_handler = logging.StreamHandler()

        formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger