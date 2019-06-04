import discord
import asyncio
from .utils.dataIO import dataIO
from string import ascii_letters
from .utils import checks
import os
import re
import random
from discord.ext import commands
from random import uniform

class Video:
    """Generates a Video Chat/Screen Share Link"""

    def __init__(self,bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def generate(self,ctx):
        try:
            vcid = ctx.message.author.voice.voice_channel.id
            serverid = ctx.message.server.id
            await self.bot.send_message(ctx.message.channel,"Video Chat/Screen Share Link: https://discordapp.com/channels/" + str(serverid) + "/" + str(vcid))
        except:
            await self.bot.send_message(ctx.message.channel,"You're not in a voice channel! :x:")


    @commands.command(pass_context=True)
    async def degenerate(self,ctx):
        await self.bot.say("-__               -")
def setup(bot):
    print("setting up...")
    n = Video(bot)
    bot.add_cog(n)
