import discord
import asyncio
from .utils.dataIO import dataIO
from string import ascii_letters
from .utils import checks
import os
import re
import math
import aiohttp
import pyoppai
import pyttanko
import datetime
from pippy.beatmap import Beatmap
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
        self.maps = dataIO.load_json("data/osu/maps/maps.json")
        self.prevRecent = dataIO.load_json("data/osu/recentlist.json")

    async def message_triggered(self,message):
        if 'https://osu.ppy.sh/community/matches' in message.content:
            url = message.content

    @commands.command(pass_context=True)
    async def mp(self,ctx,url):
        if 'https://osu.ppy.sh/community/matches' in url:
            try:
                url = url.split("matches/")
            except:
                await self.bot.say("Invalid URL! :x:")
                return
            url = url[1]
        res = await use_api(self,ctx,"https://osu.ppy.sh/api/get_match?k=" + self.settings['api_key'] + "&mp=" + url)
        if res['match'] == 0:
            await self.bot.say("Invalid URL! :x:")
            return

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
            res = await self.bot.wait_for_message(timeout=10,author=ctx.message.author,check=check)
            await self.bot.delete_message(msg1)
            if res is None:
                await self.bot.say("Response Timed Out. (You took too long to respond)")
            elif res.content.startswith("y"):
                res = await use_api(self,ctx,"https://osu.ppy.sh/api/get_user?k=" + self.settings['api_key'] + "&u=" + username)
                if len(res) == 0:
                    await self.bot.send_message(ctx.message.channel,"User not found in osu! database! :x:")
                    return
                self.users[ctx.message.author.id] = res[0]['username']
                dataIO.save_json("data/osu/users.json", self.users)
                await self.bot.say("Added! Your osu! username is set to " + username + ". ✅")
                return True
            elif res.content.startswith("n"):
                await self.bot.say("osu! username change canceled. ❌")
                return True
            else:
                await self.bot.say("Response Timed Out. (You took too long to respond)")
        else:
            self.users[ctx.message.author.id] = username
            dataIO.save_json("data/osu/users.json", self.users)
            await self.bot.say("Added! Your osu! username is set to " + username + ". ✅")

    @commands.command(pass_context=True)
    async def recent(self,ctx,*username_list):
        username = " ".join(username_list)
        if username == "":
            if ctx.message.author.id not in self.users:
                await self.bot.say("**User not set! Please set your osu! username using -osuset [Username]! ❌**")
                return
            else:
                username = self.users[ctx.message.author.id]
        loading = await self.bot.send_message(ctx.message.channel,"**Working...** <a:loading:491251984679305216>")
        res = await use_api(self,ctx,"https://osu.ppy.sh/api/get_user_recent?k=" + self.settings['api_key'] + "&u=" + username)
        if len(res) == 0:
            await self.bot.delete_message(loading)
            await self.bot.send_message(ctx.message.channel,"No recent plays found for " + username + ". :x:")
            return
        trycount = 0
        tempid = res[0]['beatmap_id']
        for i in res:
            if i['beatmap_id'] == tempid:
                trycount+=1
            else:
                break
        f = []
        acc = round(calculate_acc(res[0]),2)
        if res[0]['rank'] == "F":
            totalhits = (int(res[0]['count50']) + int(res[0]['count100']) + int(res[0]['count300']) + int(res[0]['countmiss']))
        else:
            totalhits = None
        bmapinfo = await get_pyttanko(map_id=int(res[0]['beatmap_id']),accs=[acc],mods=int(res[0]['enabled_mods']),combo=int(res[0]['maxcombo']),completion=totalhits)
        rank = rank_to_emote(res[0]['rank'])
        pp = round(float(bmapinfo['pp'][0]),2)
        if int(res[0]['perfect']) == 1:
            f.append("▸ " + rank + " ▸ **" + str(pp) + "pp** ▸ " + str(acc) + "%")
        else:
            new300 = int(res[0]['count300']) + int(res[0]['countmiss'])
            iffcstats = { "count50":res[0]['count50'],"count100":res[0]['count100'],"count300":new300,"countmiss":0 }
            iffcacc = round(calculate_acc(iffcstats),2)
            iffcinfo = await get_pyttanko(map_id=res[0]['beatmap_id'],accs=[iffcacc],mods=int(res[0]['enabled_mods']),fc=True)
            iffcpp = round(float(iffcinfo['pp'][0]),2)
            f.append("▸ " + rank + " ▸ **" + str(pp) + "pp** (" + str(iffcpp) + "pp for " + str(iffcacc) + "% FC) ▸ " + str(acc) + "%")
        f.append("▸ " + str(res[0]['score']) + " ▸ x" + str(res[0]['maxcombo']) + "/" + str(bmapinfo['max_combo']) + " ▸ [" + str(res[0]['count300']) + "/" + str(res[0]['count100']) + "/" + str(res[0]['count50']) + "/" + str(res[0]['countmiss']) + "]")
        if totalhits is not None:
            if type(bmapinfo['map_completion']) is float:
                complete = round(bmapinfo['map_completion'],2)
                f.append("▸ **Map Completion: **" + str(complete) + "%")
        mods = str(",".join(num_to_mod(res[0]['enabled_mods'])))
        if mods == "":
            mods = "NoMod"
        embed = discord.Embed(colour=0xD3D3D3,title="",description="\n".join(f))
        embed.set_author(name=bmapinfo['artist'] + " - " + bmapinfo['title'] + "[" + bmapinfo['version'] + "] +" + mods + " [" + str(round(bmapinfo['stars'],2)) + "★]",url="https://osu.ppy.sh/b/" + str(res[0]['beatmap_id']),icon_url="https://a.ppy.sh/" + str(res[0]['user_id']))
        tempres = await use_api(self,ctx,"https://osu.ppy.sh/api/get_beatmaps?k=" + self.settings['api_key'] + "&b=" + str(res[0]['beatmap_id']))
        embed.set_thumbnail(url="https://b.ppy.sh/thumb/" + str(tempres[0]['beatmapset_id']) + "l.jpg")
        timeago = time_ago(datetime.datetime.utcnow() + datetime.timedelta(hours=0), datetime.datetime.strptime(res[0]['date'], '%Y-%m-%d %H:%M:%S'))
        embed.set_footer(text="Try #" + str(trycount) + " | {} Ago".format(timeago))
        await self.bot.delete_message(loading)
        self.prevRecent[ctx.message.channel.id] = int(res[0]['beatmap_id'])
        dataIO.save_json("data/osu/recentlist.json",self.prevRecent)
        await self.bot.send_message(ctx.message.channel,embed=embed)

    @commands.command(pass_context=True)
    async def compare(self,ctx,*username_list):
        username = " ".join(username_list)
        if username == "":
            if ctx.message.author.id not in self.users:
                await self.bot.say("**User not set! Please set your osu! username using -osuset [Username]! ❌**")
                return
            else:
                username = self.users[ctx.message.author.id]

        if ctx.message.channel.id not in self.prevRecent:
            await self.bot.send_message(ctx.message.channel,"**No previous -recent command found for this channel.**")
            return
        mapid = self.prevRecent[ctx.message.channel.id]
        scores = await use_api(self,ctx,"https://osu.ppy.sh/api/get_scores?k=" + self.settings['api_key'] + "&u=" + username + "&b=" + str(mapid))
        if len(scores) == 0:
            await self.bot.send_message(ctx.message.channel,"**No scores found for this map. :x:**")
            return
        loading = await self.bot.send_message(ctx.message.channel,"**Working...** <a:loading:491251984679305216>")
        f = []
        count = 1
        for i in scores:
            mods = str(",".join(num_to_mod(i['enabled_mods'])))
            if mods == "":
                mods = "NoMod"
            mapinfo = await get_pyttanko(map_id=mapid,mods=int(i['enabled_mods']))
            f.append("**" + str(count) + "**: **" + mods + "** [**" + str(round(mapinfo['stars'],2)) + "***]")
            rank = rank_to_emote(i['rank'])
            pp = round(float(i['pp']),2)
            acc = round(calculate_acc(i),2)
            if int(i['perfect']) == 1:
                f.append(" ▸ " + rank + " ▸ **" + str(pp) + "pp** ▸ " + str(acc) + "%")
            else:
                new300 = int(i['count300']) + int(i['countmiss'])
                fcstats = { "count50":i['count50'],"count100":i['count100'],"count300":new300,"countmiss":0 }
                fcacc = round(calculate_acc(fcstats),2)
                fcinfo = await get_pyttanko(map_id=mapid,accs=[fcacc],mods=int(i['enabled_mods']),fc=True)
                fcpp = round(float(fcinfo['pp'][0]),2)
                f.append(" ▸ " + rank + " ▸ **" + str(pp) + "pp** (" + str(fcpp) + "pp for " + str(fcacc) + "% FC) ▸ " + str(acc) + "%")

            f.append("▸ " + i['score'] + " ▸ x" + i['maxcombo'] + "/" + str(mapinfo['max_combo']) + " ▸ [" + i['count300'] + "/" + i['count100'] + "/" + i['count50'] + "/" + i['countmiss'] + "]")
            timeago = time_ago(datetime.datetime.utcnow() + datetime.timedelta(hours=0), datetime.datetime.strptime(i['date'], '%Y-%m-%d %H:%M:%S'))
            f.append("▸ Score set {} Ago".format(timeago))
            count+=1
        embed = discord.Embed(colour=0xD3D3D3,title="",description="\n".join(f))
        embed.set_author(name=mapinfo['artist'] + " - " + mapinfo['title'] + "[" + mapinfo['version'] + "]",url="https://osu.ppy.sh/b/" + str(mapid),icon_url="https://a.ppy.sh/" + str(scores[0]['user_id']))
        tempres = await use_api(self,ctx,"https://osu.ppy.sh/api/get_beatmaps?k=" + self.settings['api_key'] + "&b=" + str(mapid))
        embed.set_thumbnail(url="https://b.ppy.sh/thumb/" + str(tempres[0]['beatmapset_id']) + "l.jpg")
        # timeago = time_ago(datetime.datetime.utcnow() + datetime.timedelta(hours=0), datetime.datetime.strptime(res[0]['date'], '%Y-%m-%d %H:%M:%S'))
        # embed.set_footer(text="Try #" + str(trycount) + " | {} Ago".format(timeago))
        await self.bot.send_message(ctx.message.channel,embed=embed)
        await self.bot.delete_message(loading)

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
        res = await use_api(self,ctx,"https://osu.ppy.sh/api/get_user?k=" + self.settings['api_key'] + "&u=" + username)
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
        res = await use_api(self,ctx,"https://osu.ppy.sh/api/get_user_best?k=" + self.settings['api_key'] + "&u=" + username + "&limit=50")
        if len(res) == 0: # If json is empty the user doesn't exist
            await self.bot.send_message(ctx.message.channel,"Player not found in the osu! database! :x:")
            return
        # temp2 = await self.bot.say("**osu! Top Plays for " + username + ":** ")
        numpage = ((len(res) - 1) / 5)
        #res[(i-1)*5:i*5]
        i=1
        isStart = True
        while(True):
            f = []
            tempres = res[(i-1)*5:i*5]
            count = 0
            try:
                uid = tempres[0]['user_id']
            except:
                uid = ""
            for j in tempres:
                bmapres = await use_api(self,ctx,"https://osu.ppy.sh/api/get_beatmaps?k=" + self.settings['api_key'] + "&b=" + j['beatmap_id'])
                map = str(bmapres[0]['title'] + " [" + str(bmapres[0]['version']) + "]")
                url = "https://osu.ppy.sh/b/" + str(j['beatmap_id'])
                mods = str(",".join(num_to_mod(j['enabled_mods'])))
                if mods == "":
                    mods = "NoMod"
                if "DT" in num_to_mod(j['enabled_mods']) or "HR" in num_to_mod(j['enabled_mods']) or "EZ" in num_to_mod(j['enabled_mods']) or "HT" in num_to_mod(j['enabled_mods']):
                    stars = await get_sr(self,str(j['beatmap_id']),str(j['enabled_mods']))
                    stars = round(stars,2)
                else:
                    stars = round(float(bmapres[0]['difficultyrating']),2)
                f.append("**" + str((i-1)*5+count+1) + ". [" + map + "](" + url + ") +" + mods + "** [" + str(stars) + "\*]")
                rank = rank_to_emote(j['rank'])
                pp = float(j['pp'])
                pp = str(round(pp,2)) + "pp"
                accuracy = round(calculate_acc(j),2)
                accuracy = str(accuracy) + "%"
                f.append("▸ **" + rank + "** ▸ **" + pp + "** ▸ " + accuracy)
                score = str(j['score'])
                combo = str(j['maxcombo'])
                mcombo = str(bmapres[0]['max_combo'])
                count300 = str(j['count300'])
                count100 = str(j['count100'])
                count50 = str(j['count50'])
                misses = str(j['countmiss'])
                counts = count300 + "/" + count100 + "/" + count50 + "/" + misses
                f.append("▸ " + score + " ▸ x" + combo + "/" + mcombo + " ▸ [" + counts + "]")
                timeago = time_ago(datetime.datetime.utcnow() + datetime.timedelta(hours=8), datetime.datetime.strptime(j['date'], '%Y-%m-%d %H:%M:%S'))
                f.append('▸ Score Set {}Ago'.format(timeago))
                count += 1
            embed = discord.Embed(colour=0x00FFFF,title="Top osu! Plays for %s"%username,description="\n".join(f))
            embed.set_thumbnail(url="https://a.ppy.sh/" + uid)
            embed.set_footer(text="Page " + str(i) + " of " + str(math.ceil(numpage)))
            try:
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
                    return
                elif "➡" in res1.reaction.emoji and (i < numpage):
                    i += 1
                    await self.bot.remove_reaction(msg,"➡",ctx.message.author)
                elif "⬅" in res1.reaction.emoji and i is not 1:
                    i -= 1
                    await self.bot.remove_reaction(msg,"⬅",ctx.message.author)
                elif '✅' in res1.reaction.emoji:
                    await self.bot.clear_reactions(msg)
                    return
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
            except:
                temp2 = await self.bot.say("**I need permission to edit messages! (Server Settings -> Roles -> [Bot Role] -> Manage Messages -> On)**")
                await asyncio.sleep(2)
                return

