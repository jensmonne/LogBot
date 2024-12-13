import os
import json
from config import USERS_PATH

def load_user_data():
    users_info = {}
    for filename in os.listdir(USERS_PATH):
        if filename.endswith('.json'):
            with open(os.path.join(USERS_PATH, filename), 'r') as f:
                users_info[filename.split('.')[0]] = json.load(f)
    return users_info

def save_user_data(member, users_info):
    user_id = str(member.id)
    guild_name = member.guild.name
    data = {
        'name': member.name,
        'nickname': member.nick,
        'status': str(member.status),
        'custom_status': member.activity.name if member.activity else "No custom status",
        'guild': guild_name,
    }
    users_info[user_id] = data
    with open(os.path.join(USERS_PATH, f"{user_id}.json"), 'w') as f:
        json.dump(data, f, indent=4)