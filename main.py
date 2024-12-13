import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Intents setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

# Initialize bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Load cogs dynamically
async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and filename != '__init__.py':
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"Loaded extension: {filename}")
            except Exception as e:
                print(f"Failed to load extension {filename}: {e}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

# Main function to start the bot
async def main():
    async with bot:
        await load_extensions()
        await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())