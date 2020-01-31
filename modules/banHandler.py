from discord.ext import commands
from colorama import init, Fore, Style, Back
from discord import File
from discord.utils import get
from pymongo import MongoClient
from pymongo.collation import Collation, CollationStrength
from modules.commonFunctions import channelIDToName, isUserVerified
from datetime import datetime as dt
import mysql.connector as mysql
import discord, os, pymongo, json, requests, random, asyncio, configparser

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
logs = db.twitchlogs

class banHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #add user to banned list
    @commands.command()
    async def banned(self, ctx, channel = None, bannedUser = None, *args):
        db = mysql.connect(
        host = host,
        user = user,
        passwd = passwd,
        database = database
        )
        cursor = db.cursor()
        output = ""
        for word in args:
            output += word.replace("'", '')
            output += " "
        if channel is None:
            await ctx.channel.send("The correct usage is: !banned <channel user is banned in> <banned user> <reason>")
        elif bannedUser is None:
            await ctx.channel.send("The correct usage is: !banned <channel user is banned in> <banned user> <reason>")
        elif output == "":
            await ctx.channel.send("The correct usage is: !banned <channel user is banned in> <banned user> <reason>")
        else:
            try:
                query = "SELECT * FROM banned WHERE reporter = %s AND twitchuser = %s"
                values = (str(channel), str(bannedUser),)
                cursor.execute(query, values)
                result = cursor.fetchone()
                banID = result[0]
                updateReason(banID, output)
                await ctx.message.author.guild.get_channel(579446002906300442).send(f"`{bannedUser}` has already been reported as banned from `{channel}`. Ban ID #{banID}. I've gone ahead and updated the reason to `{output}`")
                await ctx.message.author.guild.get_channel(579446002906300442).send("═════════════")
                await ctx.channel.send(u"\u2705")
            except:
                query = "INSERT INTO banned (reporter, twitchuser, reason) VALUES (%s, %s, %s)"
                values = (str(channel), str(bannedUser), str(output))
                cursor.execute(query, values)
                db.commit()
                cursor.close()
                db.close()
                await ctx.message.author.guild.get_channel(579446002906300442).send(f'`{bannedUser}` has been recorded as being banned from `{channel}` for the reason `{output}`. This has nothing to do with prebanning, just logging user bans.')
                await ctx.message.author.guild.get_channel(579446002906300442).send("═════════════")
                await ctx.channel.send("")
    
    #chatlog function
    @commands.command()
    async def chatlog(self, ctx, channel = None, user = None, amount:int = 25):
        if channel is None or user is None:
            await ctx.channel.send("The proper use of this command is `!chatlog <channel> <user> [amount]`")
        else:
            if amount > 100:
                amount = 99
            #If they want all channels do this
            if channel == "global":
                messageString = "```\n"
                messages = []
                results = logs.find({'author': user.lower()}, {'author': 0}, limit=int(amount)).sort("_id", -1)
                if results.count(with_limit_and_skip=True) == 0:
                    await ctx.channel.send(f"We found no logs for `{user}`.")
                else:
                    for x in results:
                        channel = x["channel"]
                        message = x["content"]
                        timeStamp = x["_id"].generation_time.strftime('%Y-%m-%d %H:%M:%S')
                        appendString = f"{timeStamp} | #{channel} | {user}:{message}\n"
                        messages.append(appendString)
                    messages.reverse()
                    for message in messages:
                        messageString += message
                    messageString += "```"
                    try:
                        firstMessage = await ctx.channel.send(f"Last {results.count(with_limit_and_skip=True)} messages for {user} in NoPixel streams.")
                        await ctx.channel.send(messageString)
                    except discord.HTTPException:
                        await firstMessage.delete()
                        await ctx.channel.send("The message sent would be too big. Try a smaller message count.")
            else:
                messageString = "```\n"
                messages = []
                results = logs.find({'author': user.lower(), 'channel': channel.lower()}, {'channel':0, 'author': 0}, limit=amount).sort("_id", -1)
                if results.count(with_limit_and_skip=True) == 0:
                    await ctx.channel.send(f"We found no logs for `{user}` in `{channel}`.")
                else:
                    for x in results:
                        message = x["content"]
                        timeStamp = x["_id"].generation_time.strftime('%Y-%m-%d %H:%M:%S')
                        appendString = f"{timeStamp} | {user}:{message}\n"
                        messages.append(appendString)
                    messages.reverse()
                    for message in messages:
                        messageString += message
                    messageString += "```"
                    try:
                        firstMessage = await ctx.channel.send(f"Last {results.count(with_limit_and_skip=True)} messages for {user} in {channel}.")
                        await ctx.channel.send(messageString)
                    except discord.HTTPException:
                        await firstMessage.delete()
                        await ctx.channel.send("The message sent would be too big. Try a smaller message count.")


def updateReason(banID, reason):
    db = mysql.connect(
        host = host,
        user = user,
        passwd = passwd,
        database = database
    )
    cursor = db.cursor()
    sql = "UPDATE banned SET reason = %s WHERE id = %s"
    val = (str(reason), int(banID),)
    cursor.execute(sql, val)
    db.commit()
    cursor.close()
    db.close()


def setup(bot):
    bot.add_cog(banHandler(bot))