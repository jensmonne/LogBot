from discord.ext import commands
from datetime import datetime
import os
from config import IMAGES_PATH

class ImageHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.attachments:
            guild_name = message.guild.name if message.guild else "DMs"
            channel_name = message.channel.name if message.guild else "DMs"

            now = datetime.now()
            day_folder = os.path.join(IMAGES_PATH, guild_name, channel_name, str(now.year), f"{now.month:02}", f"{now.day:02}")
            os.makedirs(day_folder, exist_ok=True)

            for attachment in message.attachments:
                if attachment.content_type and "image" in attachment.content_type:
                    image_name = f"{now.strftime('%H-%M-%S')}_{message.author.name}.png"
                    image_path = os.path.join(day_folder, image_name)
                    await attachment.save(image_path)

async def setup(bot):
    await bot.add_cog(ImageHandler(bot))