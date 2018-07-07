import discord
import asyncio
from .utils.dataIO import dataIO
from string import ascii_letters
from .utils import checks
import os
import re
import aiohttp
import pyoppai
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
        self.users = dataIO.load_json("data/osu/users.json")

    @commands.command(pass_context=True)
    async def mapstats(self,ctx,mapID):
        url = 'https://osu.ppy.sh/osu/{}'.format(mapID)

        ctx = pyoppai.new_ctx()
        b = pyoppai.new_beatmaps(ctx)

        BUFSIZE = 2000000
        buf = pyoppai.new_buffer(BUFSIZE)

        file_path = 'data/osu/maps/{}.osu'.format(mapID)
        await download_file(url, file_path)
        pyoppai.parse(file_path, b, buf, BUFSIZE, True, 'data/osu/cache/')
        dctx = pyoppai.new_d_calc_ctx(ctx)



    @commands.command(pass_context=True)
    async def osuset(self,ctx,*username_list):
        username = " ".join(username_list)
        if username == "":
            await self.bot.say("Username can't be blank!")
            return
        if ctx.message.author.id in self.users:
            msg1 = await self.bot.say("Your osu! username is already set to " + self.users[ctx.message.author.id] + "! Are you sure you want to change it to " + username + "? (y/n)")
            def check(msg):
                message = msg.content.lower()
                if message.startswith("y") or message.startswith("n"):
                    return True
                else:
                    return False
            res = await self.bot.wait_for_message(timeout=10,author=ctx.message.author,check=check)
            await self.bot.delete_message(msg1)
            if res is None:
                temp = await self.bot.say("Response Timed Out. (You took too long to respond)")
                await asyncio.sleep(2)
                await self.bot.delete_message(temp)
            elif res.content.startswith("y"):
                self.users[ctx.message.author.id] = username
                dataIO.save_json("data/osu/users.json", self.users)
                temp = await self.bot.say("Added! Your osu! username is set to " + username + ". ✅")
                await asyncio.sleep(2)
                await self.bot.delete_message(temp)
                return True
            elif res.content.startswith("n"):
                temp = await self.bot.say("osu! username change canceled. ❌")
                await asyncio.sleep(2)
                await self.bot.delete_message(temp)
                return True
            else:
                temp = await self.bot.say("Response Timed Out. (You took too long to respond)")
                await asyncio.sleep(2)
                await self.bot.delete_message(temp)
        else:
            self.users[ctx.message.author.id] = username
            dataIO.save_json("data/osu/users.json", self.users)
            temp = await self.bot.say("Added! Your osu! username is set to " + username + ". ✅")
            await asyncio.sleep(2)
            await self.bot.delete_message(temp)

    @commands.command(pass_context=True)
    async def osu(self,ctx,*username_list):
        username = " ".join(username_list) # Turn list of words into one string
        if username == "":
            if ctx.message.author.id not in self.users:
                await self.bot.say("**User not set! Please set your osu! username using -osuset [Username]! ❌**")
                return
            else:
                username = self.users[ctx.message.author.id]
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

    @commands.command(pass_context=True)
    async def osutop(self,ctx,*username_list):
        username = " ".join(username_list)
        if username == "":
            if ctx.message.author.id not in self.users:
                await self.bot.say("**User not set! Please set your osu! username using -osuset [Username]! ❌**")
                return
            else:
                username = self.users[ctx.message.author.id]
        # Get user data
        async with aiohttp.ClientSession(headers=self.header) as session:
            try:
                async with session.get("https://osu.ppy.sh/api/get_user_best?k=" + self.settings['api_key'] + "&u=" + username + "&limit=50") as channel:
                    res = await channel.json()
            except Exception as e:
                await self.bot.send_message(ctx.message.channel,"Error: " + e)
                return
        if len(res) == 0: # If json is empty the user doesn't exist
            await self.bot.send_message(ctx.message.channel,"Player not found in the osu! database! :x:")
            return
        temp2 = await self.bot.say("**osu! Top Plays for " + username + ":** ")
        numpage = ((len(res) - 1) / 5)
        #res[(i-1)*5:i*5]
        i=1
        isStart = True
        while(True):
            print("during while", i)
            f = []
            tempres = res[(i-1)*5:i*5]
            count = 0
            try:
                uid = tempres[0]['user_id']
            except:
                uid = ""
            for j in tempres:
                async with aiohttp.ClientSession(headers=self.header) as session:
                    try:
                        async with session.get("https://osu.ppy.sh/api/get_beatmaps?k=" + self.settings['api_key'] + "&b=" + j['beatmap_id']) as channel:
                            bmapres = await channel.json()
                    except Exception as e:
                        await self.bot.send_message(ctx.message.channel,"Error: " + str(e))
                        return
                map = str(bmapres[0]['title'] + " [" + str(bmapres[0]['version']) + "]")
                url = "https://osu.ppy.sh/b/" + str(j['beatmap_id'])
                mods = str(",".join(num_to_mod(j['enabled_mods'])))
                if mods == "":
                    mods = "NoMod"
                stars = round(float(bmapres[0]['difficultyrating']),2)
                f.append("**" + str((i-1)*5+count+1) + ". [" + map + "](" + url + ") +" + mods + "** [" + str(stars) + "\*]")
                f.append("")
                count += 1
            embed = discord.Embed(colour=0x00FFFF,title="Page %d"%i,description="\n".join(f))
            embed.set_thumbnail(url="https://a.ppy.sh/" + uid)
            if isStart:
                isStart = False
                msg = await self.bot.send_message(ctx.message.channel,embed=embed)
                await self.bot.add_reaction(msg,"⬅")
                await self.bot.add_reaction(msg,"➡")
                await self.bot.add_reaction(msg,"✅")
            else:
                await self.bot.edit_message(msg,embed=embed)
            res1 = await self.bot.wait_for_reaction(['⬅','➡','✅'], user=ctx.message.author, message=msg, timeout=60)
            if res1 is None:
                await self.bot.delete_message(msg)
                await self.bot.delete_message(temp2)
                break
            elif "➡" in res1.reaction.emoji and (i < numpage):
                i += 1
                await self.bot.remove_reaction(msg,"➡",ctx.message.author)
            elif "⬅" in res1.reaction.emoji and i is not 1:
                i -= 1
                await self.bot.remove_reaction(msg,"⬅",ctx.message.author)
            elif '✅' in res1.reaction.emoji:
                await self.bot.clear_reactions(msg)
                temp = await self.bot.send_message(ctx.message.channel,"**Minccino will keep this message here! ✅**")
                await asyncio.sleep(2)
                await self.bot.delete_message(temp)
                break
            else:
                if i == 1:
                    await self.bot.remove_reaction(msg,"⬅",ctx.message.author)
                    temp = await self.bot.send_message(ctx.message.channel,"**You've reached the beginning of this list.**")
                    await asyncio.sleep(1)
                    await self.bot.delete_message(temp)
                else:
                    await self.bot.remove_reaction(msg,"➡",ctx.message.author)
                    temp = await self.bot.send_message(ctx.message.channel,"**You've reached the end of this list.**")
                    await asyncio.sleep(1)
                    await self.bot.delete_message(temp)

