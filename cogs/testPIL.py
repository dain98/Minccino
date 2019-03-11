import discord
import asyncio
from .utils.dataIO import dataIO
from string import ascii_letters
from .utils import checks
import os
import re
import math
import datetime
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import urllib.request
import textwrap

class TestPIL:
    """Testing PIL"""

    def __init__(self,bot):
        self.bot = bot
        self.text = "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
        self.image = Image.open("data/testPIL/transparentbg.png")

    @commands.command(pass_context=True)
    async def testing(self,ctx):
        self.image = Image.open("data/testPIL/transparentbg.png")
        draw = ImageDraw.Draw(self.image)
        fnt = ImageFont.truetype("data/fonts/default.otf",20)
        draw.text((125,200), self.text, font=fnt,fill=(255,255,255))
        self.template.save("data/testPIL/temp_template.png")
        await self.bot.send_file(ctx.message.channel,'data/testPIL/temp_template.png')
        os.remove('data/osu/temp_template.png')

def setup(bot):
    print("setting up...")
    n = TestPIL(bot)
    bot.add_cog(n)
