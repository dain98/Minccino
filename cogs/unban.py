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

class Unban:
    """Unbans everyone"""

    def __init__(self,bot):
        self.bot = bot
        self.header = {"User-Agent": "User_Agent"}

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def unbanall(self,ctx):
        banlist = await self.bot.get_bans(ctx.message.server)
        for member in banlist:
            await self.bot.unban(ctx.message.server,member)
        await self.bot.say("Done.")


def setup(bot):
    print("setting up...")
    n = Unban(bot)
    bot.add_cog(n)
