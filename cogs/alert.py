import discord
import asyncio
from .utils.dataIO import dataIO
from string import ascii_letters
from .utils import checks
import os
import re
import aiohttp
import datetime
import time
from discord.ext import commands
from random import uniform
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class Alert:
    """Test cog for alerts"""

    def __init__(self,bot):
        self.bot = bot
        self.header = {"User-Agent": "User_Agent"}
        self.channelObj = self.bot.get_channel("438244772755537926")
        self.count = 0
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('data/alert/alertkeyfile.json', scope)
        gc = gspread.authorize(credentials)
        self.sh = gc.open_by_key('1_Mug_zaLV9GKWg1zmirplMFK1D2fmXXdFuYvj2E-C_k')

    @commands.command(pass_context=True)
    async def sread(self,ctx,loc,wkshtid):
        """Testing! Output a value in a cell for a specific sheet."""
        try:
            wksht = self.sh.worksheet(wkshtid)
            await self.bot.say("Cell " + loc + " has value " + wksht.acell(loc).value)
            if wksht.acell(loc).value is "":
                await self.bot.say("The Cell is Empty!")
        except Exception as e:
            await self.bot.say("Error: " + str(type(e)))


    async def alerts(self):
        f = "%m/%d/%Y %H:%M"
        d_str1 = datetime.timedelta(minutes=15)
        d_str2 = datetime.timedelta(minutes=5)
        d_str3 = datetime.timedelta(minutes=10)
        print(d_str1 < d_str2)
        wksht = self.sh.worksheet('BotAlert')
        while self == self.bot.get_cog("Alert"):
            wkshtlists = wksht.get_all_values()
            for i, wkshtlist in enumerate(wkshtlists[1:]):
                dtime = datetime.datetime.strptime(wkshtlist[0], f)
                print(dtime)
            break

    # async def countdown(self):
    #     msg = await self.bot.send_message(self.channelObj,"Counting up... 0")
    #     while self == self.bot.get_cog("Alert"):
    #         self.count += 1
    #         await self.bot.edit_message(msg,"Counting up... " + str(self.count))
    #         await asyncio.sleep(1)
def setup(bot):
    print("Setting up...")
    loop = asyncio.get_event_loop()
    n = Alert(bot)
    loop.create_task(n.alerts())
    bot.add_cog(n)
