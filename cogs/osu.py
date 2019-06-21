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
import decimal
import textwrap
import random
import pyttanko
import aggdraw
import time
import pycountry
from collections import OrderedDict
import datetime
from pbwrap import Pastebin
from pippy.beatmap import Beatmap
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import urllib.request

class Osu:
    """the main osu! cog"""

    def __init__(self,bot):
        self.bot = bot
        self.header = {"User-Agent": "User_Agent"}
        self.pasteKey = dataIO.load_json("data/apikeys/pastebinkey.json")
        self.pb = Pastebin(self.pasteKey['api_dev_key'])
        self.template = Image.open("data/osu/template.png")
        self.recenttemplate = Image.open("data/osu/templates/recent.png")
        self.settings = dataIO.load_json("data/osu/settings.json")
        self.users = dataIO.load_json("data/osu/users.json")
        self.maps = dataIO.load_json("data/osu/maps/maps.json")
        self.prevRecent = dataIO.load_json("data/osu/recentlist.json")
        self.sample = dataIO.load_json("data/osu/sample.json")

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def mp(self,ctx,url,warmups=2):
        """***UNDER CONSTRUCTION***"""
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
        loading = await self.bot.send_message(ctx.message.channel,"**Working...** <a:mLoading:529680784194404352>")

    @commands.command(pass_context=True)
    async def bws(self,ctx,rank,bcount):
        """Check your Badge Weighted Seeding rank. -bws [rank] [badgecount]"""
        bcount = int(bcount)
        rank = int(rank)
        newrank = bcount ** 2
        newrank = 0.9937 ** newrank
        newrank = rank ** newrank
        newrank = round(newrank)
        await self.bot.send_message(ctx.message.channel,"Previous Rank: **" + str(rank) + "**    Badge Count: **" + str(bcount) + "**")
        await self.bot.send_message(ctx.message.channel,"Rank after BWS: **" + str(newrank) + "**")

    @commands.command(pass_context=True)
    async def petbws(self,ctx,rank,bcount):
        """Check your Badge Weighted Seeding rank for Pls Enjoy Tournament. -petbws [rank] [badgecount]"""
        bcount = int(bcount)
        rank = int(rank)
        newrank = 1 + bcount
        newrank **= 1.06
        newrank = 0.7 ** newrank
        newrank = (0.09 * rank) ** newrank
        newrank = (0.9 * rank) / newrank
        newrank = rank - newrank
        newrank = round(newrank)
        await self.bot.send_message(ctx.message.channel,"Previous Rank: **" + str(rank) + "**    Badge Count: **" + str(bcount) + "**")
        await self.bot.send_message(ctx.message.channel,"Rank after BWS: **" + str(newrank) + "**")

    @commands.command(pass_context=True)
    async def osuset(self,ctx,*username_list):
        """Set your osu! username."""
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
    async def recentbest(self,ctx,*username_list):
        """Get a player's most recent best score!"""
        if username_list[0].isdigit():
            best = username_list[0]
            username_list = username_list[1:]
        else:
            best = 1
        username = " ".join(username_list)
        if username == "":
            if ctx.message.author.id not in self.users:
                await self.bot.say("**User not set! Please set your osu! username using -osuset [Username]! ❌**")
                return
            else:
                username = self.users[ctx.message.author.id]
        await self.bot.say(username)
        # loading = await self.bot.send_message(ctx.message.channel,"**Working...** <a:mLoading:529680784194404352>")
        user = await use_api(self,ctx,"https://osu.ppy.sh/api/get_user?k=" + self.settings['api_key'] + "&u=" + username)
        if len(user) == 0:
            await self.bot.edit_message(loading,"User not found! :x:")
            return
        userbest = await use_api(self,ctx,"https://osu.ppy.sh/api/get_user_best?k=" + self.settings['api_key'] + "&u=" + username + "&limit=100")
        if len(userbest) == 0:
            await self.bot.edit_message(loading,"User not found! :x:")
            return

    @commands.command(pass_context=True)
    async def recent(self,ctx,*username_list):
        """Get your most recent score!"""
        if username_list[0].isdigit():
            num = int(username_list[0])
            num -= 1
            username_list = username_list[1:]
        else:
            num = 0
        username = " ".join(username_list)
        if username == "":
            if ctx.message.author.id not in self.users:
                await self.bot.say("**User not set! Please set your osu! username using -osuset [Username]! ❌**")
                return
            else:
                username = self.users[ctx.message.author.id]
        loading = await self.bot.send_message(ctx.message.channel,"**Working...** <a:mLoading:529680784194404352>")
        user = await use_api(self,ctx,"https://osu.ppy.sh/api/get_user?k=" + self.settings['api_key'] + "&u=" + username)
        if len(user) == 0:
            await self.bot.edit_message(loading,"User not found! :x:")
            return
        userbest = await use_api(self,ctx,"https://osu.ppy.sh/api/get_user_best?k=" + self.settings['api_key'] + "&u=" + username + "&limit=100")
        if len(userbest) == 0:
            await self.bot.edit_message(loading,"User not found! :x:")
            return
        res = await use_api(self,ctx,"https://osu.ppy.sh/api/get_user_recent?k=" + self.settings['api_key'] + "&u=" + username)
        if len(res) == 0:
            await self.bot.edit_message(loading,"No recent plays found for " + username + ". :x:")
            return
        trycount = 0
        tempid = res[num]['beatmap_id']
        for i in res:
            if i['beatmap_id'] == tempid:
                trycount+=1
            else:
                break
        acc = round(calculate_acc(res[num]),2)
        totalhits = (int(res[num]['count50']) + int(res[num]['count100']) + int(res[num]['count300']) + int(res[num]['countmiss']))
        apibmapinfo = await use_api(self,ctx,"https://osu.ppy.sh/api/get_beatmaps?k=" + self.settings['api_key'] + "&b=" + str(res[num]['beatmap_id']))
        bmapinfo = await get_pyttanko(map_id=int(res[num]['beatmap_id']),misses=int(res[num]['countmiss']),accs=[acc],mods=int(res[num]['enabled_mods']),combo=int(res[num]['maxcombo']),completion=totalhits)
        complete = round(bmapinfo['map_completion'],2)
        srating = str(round(bmapinfo['stars'],2))
        pp = round(float(bmapinfo['pp'][0]),2)
        mods = str(",".join(num_to_mod(res[num]['enabled_mods'])))
        score = format(int(res[num]['score']),',d')
        if mods != "":
            mods = "+" + mods
        titleText = "{} - {}".format(bmapinfo['artist'],bmapinfo['title'])
        subtitleText = "[" + bmapinfo['version']
        maprank = await mrank(self,ctx,res[num]['beatmap_id'],res[num]['score'],user[0]['user_id'])
        toprank = None
        for idx,i in enumerate(userbest):
            if i['beatmap_id'] == res[num]['beatmap_id']:
                if i['score'] == res[num]['score']:
                    toprank = idx + 1
                    break
        self.recenttemplate = Image.open("data/osu/templates/recent.png")
        draw = ImageDraw.Draw(self.recenttemplate)
        adraw = aggdraw.Draw(self.recenttemplate)
        titleFont = ImageFont.truetype("data/fonts/NotoSansSemiBold.otf",16)
        subtitleFont = ImageFont.truetype("data/fonts/NotoSansRegular.otf",12)
        defaultFont = ImageFont.truetype("data/fonts/NotoSansLight.otf",15)
        defaultBoldFont = ImageFont.truetype("data/fonts/NotoSansSemiBold.otf",15)
        smallFont = aggdraw.Font((255,255,255),"data/fonts/NotoSansLight.otf",size=12,opacity=255)
        smalllFont = ImageFont.truetype("data/fonts/NotoSansLight.otf",12)
        smallBoldFont = aggdraw.Font((255,255,255),"data/fonts/NotoSansSemiBold.otf",size=12,opacity=255)
        smallBolddFont = ImageFont.truetype("data/fonts/NotoSansSemiBold.otf",12)
        smallestFont = aggdraw.Font((255,255,255),"data/fonts/NotoSansLight.otf",size=10,opacity=255)
        smallesttFont = ImageFont.truetype("data/fonts/NotoSansLight.otf",10)
        tryFont = ImageFont.truetype("data/fonts/NotoSansLight.otf",20)
        hittFont = ImageFont.truetype("data/fonts/NotoSansRegular.otf",10)
        hitFont = aggdraw.Font((255,255,255), "data/fonts/NotoSansRegular.otf",size=12,opacity=255)
        titleCutoff = False
        while titleFont.getsize(titleText)[0] > 448:
            titleText = titleText[:-1]
            titleCutoff = True
        if titleCutoff:
            titleText += "..."
        subtitleText += "] " + mods
        # Draw User Info
        adraw.text((498,184),"{}pp".format(user[0]['pp_raw']),smallFont)
        adraw.text((498,198),"#{}, {} #{}".format(user[0]['pp_rank'],user[0]['country'],user[0]['pp_country_rank']),smallFont)
        timeago = "Score set {}ago.".format(time_ago(datetime.datetime.utcnow() + datetime.timedelta(hours=0), datetime.datetime.strptime(res[num]['date'], '%Y-%m-%d %H:%M:%S')))
        tago = textwrap.wrap(timeago,width=22)
        h = 268
        for line in tago:
            adraw.text((498,h),str(line),smallestFont)
            h += 14
        # Draw Combo
        w, h = draw.textsize(res[num]['maxcombo'],smalllFont)
        width = 20
        height = 190
        tempFont = aggdraw.Font((255,255,255),"data/fonts/NotoSansLight.otf",size=14,opacity=255)
        tempFontSize = ImageFont.truetype("data/fonts/NotoSansLight.otf",14)
        tempBoldFont = aggdraw.Font((255,255,255),"data/fonts/NotoSansSemiBold.otf",size=14,opacity=255)
        tempBoldFontSize = ImageFont.truetype("data/fonts/NotoSansSemiBold.otf",14)
        adraw.text((width,height),str(res[num]['maxcombo']),smallFont)
        w2, h2 = draw.textsize(str(bmapinfo['max_combo']),smallBolddFont)
        width2 = width + w + 12
        height2 = (414-h2)/2
        pen = aggdraw.Pen("white",0.8)
        adraw.line((width2,height+4,width+w,height2+h2),pen)
        adraw.text((width2,height2),str(bmapinfo['max_combo']),smallBoldFont)
        # Draw 300s 100s 50s and misses
        w, h = draw.textsize(res[num]['count300'],font=hittFont)
        adraw.text(((290-w)/2,(244-h)/2),str(res[num]['count300']),hitFont)
        w, h = draw.textsize(res[num]['count50'],font=hittFont)
        adraw.text(((290-w)/2,(300-h)/2),res[num]['count50'],hitFont)
        w, h = draw.textsize(res[num]['count100'],font=hittFont)
        adraw.text(((478-w)/2,(244-h)/2),str(res[num]['count100']),hitFont)
        w, h = draw.textsize(res[num]['countmiss'],font=hittFont)
        adraw.text(((478-w)/2,(300-h)/2),res[num]['countmiss'],hitFont)
        # Draw if FC Stats
        new300 = int(res[num]['count300']) + int(res[num]['countmiss'])
        iffcstats = { "count50":res[num]['count50'],"count100":res[num]['count100'],"count300":new300,"countmiss":0 }
        iffcacc = round(calculate_acc(iffcstats),2)
        iffcinfo = await get_pyttanko(map_id=res[num]['beatmap_id'],accs=[iffcacc],mods=int(res[num]['enabled_mods']),fc=True)
        iffcpp = round(float(iffcinfo['pp'][0]),2)
        w, h = draw.textsize(str(iffcacc),smallesttFont)
        adraw.text(((790-w)/2,(530-h)/2),"IF FC WITH {}%".format(iffcacc),smallestFont)
        # Draw URL
        adraw.text((13,282),"Generated using Minccino: https://github.com/dain98/Minccino",smallestFont)
        # Flush aggdraw
        adraw.flush()
        # Draw User Image
        try:
            urllib.request.urlretrieve("https://a.ppy.sh/{}".format(user[0]['user_id']),"data/osu/cache/user_{}.png".format(user[0]['user_id']))
            userimage = Image.open("data/osu/cache/user_{}.png".format(user[0]['user_id']))
            userimage.thumbnail((54,54),Image.ANTIALIAS)
            self.recenttemplate.paste(userimage,(525,107))
            os.remove("data/osu/cache/user_{}.png".format(user[0]['user_id']))
        except:
            pass
        # Draw Beatmap Image
        try:
            urllib.request.urlretrieve("https://b.ppy.sh/thumb/" + str(apibmapinfo[0]['beatmapset_id']) + "l.jpg",'data/osu/cache/map_{}.png'.format(apibmapinfo[0]['beatmapset_id']))
            mapimage = Image.open("data/osu/cache/map_{}.png".format(apibmapinfo[0]['beatmapset_id']))
            mapimage.thumbnail((104,78),Image.ANTIALIAS)
            self.recenttemplate.paste(mapimage,(498,7))
            os.remove("data/osu/cache/map_{}.png".format(apibmapinfo[0]['beatmapset_id']))
        except:
            print(apibmapinfo[0]['beatmapset_id'])
            pass
        rankimage = Image.open("data/osu/rankletters/rank" + res[num]['rank'] + ".png")
        rankimage.thumbnail((100,100),Image.ANTIALIAS)
        self.recenttemplate.paste(rankimage,(385,63),rankimage)
        # Draw User Info
        draw.text((498,166),"{}".format(user[0]['username']),font=defaultBoldFont,fill=(255,255,255))
        # Draw name of map
        draw.text((18,13),titleText,font=titleFont,fill=(255,255,255))
        if maprank is not None:
            subtitleText = subtitleText + " Rank #{}".format(maprank)
            if toprank is not None:
                subTitleText = subtitleText + ", Personal Best #{}!".format(toprank)
        elif toprank is not None:
            subtitleText = subtitleText + " Personal Best #{}!".format(toprank)
        draw.text((18,34),subtitleText,font=subtitleFont,fill=(255,255,255))
        # Draw score
        draw.text((19,79),score,font=defaultFont,fill=(255,255,255))
        # Draw Difficulty
        draw.text((284,139),"{}*".format(srating),font=defaultBoldFont,fill=(255,255,255))
        # Draw Trycount
        draw.text((288,79),"#{}".format(trycount),font=defaultFont,fill=(255,255,255))
        # Draw Map completion
        draw.text((242,193),"{:.2f}%".format(complete),font=defaultBoldFont,fill=(255,255,255))
        # Draw Accuracy
        draw.text((150,193),"{:.2f}%".format(acc),font=defaultBoldFont,fill=(255,255,255))
        # Draw Beatmap information
        if "DT" in mods:
            lnth = round(float(apibmapinfo[0]['total_length']) / 1.5)
            bpm = str(round(float(apibmapinfo[0]['bpm']) * 1.5,2)).rstrip("0")
        elif "HT" in mods:
            lnth = round(float(apibmapinfo[0]['total_length']) / 0.75)
            bpm = str(round(float(apibmapinfo[0]['bpm']) * 0.75,2)).rstrip("0")
        else:
            lnth = float(apibmapinfo[0]['total_length'])
            bpm = str(round(float(apibmapinfo[0]['bpm']),2)).rstrip("0")
            if bpm.endswith("."):
                bpm = bpm[:-1]
        length = str(datetime.timedelta(minutes=lnth))
        length = length[:-3]
        # minutes = int(lnth/60)
        # seconds = lnth % 60
        # hours = int(minutes/60)
        # minutes = minutes%60
        # if hours == 0:
        #     length = str(minutes) + ":" + str(int(seconds))
        # else:
        #     length = str(hours) + ":" + str(int(minutes)) + ":" + str(int(seconds))
        ar = str(round(bmapinfo['ar'],2)).rstrip("0")
        if bpm.endswith("."):
            bpm = bpm[:-1]
        if ar.endswith("."):
            ar = ar[:-1]
        od = str(round(bmapinfo['od'],2)).rstrip("0")
        if od.endswith("."):
            od = od[:-1]
        cs = str(round(bmapinfo['cs'],2)).rstrip("0")
        if cs.endswith("."):
            cs = cs[:-1]
        hp = str(round(bmapinfo['hp'],2)).rstrip("0")
        if hp.endswith("."):
            hp = hp[:-1]
        draw.text((20,255),"Length: {}, AR {}, OD {}, CS {}, HP {}, {} BPM".format(length,ar,od,cs,hp,bpm),font=smalllFont,fill=(255,255,255))
        # Draw Performance
        w, h = draw.textsize(str(pp),font=defaultFont)
        draw.text(((832-w)/2,(406-h)/2),"{}pp".format(pp),font=defaultFont,fill=(255,255,255))
        w, h = draw.textsize(str(iffcpp),font=defaultFont)
        draw.text(((832-w)/2,(496-h)/2),"{}pp".format(iffcpp),font=defaultFont,fill=(255,255,255))
        code = random.randint(100000000,999999999)
        self.recenttemplate.save("data/osu/cache/score_{}.png".format(code))
        await self.bot.send_file(ctx.message.channel,'data/osu/cache/score_{}.png'.format(code))
        await self.bot.delete_message(loading)
        os.remove('data/osu/cache/score_{}.png'.format(code))
        self.prevRecent[ctx.message.channel.id] = int(res[num]['beatmap_id'])
        dataIO.save_json("data/osu/recentlist.json",self.prevRecent)

    # @commands.command(pass_context=True)
    # async def recent(self,ctx,*username_list):
    #     """Show your most recent osu! Standard play."""
    #     username = " ".join(username_list)
    #     if username == "":
    #         if ctx.message.author.id not in self.users:
    #             await self.bot.say("**User not set! Please set your osu! username using -osuset [Username]! ❌**")
    #             return
    #         else:
    #             username = self.users[ctx.message.author.id]
    #     loading = await self.bot.send_message(ctx.message.channel,"**Working...** <a:mLoading:529680784194404352>")
    #     user = await use_api(self,ctx,"https://osu.ppy.sh/api/get_user?k=" + self.settings['api_key'] + "&u=" + username)
    #     if len(user) == 0:
    #         await self.bot.edit_message(loading,"User not found! :x:")
    #         return
    #     userbest = await use_api(self,ctx,"https://osu.ppy.sh/api/get_user_best?k=" + self.settings['api_key'] + "&u=" + username + "&limit=100")
    #     if len(userbest) == 0:
    #         await self.bot.edit_message(loading,"User not found! :x:")
    #         return
    #     res = await use_api(self,ctx,"https://osu.ppy.sh/api/get_user_recent?k=" + self.settings['api_key'] + "&u=" + username)
    #     if len(res) == 0:
    #         await self.bot.edit_message(loading,"No recent plays found for " + username + ". :x:")
    #         return
    #     trycount = 0
    #     tempid = res[0]['beatmap_id']
    #     for i in res:
    #         if i['beatmap_id'] == tempid:
    #             trycount+=1
    #         else:
    #             break
    #     acc = round(calculate_acc(res[0]),2)
    #     totalhits = (int(res[0]['count50']) + int(res[0]['count100']) + int(res[0]['count300']) + int(res[0]['countmiss']))
    #     apibmapinfo = await use_api(self,ctx,"https://osu.ppy.sh/api/get_beatmaps?k=" + self.settings['api_key'] + "&b=" + str(res[0]['beatmap_id']))
    #     bmapinfo = await get_pyttanko(map_id=int(res[0]['beatmap_id']),misses=int(res[0]['countmiss']),accs=[acc],mods=int(res[0]['enabled_mods']),combo=int(res[0]['maxcombo']),completion=totalhits)
    #     rank = rank_to_emote(res[0]['rank'])
    #     semote = star_to_emote(bmapinfo['stars'])
    #     srating = str(round(bmapinfo['stars'],2))
    #     hit300 = hit_to_emote("hit300")
    #     hit100 = hit_to_emote("hit100")
    #     hit50 = hit_to_emote("hit50")
    #     hit0 = hit_to_emote("hit0")
    #     pp = round(float(bmapinfo['pp'][0]),2)
    #     mods = str(",".join(num_to_mod(res[0]['enabled_mods'])))
    #     if mods != "":
    #         mods = "**" + mods + "**"
    #     mapname = bmapinfo['artist'] + " - " + bmapinfo['title'] + "[" + bmapinfo['version'] + "]"
    #     maprank = None
    #     if len(user[0]['events']) != 0:
    #         for i in user[0]['events']:
    #             if i['beatmap_id'] == res[0]['beatmap_id']:
    #                 maprank = eventrank(i['display_html'])
    #                 break
    #     toprank = None
    #     for idx,i in enumerate(userbest):
    #         if i['beatmap_id'] == res[0]['beatmap_id']:
    #             if i['score'] == res[0]['score']:
    #                 toprank = idx + 1
    #                 break
    #     embed=discord.Embed(title="<a:mLoading:529680784194404352>Most recent play in osu! **Standard** by :flag_" + user[0]['country'].lower() + ": **" + username + "**",description="[" + mapname + "](https://osu.ppy.sh/b/" + res[0]['beatmap_id'] + ")", color=0x00ffff)
    #     embed.set_thumbnail(url="https://b.ppy.sh/thumb/" + str(apibmapinfo[0]['beatmapset_id']) + "l.jpg")
    #     f = rank + "  " + srating + "☆ " + mods + "\n**Accuracy: **" + str(acc) + "%\n**Score:** " + format(int(res[0]['score']),',d') + hit300 + str(res[0]['count300']) + hit100 + str(res[0]['count100']) + hit50 + str(res[0]['count50']) + hit0 + str(res[0]['countmiss']) + "\n**Try** #" + str(trycount)
    #     if maprank != None:
    #         f += ", **Rank**: #" + maprank
    #     if toprank != None:
    #         f += ", **Personal Best ** #" + str(toprank)
    #     embed.add_field(name="**Play Information**",value=f, inline=False)
    #     new300 = int(res[0]['count300']) + int(res[0]['countmiss'])
    #     iffcstats = { "count50":res[0]['count50'],"count100":res[0]['count100'],"count300":new300,"countmiss":0 }
    #     iffcacc = round(calculate_acc(iffcstats),2)
    #     iffcinfo = await get_pyttanko(map_id=res[0]['beatmap_id'],accs=[iffcacc],mods=int(res[0]['enabled_mods']),fc=True)
    #     iffcpp = round(float(iffcinfo['pp'][0]),2)
    #     pp = round(float(bmapinfo['pp'][0]),2)
    #     embed.add_field(name="**Combo**",value="**" + str(res[0]['maxcombo']) + "** / " + str(bmapinfo['max_combo']) + "x",inline=True)
    #     embed.add_field(name="**Performance**",value="**" + str(pp) + "pp** / " + str(iffcpp) + "pp for " + str(iffcacc) + "%",inline=True)
    #     try:
    #         if res[0]['rank'] == "F":
    #             complete = round(bmapinfo['map_completion'],2)
    #             embed.add_field(name="**Map Completion**",value="**" + str(complete) + "%**",inline=True)
    #     except Exception as e:
    #         print(e)
    #     if "DT" in mods:
    #         lnth = round(float(apibmapinfo[0]['total_length']) / 1.5)
    #         bpm = str(round(float(apibmapinfo[0]['bpm']) * 1.5,2)).rstrip("0")
    #     elif "HT" in mods:
    #         lnth = round(float(apibmapinfo[0]['total_length']) / 0.75)
    #         bpm = str(round(float(apibmapinfo[0]['bpm']) * 0.75,2)).rstrip("0")
    #     else:
    #         lnth = float(apibmapinfo[0]['total_length'])
    #         bpm = str(round(float(apibmapinfo[0]['bpm']),2)).rstrip("0")
    #         if bpm.endswith("."):
    #             bpm = bpm[:-1]
    #     minutes = int(lnth/60)
    #     seconds = lnth % 60
    #     hours = int(minutes/60)
    #     minutes = minutes%60
    #     if hours == 0:
    #         length = str(minutes) + ":" + str(int(seconds))
    #     else:
    #         length = str(hours) + ":" + str(int(minutes)) + ":" + str(int(seconds))
    #     ar = str(round(bmapinfo['ar'],2)).rstrip("0")
    #     if ar.endswith("."):
    #         ar = ar[:-1]
    #     od = str(round(bmapinfo['od'],2)).rstrip("0")
    #     if od.endswith("."):
    #         od = od[:-1]
    #     cs = str(round(bmapinfo['cs'],2)).rstrip("0")
    #     if cs.endswith("."):
    #         cs = cs[:-1]
    #     hp = str(round(bmapinfo['hp'],2)).rstrip("0")
    #     if hp.endswith("."):
    #         hp = hp[:-1]
    #     embed.add_field(name="**Beatmap Information**", value="Length: **" + length + "**, AR: **" + str(ar) + "**, OD: **" + str(od) + "**, CS: **" + str(cs) + "**, BPM: **" + str(bpm) + "**, HP: **" + str(hp) + "**", inline=False)
    #     countryObject = pycountry.countries.get(alpha_2=user[0]['country'])
    #     print(countryObject)
    #     try:
    #         countryName = countryObject.official_name
    #     except:
    #         countryName = countryObject.name
    #     timeago = time_ago(datetime.datetime.utcnow() + datetime.timedelta(hours=0), datetime.datetime.strptime(res[0]['date'], '%Y-%m-%d %H:%M:%S'))
    #     embed.set_footer(text=username + " #" + user[0]['pp_rank'] + " Global, #" + user[0]['pp_country_rank'] + " " + countryName + " • {} Ago".format(timeago),icon_url="https://a.ppy.sh/" + str(res[0]['user_id']))
    #     await self.bot.edit_message(loading," ",embed=embed)
    #     self.prevRecent[ctx.message.channel.id] = int(res[0]['beatmap_id'])
    #     dataIO.save_json("data/osu/recentlist.json",self.prevRecent)

    @commands.command(pass_context=True)
    async def compare(self,ctx,*username_list):
        """Compare the last -recent score with your own."""
        username = " ".join(username_list)
        if username == "":
            if ctx.message.author.id not in self.users:
                await self.bot.say("**User not set! Please set your osu! username using -osuset [Username]! ❌**")
                return
            else:
                username = self.users[ctx.message.author.id]
        if ctx.message.author.id == "107663669302685696":
            await self.bot.say("...>:|")
            await asyncio.sleep(2)
        if ctx.message.channel.id not in self.prevRecent:
            await self.bot.send_message(ctx.message.channel,"**No previous -recent command found for this channel.**")
            return
        mapid = self.prevRecent[ctx.message.channel.id]
        scores = await use_api(self,ctx,"https://osu.ppy.sh/api/get_scores?k=" + self.settings['api_key'] + "&u=" + username + "&b=" + str(mapid))
        if len(scores) == 0:
            await self.bot.send_message(ctx.message.channel,"**No scores found for this map. :x:**")
            return
        loading = await self.bot.send_message(ctx.message.channel,"**Working...** <a:mLoading:529680784194404352>")
        f = []
        count = 1
        for i in scores:
            mods = str(",".join(num_to_mod(i['enabled_mods'])))
            if mods == "":
                mods = "NoMod"
            acc = round(calculate_acc(i),2)
            mapinfo = await get_pyttanko(map_id=mapid,accs=[acc],misses=int(i['countmiss']),mods=int(i['enabled_mods']),combo=int(i['maxcombo']))
            f.append("**" + str(count) + "**: **" + mods + "** [**" + str(round(mapinfo['stars'],2)) + "***]")
            rank = rank_to_emote(i['rank'])
            if i['pp'] is None:
                pp = round(mapinfo['pp'][0],2)
            else:
                pp = round(float(i['pp']),2)

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
        await self.bot.edit_message(loading," ",embed=embed)

    @commands.command(pass_context=True)
    async def osu(self,ctx,*username_list):
        """Show information about an osu! account."""
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
        """Show an osu! player's top plays."""
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
        loading = await self.bot.send_message(ctx.message.channel,"**Working...** <a:mLoading:529680784194404352>")
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
                    await self.bot.delete_message(loading)
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

    @commands.command(pass_context=True)
    async def match_costs(self,ctx,url,warmups=2):
        """Shows how well each player did in a multi lobby."""
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
        loading = await self.bot.send_message(ctx.message.channel,"**Working...** <a:mLoading:529680784194404352>")
        if int(res['games'][0]['team_type']) == 2:
            teamVS = True
        else:
            teamVS = False
        if warmups <= 0:
            pass
        else:
            try:
                for i in range(warmups):
                    del res['games'][0]
            except Exception as e:
                pass
        a = time.time()
        res['games'], playerlist = parse_match(res['games'],teamVS)
        b = time.time()
        await self.bot.edit_message(loading,"**Finished Parsing MP. Outputting Embed Message... (Took {:0.5f}s)** <a:mLoading:529680784194404352>".format(b - a))
        c = time.time()
        self.sample = res['games']
        dataIO.save_json("data/osu/sample.json",self.sample)
        try:
            if ":" in res['match']['name']:
                name = res['match']['name'].split(":")
            else:
                name = res['match']['name'].split("(",1)
        except:
            name = res['match']['name']
        try:
            tname = name[0]
            team1 = name[1].split("vs")
            team2 = team1[1]
            team1 = team1[0]
            team1 = ''.join(c for c in team1 if c not in ' ()')
            team2 = ''.join(c for c in team2 if c not in ' ()')
        except:
            try:
                del team1
                del team2
                del tname
            except:
                pass
            name = res['match']['name']

        if teamVS:
            userlist0, pointlist0 = sortdict(playerlist[1])
            userlist1, pointlist1 = sortdict(playerlist[2])
            f = []
            try:
                f.append(":large_blue_circle: **{}**: ".format(team1))
            except:
                f.append(":large_blue_circle:: ")
            for index, player in enumerate(userlist0):
                try:
                    username = await get_username(self,ctx,player)
                except:
                    username = player + " (Banned)"
                f.append("**{}**: {:15} - **{:0.2f}**".format(index + 1,username,pointlist0[index]))
            f.append("")
            try:
                f.append(":red_circle: **{}**: ".format(team2))
            except:
                f.append(":red_circle:: ")
            for index, player in enumerate(userlist1):
                try:
                    username = await get_username(self,ctx,player)
                except:
                    username = player + " (Banned)"
                f.append("**{}**: {:15} - **{:0.2f}**".format(index + 1,username,pointlist1[index]))
            f = "\n".join(f)
            try:
                embed=discord.Embed(title="<a:mLoading:529680784194404352> {}: {} vs {}".format(tname,team1,team2),
                                    url="https://osu.ppy.sh/mp/" + url,
                                    description=f)
            except:
                embed=discord.Embed(title="<a:mLoading:529680784194404352> {}".format(name),
                                    url="https://osu.ppy.sh/mp/" + url,
                                    description=f)
        else:
            userlist, pointlist = sortdict(playerlist)
            f = []
            for index, player in enumerate(userlist):
                try:
                    username = await get_username(self,ctx,player)
                except:
                    username = player + " (Banned)"
                f.append("**{}**: {:15} - **{:0.2f}**".format(index + 1,username,pointlist[index]))
            f = "\n".join(f)
            try:
                embed=discord.Embed(title="<a:mLoading:529680784194404352> {}: {} vs {}".format(tname,team1,team2),
                                    url="https://osu.ppy.sh/mp/" + url,
                                    description=f)
            except:
                embed=discord.Embed(title="<a:mLoading:529680784194404352> {}".format(name),
                                    url="https://osu.ppy.sh/mp/" + url,
                                    description=f)

        await self.bot.say(embed=embed)
        dataIO.save_json("data/osu/sample.json",self.sample)
        d = time.time()
        await self.bot.edit_message(loading,"**Finished Parsing MP. Outputting Embed Message... (Took {:0.5f}s) Done. (Took {:0.5f}s) **".format(b - a,d - c))