def num_to_mod(number):
    """This is the way pyttanko does it.
    Just as an actual bitwise instead of list.
    Deal with it."""
    number = int(number)
    mod_list = []

    if number & 1<<0:   mod_list.append('NF')
    if number & 1<<1:   mod_list.append('EZ')
    if number & 1<<3:   mod_list.append('HD')
    if number & 1<<4:   mod_list.append('HR')
    if number & 1<<5:   mod_list.append('SD')
    if number & 1<<9:   mod_list.append('NC')
    elif number & 1<<6: mod_list.append('DT')
    if number & 1<<7:   mod_list.append('RX')
    if number & 1<<8:   mod_list.append('HT')
    if number & 1<<10:  mod_list.append('FL')
    if number & 1<<12:  mod_list.append('SO')
    if number & 1<<14:  mod_list.append('PF')
    if number & 1<<15:  mod_list.append('4 KEY')
    if number & 1<<16:  mod_list.append('5 KEY')
    if number & 1<<17:  mod_list.append('6 KEY')
    if number & 1<<18:  mod_list.append('7 KEY')
    if number & 1<<19:  mod_list.append('8 KEY')
    if number & 1<<20:  mod_list.append('FI')
    if number & 1<<24:  mod_list.append('9 KEY')
    if number & 1<<25:  mod_list.append('10 KEY')
    if number & 1<<26:  mod_list.append('1 KEY')
    if number & 1<<27:  mod_list.append('3 KEY')
    if number & 1<<28:  mod_list.append('2 KEY')

    return mod_list

def setup(bot):
    print("setting up...")
    n = Osu(bot)
    bot.add_cog(n)