def determine_plural(number):
    if int(number) != 1:
        return 's'
    else:
        return ''

def time_ago(time1, time2):
    time_diff = time1 - time2
    timeago = datetime.datetime(1,1,1) + time_diff
    time_limit = 0
    time_ago = ""
    if timeago.year-1 != 0:
        time_ago += "{} Year{} ".format(timeago.year-1, determine_plural(timeago.year-1))
        time_limit = time_limit + 1
    if timeago.month-1 !=0:
        time_ago += "{} Month{} ".format(timeago.month-1, determine_plural(timeago.month-1))
        time_limit = time_limit + 1
    if timeago.day-1 !=0 and not time_limit == 2:
        time_ago += "{} Day{} ".format(timeago.day-1, determine_plural(timeago.day-1))
        time_limit = time_limit + 1
    if timeago.hour != 0 and not time_limit == 2:
        time_ago += "{} Hour{} ".format(timeago.hour, determine_plural(timeago.hour))
        time_limit = time_limit + 1
    if timeago.minute != 0 and not time_limit == 2:
        time_ago += "{} Minute{} ".format(timeago.minute, determine_plural(timeago.minute))
        time_limit = time_limit + 1
    if not time_limit == 2:
        time_ago += "{} Second{} ".format(timeago.second, determine_plural(timeago.second))
    return time_ago