def sortdict(main_list):
    list1 = []
    list2 = []
    try:
        od = OrderedDict(sorted(main_list.items(),key=lambda x:x[1], reverse=True))
    except:
        od = sorted(main_list.items(),key=lambda x:x[1], reverse=True)
    for key,value in od.items():
        list1.append(key)
        list2.append(value)
    return list1, list2

def parse_match(games,teamVS):
    plist = {}
    for game in games:
        try:
            del game['game_id']
        except:
            pass
        try:
            del game['play_mode']
        except:
            pass
        try:
            del game['match_type']
        except:
            pass
        try:
            del game['team_type']
        except:
            pass
        try:
            starttime = datetime.datetime.strptime(game['start_time'],"%Y-%m-%d %H:%M:%S")
            endtime = datetime.datetime.strptime(game['end_time'],"%Y-%m-%d %H:%M:%S")
            timediff = endtime - starttime
            game["time_taken"] = str(timediff)
        except:
            pass
        try:
            del game['start_time']
            del game['end_time']
            del game['scoring_type']
        except:
            pass
        scoresum = 0
        game['newscores'] = []
        game['playercount'] = 0
        for score in game['scores']:
            g = {}
            if int(score['score']) < 1000:
                continue
            g['user_id'] = score['user_id']
            if teamVS:
                try:
                    plist[int(score['team'])][g['user_id']] = 0
                except:
                    plist[int(score['team'])] = {}
                    plist[int(score['team'])][g['user_id']] = 0
            else:
                plist[g['user_id']] = 0
            g['score'] = score['score']
            g['maxcombo'] = score['maxcombo']
            g['acc'] = calculate_acc(score)
            g['enabled_mods'] = score['enabled_mods']
            scoresum += int(score['score'])
            game['playercount'] += 1
            game['newscores'].append(g)
        game['scoresum'] = scoresum
        try:
            del game['scores']
        except:
            pass
        for newscore in game['newscores']:
            avg = int(game['scoresum']) / game['playercount']
            pointcost = int(newscore['score']) / avg
            newscore['point_cost'] = pointcost
    if teamVS:
        for player,point in plist[1].items():
            pointlist = []
            for game in games:
                for score in game['newscores']:
                    if player == score['user_id']:
                        pointlist.append(score['point_cost'])
            pointmax = 0
            for i in range(0,len(pointlist)):
                pointmax += pointlist[i]
            plist[1][player] = pointmax / len(pointlist)
        for player,point in plist[2].items():
            pointlist = []
            for game in games:
                for score in game['newscores']:
                    if player == score['user_id']:
                        pointlist.append(score['point_cost'])
            pointmax = 0
            for i in range(0,len(pointlist)):
                pointmax += pointlist[i]
            plist[2][player] = pointmax / len(pointlist)
    else:
        for player,point in plist.items():
            pointlist = []
            for game in games:
                for score in game['newscores']:
                    if player == score['user_id']:
                        pointlist.append(score['point_cost'])
            pointmax = 0
            for i in range(0,len(pointlist)):
                pointmax += pointlist[i]
            plist[player] = pointmax / len(pointlist)
    return games, plist

