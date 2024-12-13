import os

# Base directories
BASE_DIR = os.path.join(os.path.expanduser("C:/Users/jensm"), "Discord_Logging")
LOGS_PATH = os.path.join(BASE_DIR, 'discord_logs')
IMAGES_PATH = os.path.join(BASE_DIR, 'discord_images')
USERS_PATH = os.path.join(BASE_DIR, 'discord_users')

# Create directories if they don't exist
os.makedirs(LOGS_PATH, exist_ok=True)
os.makedirs(IMAGES_PATH, exist_ok=True)
os.makedirs(USERS_PATH, exist_ok=True)
