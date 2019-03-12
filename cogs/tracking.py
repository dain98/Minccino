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

class Tracking:
    """new class just for tracking"""

    def __init__(self,bot):
        self.bot = bot
        self.header = {"User-Agent": "User_Agent"}
        self.settings = dataIO.load_json("data/osu/settings.json")
        self.users = dataIO.load_json("data/osu/users.json")
        self.maps = dataIO.load_json("data/osu/maps/maps.json")
        self.tracking = dataIO.load_json("data/osu/tracking.json")

    @commands.group(pass_context=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def osutrack(self,ctx):
        """Add users for tracking in this channel!"""

        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
    @osutrack.command(pass_context=True)
    async def add(self,ctx,*username_list):
        username = " ".join(username_list)
        res = await use_api(self,"https://osu.ppy.sh/api/get_user?k=" + self.settings['api_key'] + "&u=" + username)
        if len(res) == 0:
            await self.bot.send_message(ctx.message.channel,"User not found in osu! database! :x:")
            return
        username = res[0]['username']
        if username in self.tracking:
            if ctx.message.channel.id in self.tracking[username]['channels']:
                await self.bot.send_message(ctx.message.channel,username + " is already being tracked in this channel!")
                return
        if username not in self.tracking:
            self.tracking[username] = {}
            self.tracking[username]['channels'] = []
        self.tracking[username]['channels'].append(ctx.message.channel.id)
        dataIO.save_json("data/osu/tracking.json",self.tracking)
        await self.bot.send_message(ctx.message.channel,username + " is now being tracked in this channel. :white_check_mark:")

    @osutrack.command(pass_context=True)
    async def remove(self,ctx,*username_list):
        username = " ".join(username_list)
        if username in self.tracking:
            if ctx.message.channel.id in self.tracking[username]['channels']:
                self.tracking[username]['channels'].remove(ctx.message.channel.id)
                if len(self.tracking[username]['channels']) == 0:
                    del(self.tracking[username])
                await self.bot.send_message(ctx.message.channel,username + " is no longer being tracked in this channel. :white_check_mark:")
                dataIO.save_json("data/osu/tracking.json",self.tracking)
                return
        await self.bot.send_message(ctx.message.channel,username + " was never being tracked in this channel!")

    @osutrack.command(pass_context=True)
    async def list(self,ctx):
        f = []
        f.append("```")
        f.append("Players Being Tracked in this Channel:")
        f.append("--------------------------------------------")
        for key,value in self.tracking.items():
            if ctx.message.channel.id in value['channels']:
                f.append("- " + key)
        f.append("```")
        await self.bot.send_message(ctx.message.channel,"\n".join(f))

    # async def track_loop(self):
    #     # Save/Update top 50 information of a player
    #     self.tracking = dataIO.load_json("data/osu/tracking.json")
    #     count = 0
    #     while self == self.bot.get_cog("Tracking"):
    #         print("Test")
    #         for username, data in self.tracking.items():
    #             res = await use_api(self,"https://osu.ppy.sh/api/get_user_best?k=" + self.settings['api_key'] + "&u=" + username + "&limit=100")
    #             if len(res) == 0:
    #                 res2 = await use_api(self,"https://osu.ppy.sh/api/get_user?k=" + self.settings['api_key'] + "&u=" + username)
    #                 if len(res2) == 0:
    #                     self.tracking.pop(username, None)
    #                     dataIO.save_json("data/osu/tracking.json",self.tracking)
    #                     print("Removed " + username + " from json: either banned or renamed")
    #                     return
    #             if "topplays" in data:
    #                 if res is data['topplays']:
    #                     print("test2")
    #                     return
    #             self.tracking[username]['topplays'] = []
    #             self.tracking[username]['topplays'].append(res)
    #             dataIO.save_json("data/osu/tracking.json",self.tracking)
    #             print("Updated " + username + " Count: " + str(count))
    #             count+=1
    #             if count == 800:
    #                 print("API has reached its limit! Resetting...")
    #                 await asyncio.sleep(60)
    #                 count = 0

def eventrank(event):
    stri = "<img src='\/images\/S_small.png'\/> <b><a href='\/u\/3099689'>Xilver15<\/a><\/b> achieved <b>rank #2<\/b> on <a href='\/b\/261464?m=0'>Venetian Snares - Hajnal [broken]<\/a> (osu!)"
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', event)
    event = cleantext.split('achieved rank #')
    event = event[1].split('on')
    return event[0]

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

async def use_api(self,url):
    async with aiohttp.ClientSession(headers=self.header) as session:
        try:
            async with session.get(url) as channel:
                res = await channel.json()
                return res
        except asyncio.CancelledError:
            print("timed out")
            return
        except Exception as e:
            print("Error: " + e)
            return

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
    n = Tracking(bot)
    # loop = asyncio.get_event_loop()
    # loop.create_task(n.track_loop())
    bot.add_cog(n)