def format_number(num):
    try:
        dec = decimal.Decimal(num)
    except:
        return 'bad'
    tup = dec.as_tuple()
    delta = len(tup.digits) + tup.exponent
    digits = ''.join(str(d) for d in tup.digits)
    if delta <= 0:
        zeros = abs(tup.exponent) - len(tup.digits)
        val = '0.' + ('0'*zeros) + digits
    else:
        val = digits[:delta] + ('0'*tup.exponent) + '.' + digits[delta:]
    val = val.rstrip('0')
    if val[-1] == '.':
        val = val[:-1]
    if tup.sign:
        return '-' + val
    return val

def paste_format(tname,team1,team2,time,mvp,mvpoint,ace,acepoint,player_list,point_list):
    f = []
    f.append("----------------------------------------------------------------------")
    f.append("-                            MATCH DETAILS                           -")
    f.append("----------------------------------------------------------------------")
    f.append("Tournament: {}".format(tname))
    f.append("{} vs. {}".format(team1,team2))
    f.append("Lobby started: {}".format(time))
    f.append("Match MVP: {} - {}".format(mvp,mvpoint))
    f.append("Match ACE: {} - {}".format(ace,acepoint))
    f.append("----------------------------------------------------------------------")
    index = 0
    for index, player in enumerate(player_list):
        f.append("#{}: {:15} - {:0.2f}".format(index + 1,player,point_list[index]))
    f = "\n".join(f)
    return f

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

