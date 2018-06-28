import discord
import asyncio
from .utils.dataIO import dataIO
from string import ascii_letters
from .utils import checks
import os
import re
import aiohttp
import urllib.request
import pytesseract
from PIL import Image
from discord.ext import commands

class Imagetotext:
    """Image to text!!"""

    def __init__(self, bot):
        self.bot = bot
        self.header = {"User-Agent": "User_Agent"}

    async def message_triggered(self, message):
        if 'http://zenith.blue/i/' in message.content:
            filename = message.content.split('/')[-1]
            urllib.request.urlretrieve(message.content, "data/imagetotext/" + filename)
            original_image = Image.open("data/imagetotext/" + filename)
            # os.remove("data/imagetotext/" + filename)
            info = pytesseract.image_to_string(original_image).split('\n')

            for text in info:
                if len(text) != 0:
                    await self.bot.send_message(message.channel,text)

def setup(bot):
    print("setting up...")
    n = Imagetotext(bot)
    bot.add_listener(n.message_triggered, "on_message")
    bot.add_cog(n)
