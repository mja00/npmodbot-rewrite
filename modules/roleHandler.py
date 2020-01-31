from discord.ext import commands
from colorama import init, Fore, Style, Back
from discord import File
from discord.utils import get
from pymongo import MongoClient
from pymongo.collation import Collation, CollationStrength
from modules.commonFunctions import channelIDToName, isUserVerified
from datetime import datetime as dt
import discord, os, pymongo, json, requests, random

class roleHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pingme(self, ctx):
        user = ctx.message.author
        role = discord.utils.get(ctx.message.author.guild.roles, name="pingme")
        await ctx.message.author.add_roles(role)
        await ctx.channel.send(f"<@{user.id}> >> You've been added to the ping role. You will now get pinged for stuff.")
    
    @commands.command()
    async def mcserver(self, ctx):
        user = ctx.message.author
        role = discord.utils.get(ctx.message.author.guild.roles, name="mcserver")
        await ctx.message.author.add_roles(role)
        await ctx.channel.send(f"<@{user.id}> >> You will now get pinged about information about the Minecraft server.")

def setup(bot):
    bot.add_cog(roleHandler(bot))