async def mrank(self, ctx, mapID, mapScore, userID):
    async with aiohttp.ClientSession(headers=self.header) as session:
        try:
            async with session.get("https://osu.ppy.sh/api/get_scores?b={}&limit=100&k={}".format(mapID,self.settings['api_key'])) as channel:
                res = await channel.json()
        except Exception as e:
            await self.bot.send_message(ctx.message.channel,"Error: " + str(e))
            return
    idx = 1
    for score in res:
        if score['user_id'] == userID:
            if score['score'] == mapScore:
                return idx
        idx += 1
    return None

async def use_api(self, ctx,url):
    async with aiohttp.ClientSession(headers=self.header) as session:
        try:
            async with session.get(url) as channel:
                res = await channel.json()
                return res
        except Exception as e:
            await self.bot.send_message(ctx.message.channel,"Error: " + str(e))
            return

async def get_username(self,ctx,id):
    async with aiohttp.ClientSession(headers=self.header) as session:
        try:
            async with session.get("https://osu.ppy.sh/api/get_user?u=" + id + "&k=" + self.settings['api_key']) as channel:
                res = await channel.json()
        except Exception as e:
            await self.bot.send_message(ctx.message.channel,"Error: " + str(e))
            return
        return res[0]['username']

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
            pyttanko_json['map_completion'] = (completion / len(bmap.hitobjects)) * 100
        except:
            pyttanko_json['map_completion'] = "Error"
    if plot:
        #try:
        pyttanko_json['graph_url'] = await plot_map_stars(file_path, mods, color)
        # print(pyttanko_json['graph_url'])
        #except:
            #pass
        # print(pyttanko_json['graph_url'])

    os.remove(file_path)
    return pyttanko_json

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

