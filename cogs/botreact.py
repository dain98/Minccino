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
        if ':7roll:' in message2:
            await self.bot.send_message(message.channel,"<:7pain:589695777241301021>")
        if 'i love you <@438239507565903872>' in message2 or 'i love you minccino' in message2 or 'i love u <@438239507565903872>' in message2 or 'i love u minccino' in message2 or 'ily <@438239507565903872>' in message2 or 'ily minccino' in message2 or 'ilu <@438239507565903872>' in message2 or 'ilu minccino' in message2:
            await self.bot.send_message(message.channel,"I love you too, " + message.author.mention + "!!")
            await self.bot.send_file(message.channel,"data/pictures/MinccinoLove.gif")
        if 'its my birthday' in message2 or 'it\'s my birthday' in message2:
            await self.bot.send_message(message.channel,"Oh is it your birthday, " + message.author.mention + "? Happy birthday!! <a:cuddle:527195573292498964>")
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
