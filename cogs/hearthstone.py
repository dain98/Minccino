import discord
import asyncio
import aiohttp
from .utils.dataIO import dataIO
from string import ascii_letters
from .utils import checks
import os
import re
from discord.ext import commands
import urllib.request

class Hearthstone:
    """Hearthstone-related commands"""

    def __init__(self,bot):
        self.bot = bot
        self.settings = dataIO.load_json("data/hearthstone/settings.json")
        self.header = {"User-Agent": "User_Agent","X-Mashape-Key": self.settings['key']}

    @commands.command(pass_context=True)
    async def card(self,ctx,*card_list):
        """Looks up a card in Hearthstone"""
        card = " ".join(card_list)
        loading = await self.bot.send_message(ctx.message.channel,"**Working...** <a:loading:491251984679305216>")
        url = "https://omgvamp-hearthstone-v1.p.mashape.com/cards/" + card
        async with aiohttp.ClientSession(headers=self.header) as session:
            try:
                async with session.get(url) as channel:
                    res = await channel.json()
            except Exception as e:
                await self.bot.send_message(ctx.message.channel,"Error: " + str(e))
                return
        fpath = "data/hearthstone/{}.png".format(card)
        await self.bot.delete_message(loading)
        try:
            await self.bot.send_message(ctx.message.channel,"**Card image for " + res[0]['name'] + ":**")
            urllib.request.urlretrieve(res[0]['img'],"data/hearthstone/card.png")
            await self.bot.send_file(ctx.message.channel,"data/hearthstone/card.png")
            os.remove("data/hearthstone/card.png")
        except Exception as e:
            await self.bot.send_message(ctx.message.channel,str(e))

def setup(bot):
    print("setting up...")
    n = Hearthstone(bot)
    bot.add_cog(n)