def star_to_emote(sr):
    if sr <= 1.5: return "<:easys:524762856407957505>"
    if sr <= 2.25: return "<:normals:524762905560875019>"
    if sr <= 3.75: return "<:hards:524762888079015967>"
    if sr <= 5.25: return "<:insanes:524762897235312670>"
    if sr <= 6.75: return "<:experts:524762877912154142>"
    return "<:expertpluss:524762868235894819>"

def rank_to_emote(rank):
    if rank == "XH": return "<:rankingSSH:524765519686008867>"
    if rank == "X": return "<:rankingSS:524765487394062366>"
    if rank == "SH": return "<:rankingSH:524765442456289290>"
    if rank == "S": return "<:rankingS:524765397581430797>"
    if rank == "A": return "<:rankingA:524765216093765653>"
    if rank == "B": return "<:rankingB:524765259773509672>"
    if rank == "C": return "<:rankingC:524765302064676864>"
    if rank == "D": return "<:rankingD:524765348319330304>"
    if rank == "F": return "<:rankingF:524971327640305664>"

def hit_to_emote(hit):
    if hit == "hit300": return "<:hit300:524769369532792833>"
    if hit == "hit100": return "<:hit100:524769397840281601>"
    if hit == "hit50": return "<:hit50:524769420887982081>"
    if hit == "hit0": return "<:hit0:524769445936234496>"

def setup(bot):
    print("setting up...")
    n = Osu(bot)
    # bot.add_listener(n.message_triggered, "on_message")
    bot.add_cog(n)