def calculate_acc(beatmap):
    total_unscale_score = float(beatmap['count300'])
    total_unscale_score += float(beatmap['count100'])
    total_unscale_score += float(beatmap['count50'])
    total_unscale_score += float(beatmap['countmiss'])
    total_unscale_score *=300
    user_score = float(beatmap['count300']) * 300.0
    user_score += float(beatmap['count100']) * 100.0
    user_score += float(beatmap['count50']) * 50.0
    return (float(user_score)/float(total_unscale_score)) * 100.0

async def use_api(self, ctx,url):
    async with aiohttp.ClientSession(headers=self.header) as session:
        try:
            async with session.get(url) as channel:
                res = await channel.json()
                return res
        except Exception as e:
            await self.bot.send_message(ctx.message.channel,"Error: " + str(e))
            return

async def get_sr(self, mapID, mods):
    if mapID in self.maps:
        return self.maps[mapID]['stars']
    url = 'https://osu.ppy.sh/osu/{}'.format(mapID)
    ctx = pyoppai.new_ctx()
    b = pyoppai.new_beatmap(ctx)

    BUFSIZE = 2000000
    buf = pyoppai.new_buffer(BUFSIZE)

    file_path = 'data/osu/maps/{}.osu'.format(mapID)
    await download_file(url, file_path)
    pyoppai.parse(file_path, b, buf, BUFSIZE, True, 'data/osu/cache/')
    dctx = pyoppai.new_d_calc_ctx(ctx)
    pyoppai.apply_mods(b, int(mods))

    stars, aim, speed, _, _, _, _ = pyoppai.d_calc(dctx, b)
    pyoppai_json = {
        'stars' : stars
    }

    self.maps[mapID] = pyoppai_json
    dataIO.save_json("data/osu/maps/maps.json",self.maps)
    os.remove(file_path)
    return stars

