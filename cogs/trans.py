import discord
import asyncio
from .utils.dataIO import dataIO
from string import ascii_letters
from .utils import checks
import os
import re
import aiohttp
from discord.ext import commands
from random import uniform
from googletrans import Translator
import pycountry
class Translate:
    """Basic Commands Utilizing Google Translate API"""

    def __init__(self,bot):
        self.bot = bot
        self.header = {"User-Agent": "User_Agent"}
        self.translator = Translator()

    @commands.command(pass_context=True)
    async def tr(self,ctx,lang,*sentence_list):
        """default translation command!"""
        sentence = " ".join(sentence_list)
        try:
            translation = self.translator.translate(sentence, dest=lang)
            try:
                lng = pycountry.languages.get(alpha_2=lang)
                await self.bot.say("\"" + translation.origin + " \" is **\"" + translation.text + "\"** in " + lng.name + ". ")
            except:
                lang = lang.capitalize()
                await self.bot.say("\"" + translation.origin + " \" is **\"" + translation.text + "\"** in " + lang + ". ")
        except Exception as e:
            await self.bot.say(str(e) + ". ")

    @commands.command(pass_context=True)
    async def detect(self,ctx,*sentence_list):
        """Detect the language of a sentence!"""
        sentence = " ".join(sentence_list)
        translation = self.translator.detect(sentence)
        confid = int(translation.confidence) * 100
        try:
            lang = pycountry.languages.get(alpha_2=translation.lang)
            await self.bot.say("I'm " + str(confid) + "% confident that " + sentence + " is " + lang.name + ". ")
        except:
            await self.bot.say("I'm " + str(confid) + "% confident that " + sentence + " is " + translation.lang + ". ")

def setup(bot):
    print("setting up...")
    n = Translate(bot)
    bot.add_cog(n)
