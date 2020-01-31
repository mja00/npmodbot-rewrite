from discord.ext import commands
from colorama import init, Fore, Style, Back
from discord import File
from discord.utils import get
from pymongo import MongoClient
from pymongo.collation import Collation, CollationStrength
from modules.commonFunctions import channelIDToName, isUserVerified
from datetime import datetime as dt
import discord, os, pymongo, json, requests, random, configparser

#Read connection config
config = configparser.ConfigParser()
config.read('config.ini')

host = config['mysql']['host']
user = config['mysql']['user']
passwd = config['mysql']['passwd']
database = config['mysql']['database']

clientID = config['mainsettings']['clientID']
client = pymongo.MongoClient(config['mainsettings']['mongoDB'])
db = client.nopixel
users = db.users

class modTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_any_role('Owner', 'Discord MANAGER', 'Mods Moderator')
    async def createrole(self, ctx, name = None):
        if name is None:
            await ctx.channel.send("Please specify a name for the role.")
        else:
            colorRGB = discord.Colour.from_rgb(r=random.randint(0,255), g=random.randint(0,255), b=random.randint(0,255))
            guild = ctx.message.author.guild
            role = await guild.create_role(name=f"{name} mods", colour=colorRGB, hoist=True, mentionable=True, reason="Bot created role.")
            colorCode = hex(colorRGB.value)
            await ctx.channel.send(f"'{role.name}' role created with the color code {colorCode}.")
            print(f"{role.name} has been created.")

    @commands.command()
    @commands.has_any_role('Owner', 'Discord MANAGER', 'Mods Moderator')
    async def purge(self, ctx, amount = 5):
        await ctx.channel.purge(limit=amount+1, bulk=True)
    
    @commands.command()
    async def printroles(self, ctx):
        await ctx.channel.send(f"{len(ctx.message.author.guild.roles)}/250 roles in the server.")
    
    @commands.command()
    async def invite(self, ctx):
        member = ctx.message.author
        channel = ctx.channel
        invite = await channel.create_invite(max_age=10800, max_uses=5, reason=f"Auto invite for {ctx.message.author.name}")
        await member.send(f"Here's the invite. This is valid for 5 uses and for 3 hours. If you need more than 5 use please contact mja00. {invite.url}")


def setup(bot):
    bot.add_cog(modTools(bot))