async def download_file(url, filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            with open(filename, 'wb') as f:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)
            return await response.release()

async def get_pyttanko(map_id:str, accs=[100], mods=0, misses=0, combo=None, completion=None, fc=None, plot = False, color = 'blue'):
    url = 'https://osu.ppy.sh/osu/{}'.format(map_id)
    file_path = 'data/osu/temp/{}.osu'.format(map_id)
    await download_file(url, file_path)
    bmap = pyttanko.parser().map(open(file_path))
    _, ar, od, cs, hp = pyttanko.mods_apply(mods, ar=bmap.ar, od=bmap.od, cs=bmap.cs, hp=bmap.hp)
    stars = pyttanko.diff_calc().calc(bmap, mods=mods)
    bmap.stars = stars.total
    bmap.aim_stars = stars.aim
    bmap.speed_stars = stars.speed

    if not combo:
        combo = bmap.max_combo()

    bmap.pp = []
    bmap.aim_pp = []
    bmap.speed_pp = []
    bmap.acc_pp = []

    bmap.acc = accs

    for acc in accs:
        n300, n100, n50 = pyttanko.acc_round(acc, len(bmap.hitobjects), misses)
        pp, aim_pp, speed_pp, acc_pp, _ = pyttanko.ppv2(
            bmap.aim_stars, bmap.speed_stars, bmap=bmap, mods=mods,
            n300=n300, n100=n100, n50=n50, nmiss=misses, combo=combo)
        bmap.pp.append(pp)
        bmap.aim_pp.append(aim_pp)
        bmap.speed_pp.append(speed_pp)
        bmap.acc_pp.append(acc_pp)

    if fc:
        n300, n100, n50 = pyttanko.acc_round(fc, len(bmap.hitobjects), 0)
        # print("-------------", n300, n100, n50)
        fc_pp, _, _, _, _ = pyttanko.ppv2(
            bmap.aim_stars, bmap.speed_stars, bmap=bmap, mods=mods,
            n300=n300 + misses, n100=n100, n50=n50, nmiss=0, combo=bmap.max_combo())

    pyttanko_json = {
        'version': bmap.version,
        'title': bmap.title,
        'artist': bmap.artist,
        'creator': bmap.creator,
        'combo': combo,
        'max_combo': bmap.max_combo(),
        'misses': misses,
        'mode': bmap.mode,
        'stars': bmap.stars,
        'aim_stars': bmap.aim_stars,
        'speed_stars': bmap.speed_stars,
        'pp': bmap.pp, # list
        'aim_pp': bmap.aim_pp,
        'speed_pp': bmap.speed_pp,
        'acc_pp': bmap.acc_pp,
        'acc': bmap.acc, # list
        'cs': cs,
        'od': od,
        'ar': ar,
        'hp': hp
        }

    if completion:
        try:
            pyttanko_json['map_completion'] = await _map_completion(file_path, int(completion))
        except Exception as e:
            print(e)
            pyttanko_json['map_completion'] = "Error: " + str(e)

    if plot:
        #try:
        pyttanko_json['graph_url'] = await plot_map_stars(file_path, mods, color)
        # print(pyttanko_json['graph_url'])
        #except:
            #pass
        # print(pyttanko_json['graph_url'])

    os.remove(file_path)
    return pyttanko_json

