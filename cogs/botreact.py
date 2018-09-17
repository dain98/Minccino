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
        if 'all aboard the hype train' in message2:
            await self.bot.send_message(message.channel, "<a:hypetrain:450609914705084416><a:hypetrain:450609914705084416><a:hypetrain:450609914705084416><a:hypetrain:450609914705084416><a:hypetrain:450609914705084416><a:hypetrain:450609914705084416><a:hypetrain:450609914705084416>")
        if 'alexa play honesty' in message2:
            await self.bot.send_message(message.channel, "ɴᴏᴡ ᴘʟᴀʏɪɴɢ: GYZE - HONESTY")
            await self.bot.send_message(message.channel, "─────────────────:white_circle:─────────────")
            await self.bot.send_message(message.channel, "◄◄⠀▐▐ ⠀►►⠀⠀ ⠀ 3:4𝟾 / 5:02 ⠀ ───○ :loud_sound:⠀ ᴴᴰ :gear:")
        if 'alexa play despacito' in message2:
            await self.bot.send_message(message.channel, "ɴᴏᴡ ᴘʟᴀʏɪɴɢ: Luis Fonsi - Despacito ft. Daddy Yankee")
            await self.bot.send_message(message.channel, "───────────────────────────:white_circle:───")
            await self.bot.send_message(message.channel, "◄◄⠀▐▐ ⠀►►⠀⠀ ⠀ 3:4𝟾 / 4:41 ⠀ ───○ :loud_sound:⠀ ᴴᴰ :gear:")
def setup(bot):
    print("setting up...")
    n = Botreact(bot)
    bot.add_listener(n.message_triggered, "on_message")
    bot.add_cog(n)
