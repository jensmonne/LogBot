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

    # If the user doesn't exist in the data, initialize an empty structure
    if user_id not in users_info:
        users_info[user_id] = {
            'name': member.name,
            'guilds': {}  # Key will be guild_name, value will hold the nicknames and statuses for that guild
        }

    # Check if this user is already in this guild
    if guild_name not in users_info[user_id]['guilds']:
        users_info[user_id]['guilds'][guild_name] = {
            'nicknames': [],
            'statuses': []
        }

    # Append the current nickname and status to the guild's data
    if member.nick:
        users_info[user_id]['guilds'][guild_name]['nicknames'].append(member.nick)
    if member.activity:
        users_info[user_id]['guilds'][guild_name]['statuses'].append(str(member.activity.name))
    else:
        users_info[user_id]['guilds'][guild_name]['statuses'].append("No custom status")

    # Save the updated data to the user's JSON file
    with open(os.path.join(USERS_PATH, f"{user_id}.json"), 'w') as f:
        json.dump(users_info[user_id], f, indent=4)
