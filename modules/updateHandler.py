from discord.ext import commands
from colorama import init, Fore, Style, Back
from discord import File
from discord.utils import get
from pymongo import MongoClient
from pymongo.collation import Collation, CollationStrength
from modules.commonFunctions import channelIDToName, isUserVerified
from datetime import datetime as dt
import git
import mysql.connector as mysql
import discord, os, pymongo, json, requests, random


class updateHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_any_role('Discord MANAGER')
    async def pullupdate(self, ctx):
        await ctx.channel.send("Pulling update.")
        #Pulls using stored creds
        stream = os.popen('git pull')
        #Gets response from that
        output = stream.readlines()
        message = ""
        for line in output:
            message += line
        #Outputs to discord
        await ctx.channel.send(message)


def setup(bot):
    bot.add_cog(updateHandler(bot))