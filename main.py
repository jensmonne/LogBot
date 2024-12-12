import discord
import asyncio
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
AUTHOR_ID = os.getenv('AUTHOR_ID')

logs_path = './discord_logs/test_logs'
images_path = './discord_images'
users_path = './discord_users'
os.makedirs(logs_path, exist_ok=True)
os.makedirs(images_path, exist_ok=True)
os.makedirs(users_path, exist_ok=True)

class Client(discord.Client):
    def __init__(self, intents, *args, **kwargs):
        super().__init__(intents=intents, *args, **kwargs)
        self.current_log_file = None
        self.log_file_handler = None
        self.setup_logger()
        self.users_info = {}
        self.load_user_data()

    def setup_logger(self):
        now = datetime.now()
        filename = f'{logs_path}/discord_{now.strftime("%Y-%m-%d_%H")}.log'
        
        if self.current_log_file != filename:
            self.current_log_file = filename

            with open(self.current_log_file, 'a') as file:
                pass

            if self.log_file_handler:
                logging.getLogger('discord').removeHandler(self.log_file_handler)
                self.log_file_handler.close()

            self.log_file_handler = logging.FileHandler(filename=self.current_log_file, encoding='utf-8', mode='a')

            logging.basicConfig(
                level=logging.INFO,
                handlers=[self.log_file_handler, logging.StreamHandler()],
                format='%(message)s'
            )

    def load_user_data(self):
        """Load user data from files to retain past nicknames and logs"""
        for filename in os.listdir(users_path):
            if filename.endswith('.txt'):
                user_id = filename.split('.')[0]
                user_file_path = os.path.join(users_path, filename)

                with open(user_file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if len(lines) > 0:
                        user_name = lines[0].split(":")[1].strip()
                        nickname = lines[4].split(":")[1].strip()
                        status = lines[2].split(":")[1].strip()
                        custom_status = lines[3].split(":")[1].strip()
                        past_nicknames = lines[5].split(":")[1].strip().split(", ")

                        self.users_info[int(user_id)] = {
                            'name': user_name,
                            'nickname': nickname,
                            'status': status,
                            'custom_status': custom_status,
                            'nicknames': past_nicknames
                        }
                        
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        self.bot_loop_task = asyncio.create_task(self.repeating_task())

    async def on_message(self, message):
        print(f'Message received from {message.author}: {message.content}')

        self.setup_logger()

        logging.info(f'[{datetime.now()}] {message.author}: {message.content if message.content else "Send a File"}')

        if message.content.startswith('!log'):
            if message.author.id == int(AUTHOR_ID):
                if self.current_log_file:
                    try:
                        await message.channel.send(
                            content="Here is your log file:",
                            file=discord.File(self.current_log_file)
                        )
                    except Exception as e:
                        logging.error(f"Error sending log file: {e}")
                        await message.channel.send("There was an error sending the log file.")
                else:
                    await message.channel.send("No log file is currently available.")
            else:
                await message.channel.send("You don't have permission to use this command.")

        if message.attachments:
            sender_name = message.author.name
            sender_id = message.author.id
            server_name = message.guild.name if message.guild else "DMs"

            user_folder = f"{images_path}/{sender_name}_{sender_id}"
            os.makedirs(user_folder, exist_ok=True)

            for attachment in message.attachments:
                if attachment.content_type and "image" in attachment.content_type:
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    image_name = f"{timestamp}_{server_name.replace(' ', '_')}.png"
                    image_path = f"{user_folder}/{image_name}"

                    try:
                        await attachment.save(image_path)
                        logging.info(f"[{datetime.now()}] Saved image to {image_path}")
                    except Exception as e:
                        logging.error(f"[{datetime.now()}] Error saving image: {e}")
                        await message.channel.send("There was an error saving the image.")

    async def repeating_task(self):
        while True:
            await asyncio.sleep(120)

            logging.info(f"[{datetime.now()}] Logging users")

            if self.guilds:
                for guild in self.guilds:
                    for member in guild.members:
                        user_id = member.id
                        user_name = member.name
                        nickname = member.nick if member.nick else "No nickname"
                        status = str(member.status)
                        custom_status = member.activity.name if member.activity else "No custom status"

                        if user_id not in self.users_info:
                            self.users_info[user_id] = {'name': user_name, 'nickname': nickname, 'status': status, 'custom_status': custom_status, 'nicknames': []}
                        else:
                            if self.users_info[user_id]['nickname'] != nickname:
                                self.users_info[user_id]['nicknames'].append(self.users_info[user_id]['nickname'])
                                self.users_info[user_id]['nickname'] = nickname
                            if self.users_info[user_id]['status'] != status:
                                self.users_info[user_id]['status'] = status
                            if self.users_info[user_id]['custom_status'] != custom_status:
                                self.users_info[user_id]['custom_status'] = custom_status

                        user_file_path = os.path.join(users_path, f'{user_id}.txt')
                        with open(user_file_path, 'w', encoding='utf-8') as f:
                            f.write(f"Name: {user_name}\n")
                            f.write(f"User ID: {user_id}\n")
                            f.write(f"Current Status: {status}\n")
                            f.write(f"Custom Status: {custom_status}\n")
                            f.write(f"Current Nickname: {nickname}\n")
                            f.write(f"Past Nicknames: {', '.join(self.users_info[user_id]['nicknames'])}\n")
                            f.write(f"Logs:\n")

            self.setup_logger()

    async def on_member_update(self, before, after):
        """Called when a member's information is updated (e.g., nickname change)"""
        if before.nick != after.nick:
            logging.info(f"Nickname changed for {after.name} ({after.id}): {before.nick} -> {after.nick}")
        
        if before.status != after.status:
            logging.info(f"Status changed for {after.name} ({after.id}): {before.status} -> {after.status}")

            user_file_path = os.path.join(users_path, f'{after.id}.txt')
            with open(user_file_path, 'a', encoding='utf-8') as f:
                f.write(f"Status updated: {after.status} on {datetime.now()}\n")
                f.write(f"Custom Status: {after.activity.name if after.activity else 'No custom status'}\n")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

client = Client(intents=intents)
client.run(DISCORD_TOKEN)