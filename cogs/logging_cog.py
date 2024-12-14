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
        self.authorized_users = [int(uid) for uid in os.getenv('AUTHORIZED_USER_IDS', '').split(',') if uid]
        self.latest_log_message_map = {}

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
            if message.author.id in self.authorized_users:  # Check against the authorized users list
                await self.handle_log_command(message)
            else:
                await message.channel.send("You don't have permission to use this command.")

        elif message.content.startswith('!removelog'):
            if message.author.id in self.authorized_users:  # Ensure authorized users only
                await self.handle_remove_log(message)

    async def handle_log_command(self, message):
        guild_id = message.guild.id if message.guild else None
        if not guild_id:
            return  # Only process in guilds

        guild_name = message.guild.name
        channel_name = message.channel.name
        log_file = setup_logger(guild_name, channel_name).handlers[0].baseFilename

        # Send the log file or notify if not available
        if os.path.exists(log_file):
            bot_message = await message.channel.send(
                content="Here is your log file:", 
                file=discord.File(log_file)
            )
        else:
            bot_message = await message.channel.send("No log file is currently available.")

        # Update the latest message tracking for this guild
        self.latest_log_message_map[guild_id] = (message.id, bot_message.id)

    async def handle_remove_log(self, message):
        guild_id = message.guild.id if message.guild else None
        if not guild_id or guild_id not in self.latest_log_message_map:
            await message.channel.send("No recent log to remove.")
            return

        # Retrieve the latest log-related messages
        user_msg_id, bot_msg_id = self.latest_log_message_map[guild_id]

        # Attempt to delete the tracked messages
        for msg_id in [user_msg_id, bot_msg_id]:
            try:
                msg = await message.channel.fetch_message(msg_id)
                await msg.delete()
            except discord.NotFound:
                pass  # Message might already be deleted

        # Delete the `!removelog` message itself
        await message.delete()

        # Clear the latest log entry for this guild
        del self.latest_log_message_map[guild_id]

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