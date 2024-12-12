import discord
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
AUTHOR_ID = os.getenv('AUTHOR_ID')

# Define the directory for logs and images
logs_path = './discord_logs/test_logs'
images_path = './discord_images'
os.makedirs(logs_path, exist_ok=True)
os.makedirs(images_path, exist_ok=True)

class Client(discord.Client):
    def __init__(self, intents, *args, **kwargs):
        super().__init__(intents=intents, *args, **kwargs)
        self.current_log_file = None
        self.log_file_handler = None
        self.setup_logger()

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
                handlers=[self.log_file_handler, logging.StreamHandler()]
            )

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message received from {message.author}: {message.content}')

        self.setup_logger()

        logging.info(f'[{datetime.now()}] {message.author}: {message.content}')

        # Check for the !log command
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

        # Check if the message has attachments (e.g., images)
        if message.attachments:
            sender_name = message.author.name
            sender_id = message.author.id
            server_name = message.guild.name if message.guild else "DMs"

            # Create a folder for the user if it doesn't exist
            user_folder = f"{images_path}/{sender_name}_{sender_id}"
            os.makedirs(user_folder, exist_ok=True)

            for attachment in message.attachments:
                if attachment.content_type and "image" in attachment.content_type:
                    # Format the image filename
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    image_name = f"{timestamp}_{server_name.replace(' ', '_')}.png"
                    image_path = f"{user_folder}/{image_name}"

                    try:
                        # Save the image to the user's folder
                        await attachment.save(image_path)
                        logging.info(f"Saved image to {image_path}")
                        await message.channel.send(f"Image saved to {user_folder} as {image_name}")
                    except Exception as e:
                        logging.error(f"Error saving image: {e}")
                        await message.channel.send("There was an error saving the image.")

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

client = Client(intents=intents)
client.run(DISCORD_TOKEN)