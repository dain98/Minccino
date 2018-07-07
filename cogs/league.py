import discord
import asyncio
from .utils.dataIO import dataIO
from string import ascii_letters
from .utils import checks
import os
import re
import aiohttp
import json
from discord.ext import commands
import py_gg

class League:
    """The main League of Legends cog"""

    def __init__(self,bot):
        self.bot = bot
        self.header = {"User-Agent": "User_Agent"}
        self.settings = dataIO.load_json("data/league/settings.json")
        py_gg.init(self.settings['api_key'])

    @commands.command(pass_context=True)
    async def champion(self,ctx,*champname_list):
        champname = " ".join(champname_list)
        # f = { 'champData' : 'hashes' }
        f = { 'elo' : 'PLATINUM,DIAMOND,MASTER,CHALLENGER' , 'champData' : { 'kda', }
        res = py_gg.champions.specific(412,f)
        print(res)

    @commands.command(pass_context=True)
    async def react(self,ctx):
        msg = await self.bot.send_message(ctx.message.channel,"Testing!")
        await self.bot.add_reaction(msg,"⬅")
        await self.bot.add_reaction(msg,"➡")
        # def check(reaction,user):
        #     e = str(reaction.emoji)
        #     return e.startswith(('⬅','➡'))
        # await self.bot.wait_for_reaction(message=msg, check=check)

    @commands.command(pass_context=True)
    async def dljson(self,ctx):
        async with aiohttp.ClientSession(headers=self.header) as session:
            async with session.get("https://na1.api.riotgames.com/lol/static-data/v3/reforged-runes?api_key=" + self.settings['api_key2']) as channel:
                res = await channel.json()
                with open("data/league/sample.json", "w") as outfile:
                    json.dump(res, outfile)
                    await self.bot.send_message(ctx.message.channel,"Done!")

def setup(bot):
    print("setting up...")
    n = League(bot)
    bot.add_cog(n)
