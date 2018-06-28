import discord
import asyncio
from .utils.dataIO import dataIO
from string import ascii_letters
from .utils import checks
import os
import re
import aiohttp
import random
from discord.ext import commands
from random import uniform

class Botreact:
    """Aww what a cute bot"""

    def __init__(self,bot):
        self.bot = bot
        self.header = {"User-Agent": "User_Agent"}

    async def message_triggered(self, message):
        message2 = message.content.lower()
        if 'good bot' in message2:
            await self.bot.send_message(message.channel, "<:yayy:444933813043462145>")
        if 'bad bot' in message2:
            await self.bot.send_message(message.channel, ":[")

def setup(bot):
    print("setting up...")
    n = Botreact(bot)
    bot.add_listener(n.message_triggered, "on_message")
    bot.add_cog(n)
