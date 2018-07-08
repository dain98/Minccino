import discord
import asyncio
from .utils.dataIO import dataIO
from string import ascii_letters
from .utils import checks
import os
import re
import aiohttp
import json
import math
from discord.ext import commands
import py_gg

class League:
    """The main League of Legends cog"""

    def __init__(self,bot):
        self.bot = bot
        self.header = {"User-Agent": "User_Agent"}
        self.settings = dataIO.load_json("data/league/settings.json")
        self.summoners = dataIO.load_json("data/league/summoners.json")
        py_gg.init(self.settings['api_key'])

    @commands.command(pass_context=True)
    async def summoner(self,ctx,region,*summname_list):
        cnl = ctx.message.channel
        uid = ctx.message.author.id
        region = region.upper()
        if region == "NA":
            region = "NA1"
        elif region == "BR":
            region = "BR1"
        elif region == "OCE":
            region = "OC1"
        elif region == "JP":
            region = "JP1"
        elif region == "EUNE":
            region = "EUN1"
        elif region == "EUW":
            region = "EUW1"
        elif region == "TR":
            region = "TR1"
        elif region == "LAN":
            region = "LA1"
        elif region == "LAS":
            region = "LA2"
        region = region.lower()
        summname = " ".join(summname_list)
        if summname == "":
            if uid not in self.users:
                await self.bot.say("**User not set! Please set your League username using -leagueset [Region] [Summoner]! :x:**")
                return
            else:
                summname = self.summoners[uid]['summoner_name']
                verified = self.summoners[uid]['verified']

        # Get summoner data
        url = "https://" + region + ".api.riotgames.com/lol/summoner/v3/summoners/by-name/" + summname + "?api_key=" + self.settings['api_key2']
        summdetails = await getjson(self,url)
        if summdetails is None:
            return
        else:
            if 'status' in summdetails:
                if "Data not found" in summdetails['status']:
                    await self.bot.send_message(cnl,"Summoner not found! :x:")
                    return
                else:
                    await self.bot.send_message(cnl,"Error code " + str(summdetails['status']['status_code']) + ": " + str(summdetails['status']['message']))
                    return
        name = summdetails['name']
        pIconId = summdetails['profileIconId']
        level = summdetails['summonerLevel']
        id = summdetails['id']

        url = "https://" + region + ".api.riotgames.com/lol/league/v3/positions/by-summoner/" + str(id) + "?api_key=" + self.settings['api_key2']
        rankedstats = await getjson(self,url)
        unranked = False
        if rankedstats is None:
            return
        else:
            if len(rankedstats) == 0: # Checking if unranked
                unranked = True

        url = "https://" + region + ".api.riotgames.com/lol/champion-mastery/v3/champion-masteries/by-summoner/" + str(id) + "?api_key=" + self.settings['api_key2']
        masterystats = await getjson(self,url)
        if masterystats is None:
            return
        masterystats = masterystats[0:3]
        url = "https://ddragon.leagueoflegends.com/api/versions.json"
        currentVer = await getjson(self,url)
        currentVer = currentVer[0]
        # url = "http://ddragon.leagueoflegends.com/cdn/" + currentVer + "/data/en_US/championFull.json"
        # champkeys = await getjson(self,url)
        # champkeys = champkeys['keys']
        champkeys = dataIO.load_json("data/league/champkeys.json")
        i = 1
        isStart = True
        numpage = len(rankedstats) + 1
        while(True):
            f = []
            if i == 1:
                f.append("▸ **" + name + "**")
                f.append("▸ Level **" + str(level) + "**")
                f.append("▸ **Champion Masteries**: ")
                for num, data in enumerate(masterystats):
                    champId = int(data['championId'])
                    champName = str(champkeys[str(champId)])
                    champLevel = int(data['championLevel'])
                    champPoints = int(data['championPoints'])
                    f.append("  ▸ **" + champName + "**: ")
                    f.append("      ▸ Level **" + str(champLevel) + "**")
                    f.append("      ▸ **" + str(champPoints) + "** points")
                    if champLevel != 7:
                        pointsUntil = int(data['championPointsUntilNextLevel'])
                        f.append("      ▸ **" + str(pointsUntil) + "** points until level **" + str(champLevel + 1) + "**")
                embed = discord.Embed(colour=0x00FFFF,title="Summoner information for %s"%name,description="\n".join(f))
                embed.set_thumbnail(url="http://ddragon.leagueoflegends.com/cdn/" + currentVer + "/img/profileicon/" + str(pIconId) + ".png")
                embed.set_footer(text="Page " + str(i) + " of " + str(math.ceil(numpage)))
            elif unranked == False:
                pnum = i - 2
                if rankedstats[pnum]['queueType'] == "RANKED_SOLO_5x5":
                    qType = "Ranked Solo/Duo"
                elif rankedstats[pnum]['queueType'] == "RANKED_FLEX_TT":
                    qType = "Ranked Flex 3v3/Twisted Treeline"
                elif rankedstats[pnum]['queueType'] == "RANKED_FLEX_SR":
                    qType = "Ranked Flex 5v5"
                if rankedstats[pnum]['rank'] == "I":
                    rank = 1
                elif rankedstats[pnum]['rank'] == "II":
                    rank = 2
                elif rankedstats[pnum]['rank'] == "III":
                    rank = 3
                elif rankedstats[pnum]['rank'] == "IV":
                    rank = 4
                elif rankedstats[pnum]['rank'] == "V":
                    rank = 5
                tier = rankedstats[pnum]['tier'] + " " + rankedstats[pnum]['rank']
                leaguePoints = str(rankedstats[pnum]['leaguePoints']) + "LP"
                wins = rankedstats[pnum]['wins']
                losses = rankedstats[pnum]['losses']
                winratio = round(wins/(wins + losses),2)
                winratio = int(winratio * 100)
                inactive = rankedstats[pnum]['inactive']
                leagueName = rankedstats[pnum]['leagueName']

                f.append("▸ **" + qType + "**")
                f.append("▸ **" + tier + "** " + leaguePoints)
                f.append("▸ **" + leagueName + "**")
                f.append("▸ **" + str(wins) + "**W **" + str(losses) + "**L")
                f.append("  ▸ **" + str(winratio) + "**% Win Ratio")
                if inactive == True:
                    f.append("▸ **CURRENTLY DECAYING**")
                embed = discord.Embed(colour=0x00FFFF,title="Summoner information for %s"%name,description="\n".join(f))
                embed.set_thumbnail(url="http://opgg-static.akamaized.net/images/medals/" + rankedstats[pnum]['tier'].lower() + "_" + str(rank) + ".png")
                embed.set_footer(text="Page " + str(i) + " of " + str(math.ceil(numpage)))
            try:
                if isStart:
                    isStart = False
                    msg = await self.bot.send_message(cnl,embed=embed)
                    await self.bot.add_reaction(msg,"⬅")
                    await self.bot.add_reaction(msg,"➡")
                    await self.bot.add_reaction(msg,"✅")
                else:
                    await self.bot.edit_message(msg,embed=embed)
                res1 = await self.bot.wait_for_reaction(['⬅','➡','✅'], user=ctx.message.author, message=msg, timeout=60)
                if res1 is None:
                    await self.bot.delete_message(msg)
                    return
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
                await self.bot.delete_message(temp2)

async def getjson(self,url):
    async with aiohttp.ClientSession(headers=self.header) as session:
        try:
            async with session.get(url) as channel:
                results = await channel.json()
                return results
        except Exception as e:
            await self.bot.send_message(cnl,"Error: " + str(e))
            return None
def setup(bot):
    print("setting up...")
    n = League(bot)
    bot.add_cog(n)
