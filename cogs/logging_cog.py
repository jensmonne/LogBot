import discord
from discord.ext import commands, tasks
from datetime import datetime
import logging
from utils.logger import setup_logger
from utils.user_data import load_user_data, save_user_data
import os

class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users_info = load_user_data()

    @tasks.loop(hours=1)  # This will run every hour
    async def save_data(self):
        for guild in self.bot.guilds:
            for member in guild.members:
                save_user_data(member, self.users_info)
        print("User data saved")

    @commands.Cog.listener()
    async def on_ready(self):
        self.save_data.start()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        guild_name = message.guild.name if message.guild else "DMs"
        channel_name = message.channel.name if message.guild else "DMs"
        
        # Setup logger
        logger = setup_logger(guild_name, channel_name)

        # Log the message
        logger.info(f"[{datetime.now()}] {message.author}: {message.content if message.content else 'Sent a File'}")

        # Handle commands
        if message.content.startswith('!log'):
            if message.author.id == int(os.getenv('AUTHOR_ID')):  # Ensure this check is secure
                await self.send_log_file(message)
            else:
                await message.channel.send("You don't have permission to use this command.")

    async def send_log_file(self, message):
        guild_name = message.guild.name
        channel_name = message.channel.name
        log_file = setup_logger(guild_name, channel_name).handlers[0].baseFilename

        if os.path.exists(log_file):
            await message.channel.send(content="Here is your log file:", file=discord.File(log_file))
        else:
            await message.channel.send("No log file is currently available.")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.nick != after.nick:
            logging.info(f"Nickname changed for {after.name}: {before.nick} -> {after.nick}")

        if before.status != after.status:
            logging.info(f"Status changed for {after.name}: {before.status} -> {after.status}")

        # Save user data for the updated member
        save_user_data(after, self.users_info)

async def setup(bot):
    await bot.add_cog(LoggingCog(bot))