async def _map_completion(btmap, totalhits=0):
    btmap = open(btmap, 'r').read()
    btmap = Beatmap(btmap)
    good = btmap.parse()
    if not good:
        raise ValueError("Beatmap verify failed. "
                         "Either beatmap is not for osu! standard, or it's malformed")
        return
    hitobj = []
    if totalhits == 0:
        totalhits = len(btmap.hit_objects)
    numobj = totalhits - 1
    num = len(btmap.hit_objects)
    for objects in btmap.hit_objects:
        hitobj.append(objects.time)
    timing = int(hitobj[num - 1]) - int(hitobj[0])
    point = int(hitobj[numobj]) - int(hitobj[0])
    map_completion = (point / timing) * 100
    return map_completion

async def plot_map_stars(beatmap, mods, color = 'blue'):
    #try:
    star_list, speed_list, aim_list, time_list = [], [], [], []
    results = oppai(beatmap, mods=mods)
    for chunk in results:
        time_list.append(chunk['time'])
        star_list.append(chunk['stars'])
        aim_list.append(chunk['aim_stars'])
        speed_list.append(chunk['speed_stars'])
    fig = plt.figure(figsize=(6, 2))
    ax = fig.add_subplot(111)
    plt.style.use('ggplot')
    ax.plot(time_list, star_list, color=color, label='Stars', linewidth=2)
    fig.gca().xaxis.set_major_formatter(ticker.FuncFormatter(plot_time_format))
    # plt.ylabel('Stars')
    ax.legend(loc='best')
    fig.tight_layout()
    ax.xaxis.label.set_color(color)
    ax.yaxis.label.set_color(color)
    ax.tick_params(axis='both', colors=color, labelcolor = color)
    ax.grid(color='w', linestyle='-', linewidth=1)

    img_id = random.randint(0, 50)
    filepath = "map_{}.png".format(img_id)
    fig.savefig(filepath, transparent=True)
    plt.close()
    upload = cloudinary.uploader.upload(filepath)
    url = upload['url']
    os.remove(filepath)
    # print(url)
    return url

def num_to_mod(number):
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

def rank_to_emote(rank):
    if rank == "XH": return "<:rankingSSH:507258449080352771>"
    if rank == "X": return "<:rankingSS:507258425185533963>"
    if rank == "SH": return "<:rankingSH:507258396009824274>"
    if rank == "S": return "<:rankingS:507258370986737675>"
    if rank == "A": return "<:rankingA:507258259921698816>"
    if rank == "B": return "<:rankingB:507258284546457640>"
    if rank == "C": return "<:rankingC:507258310655868929>"
    if rank == "D": return "<:rankingD:507258338007056394>"
    if rank == "F": return "<:rankingF:507260433997103115>"

def setup(bot):
    print("setting up...")
    n = Osu(bot)
    bot.add_listener(n.message_triggered, "on_message")
    bot.add_cog(n)
