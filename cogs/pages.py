import discord
from string import ascii_letters
import os
import re
from .utils.chat_formatting import pagify
from discord.ext import commands

class Pages:
    """Paging testing Cog"""

    def __init__(self,bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def test(self,ctx):
        f = []
        f.append("Hello")
        f.append("GOodbye")
        msg = "\n".join(msg)
        for page is pagify(msg)
        embed = discord.Embed(colour=0x00FFFF,title="Hey",description=''.join(f))

        await self.bot.send_message(ctx.message.channel,embed=embed)
    @commands.command(pass_context=True)
    async def page(self,ctx):
        i=1
        isStart = True
        while(True):
            print("during while", i)
            embed = discord.Embed(colour=0x00FFFF,title="Testing",description="Page %d"%i)
            if isStart:
                isStart = False
                msg = await self.bot.send_message(ctx.message.channel,embed=embed)
                await self.bot.add_reaction(msg,"⬅")
                await self.bot.add_reaction(msg,"➡")
                await self.bot.add_reaction(msg,"❌")
            else:
                await self.bot.edit_message(msg,embed=embed)
            res = await self.bot.wait_for_reaction(['⬅','➡','❌'], user=ctx.message.author, message=msg, timeout=60)
            if res is None:
                await self.bot.clear_reactions(msg)
                break
            elif "➡" in res.reaction.emoji:
                i += 1
                await self.bot.remove_reaction(msg,"➡",ctx.message.author)
            elif "⬅" in res.reaction.emoji and i is not 1:
                i -= 1
                await self.bot.remove_reaction(msg,"⬅",ctx.message.author)
            elif '❌' in res.reaction.emoji:
                await self.bot.clear_reactions(msg)
                break
            else:
                print("else", res.reaction.emoji)
                await self.bot.remove_reaction(msg,"⬅",ctx.message.author)
                await self.bot.remove_reaction(msg,"➡",ctx.message.author)

    @commands.command(pass_context=True)
    async def page2(self,ctx):
        i=1
        isStart = True
        numpage = 8
        while(True):
            print("during while", i)
            embed = discord.Embed(colour=0x00FFFF,title="Testing",description="Page %d"%i)
            if isStart:
                isStart = False
                msg = await self.bot.send_message(ctx.message.channel,embed=embed)
                await self.bot.add_reaction(msg,"➡")
                await self.bot.add_reaction(msg,"❌")
            else:
                await self.bot.edit_message(msg,embed=embed)
            res = await self.bot.wait_for_reaction(['⬅','➡','❌'], user=ctx.message.author, message=msg, timeout=60)
            if res is None:
                await self.bot.clear_reactions(msg)
                break
            elif "➡" in res.reaction.emoji and (i < numpage):
                i += 1
                if i == numpage:
                    await self.bot.clear_reactions(msg)
                    await self.bot.add_reaction(msg,"⬅")
                    await self.bot.add_reaction(msg,"➡")
                    await self.bot.add_reaction(msg,"❌")
                await self.bot.remove_reaction(msg,"➡",ctx.message.author)
            elif "⬅" in res.reaction.emoji and i is not 1:
                i -= 1
                if i == 1:
                    await self.bot.clear_reactions(msg)
                    await self.bot.add_reaction(msg,"⬅")
                    await self.bot.add_reaction(msg,"➡")
                    await self.bot.add_reaction(msg,"❌")
                await self.bot.remove_reaction(msg,"⬅",ctx.message.author)
            elif '❌' in res.reaction.emoji:
                await self.bot.clear_reactions(msg)
                break
            else:
                if i == 1:
                    await self.bot.remove_reaction(msg,"⬅",self.bot.user)
                elif i == numpage:
                    await self.bot.remove_reaction(msg,"➡",self.bot.user)
                await self.bot.remove_reaction(msg,"⬅",ctx.message.author)
                await self.bot.remove_reaction(msg,"➡",ctx.message.author)
def setup(bot):
    print("setting up...")
    n = Pages(bot)
    bot.add_cog(n)
