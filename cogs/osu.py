import discord
import asyncio
from .utils.dataIO import dataIO
from string import ascii_letters
from .utils import checks
import os
import re
import aiohttp
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import urllib.request

class Osu:
    """the main osu! cog"""

    def __init__(self,bot):
        self.bot = bot
        self.header = {"User-Agent": "User_Agent"}
        self.template = Image.open("data/osu/template.png")
        self.settings = dataIO.load_json("data/osu/settings.json")

    @commands.command(pass_context=True)
    async def osu(self,ctx,*username_list):
        username = " ".join(username_list) # Turn list of words into one string
        self.template = Image.open("data/osu/template.png") # Reset self.template to remove overlaps
        # Get user data
        async with aiohttp.ClientSession(headers=self.header) as session:
            try:
                async with session.get("https://osu.ppy.sh/api/get_user?k=" + self.settings['api_key'] + "&u=" + username) as channel:
                    res = await channel.json()
            except Exception as e:
                await self.bot.send_message(ctx.message.channel,"Error: " + e)
                return

        if len(res) == 0: # If json is empty the user doesn't exist
            await self.bot.send_message(ctx.message.channel,"Player not found in the osu! database! :x:")
            return

        await self.bot.send_message(ctx.message.channel,"**osu! profile for " + username + ":**")
        urllib.request.urlretrieve("https://a.ppy.sh/" + res[0]['user_id'], "data/osu/useravatar.png") # Receive the user avatar through ID
        # Start drawing the text onto template
        namefnt = ImageFont.truetype("data/osu/fonts/default.otf", 20)
        rankfnt = ImageFont.truetype("data/osu/fonts/default.otf",18)
        cntfnt = ImageFont.truetype("data/osu/fonts/default.otf",14)
        draw = ImageDraw.Draw(self.template)
        # Draw the text in first
        draw.text((125,200), res[0]['username'], font=namefnt, fill=(255,255,255))
        draw.text((125,234), res[0]['country'] + ": " + res[0]['pp_country_rank'], font=cntfnt, fill=(255,255,255))
        draw.text((125,249), res[0]['pp_raw'] + "pp (#" + res[0]['pp_rank'] + ")", font=rankfnt, fill=(255,255,255))
        # Edit avatar and paste onto temp_template
        avatar = Image.open("data/osu/useravatar.png")
        avatar.thumbnail((98,98),Image.ANTIALIAS)
        self.template.paste(avatar,(19,164))
        # Paste avatar corners on top of the avatar to create rounded edges
        aviborder = Image.open("data/osu/avatar_border.png")
        aviborder.thumbnail((98,98),Image.ANTIALIAS)
        self.template.paste(aviborder,(19,164),aviborder)
        
        self.template.save("data/osu/temp_template.png") # Save the file onto a temporary file
        await self.bot.send_file(ctx.message.channel, 'data/osu/temp_template.png')
        os.remove("data/osu/temp_template.png") # Delete the file to reduce clutter

def setup(bot):
    print("setting up...")
    n = Osu(bot)
    bot.add_cog(n)
