import discord
import asyncio
from .utils.dataIO import dataIO
from string import ascii_letters
from .utils import checks
import os
import re
import aiohttp
from discord.ext import commands
import datetime
from random import uniform

class Coolstuff:
    """Just testing some stuff"""

    def __init__(self,bot):
        self.bot = bot
        self.header = {"User-Agent": "User_Agent"}

    @commands.command(pass_context=True)
    async def avatar(self,ctx,user: discord.User):
        await self.bot.say("https://cdn.discordapp.com/avatars/{}/{}.jpg?size=1024".format(user.id,user.avatar))

    @commands.command(pass_context=True)
    async def timeutc(self,ctx):
        time = datetime.datetime.utcnow()
        await self.bot.send_message(ctx.message.channel,"The current time is **{}/{}/{} {:02d}:{:02d}** UTC.".format(time.month,time.day,time.year,time.hour,time.minute))
def setup(bot):
    n = Coolstuff(bot)
    bot.add_cog(n)
