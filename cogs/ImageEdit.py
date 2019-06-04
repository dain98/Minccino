import discord
import asyncio
from .utils.dataIO import dataIO
from string import ascii_letters
from .utils import checks
import os
import re
import requests
from discord.ext import commands

class ImageEdit:

    def __init__(self, bot):
        self.bot = bot
        self.header = {"User-Agent": "User_Agent"}
        self.api = dataIO.load_json("data/imageedit/key.json")

    @commands.command(pass_context=True)
    async def removebg(self,ctx,url):
        if ctx.message.author.id != '91317742983974912':
            return
        loading = await self.bot.send_message(ctx.message.channel,"**Working...** <a:mLoading:529680784194404352>")
        response = requests.post(
        'https://api.remove.bg/v1.0/removebg',
        data={
        'image_url': url,
        'size': 'auto'
        },
        headers={'X-Api-Key': self.api['key']},
        )
        await self.bot.delete_message(loading)
        if response.status_code == requests.codes.ok:
            with open('data/imageedit/no-bg.png','wb') as out:
                out.write(response.content)
            await self.bot.send_file(ctx.message.channel,'data/imageedit/no-bg.png')
        else:
            await self.bot.say("Crap, something went wrong: " + response.status_code + response.text)

def setup(bot):
    n = ImageEdit(bot)
    bot.add_cog(n)
