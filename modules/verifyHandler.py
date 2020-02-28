from discord.ext import commands
from colorama import init, Fore, Style, Back
from discord import File
from discord.utils import get
from pymongo import MongoClient
from bs4 import BeautifulSoup
from pymongo.collation import Collation, CollationStrength
from modules.commonFunctions import channelIDToName, isUserVerified
from datetime import datetime as dt
import discord, os, pymongo, json, requests, configparser, re 

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

class verifyHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    #Start verification
    @commands.command()
    async def verify(self, ctx):
        member = ctx.message.author
        await ctx.channel.send(f"<@{member.id}> >> To begin the verification process please go to https://nopixel.mja00.dev/auth and follow the prompts. Once you're done with that please run !update here.")

    @commands.command()
    async def update(self, ctx, user:discord.Member = None):
        loadingMessage = await ctx.channel.send("Assigning roles... please wait.")
        if user is None:
            user = ctx.message.author
        if isUserVerified(users, user):
            await removeRoles(user)
            rolesAdded = await addRoles(users, user, ctx)
            await loadingMessage.delete()
            if rolesAdded == 0:
                await ctx.channel.send(f"<@{user.id}> >> It seems that we either have no roles for the streamers you mod for **or** you don't mod for any NoPixel streamers.")
            else:
                modRole = discord.utils.get(user.guild.roles, name="Mod")
                await user.add_roles(modRole)
        else:
            await ctx.channel.send(f"<@{user.id}> >> You aren't verified yet. Please verify yourself through https://nopixel.mja00.dev/auth and then try again.")
    
    @commands.command()
    @commands.has_any_role('Discord MANAGER', 'Owner', 'Mods Moderator')
    async def updateall(self, ctx):
        await ctx.channel.send("Updating everyone's roles. This will take a while.")
        await ctx.channel.send("Getting a list of all users.")
        allMembers = ctx.message.author.guild.members
        verfiedUsers = 0
        unverifiedUsers = 0
        for member in allMembers:
            if member.bot:
                pass
            else:
                if isUserVerified(users, member):
                    await removeRoles(member)
                    await addRoles(users, member, ctx)
                    verfiedUsers += 1
                else:
                    await ctx.channel.send(f"{member.display_name} is not verified. Skipping.")
                    unverified = discord.utils.get(member.guild.roles, name="UNVERIFIED")
                    await member.add_roles(unverified)
                    unverifiedUsers += 1
        await ctx.channel.send(f"Everyone has been updated. Total: {verfiedUsers + unverifiedUsers} | Verified: {verfiedUsers} | Unverified: {unverifiedUsers}")

    @commands.command()
    @commands.has_any_role('Discord MANAGER', 'Owner', 'Mods Moderator')
    async def whois(self, ctx, user:discord.Member = None):
        if user is None:
            await ctx.channel.send("Please specify a user")
        else:
            userVerified = isUserVerified(users, user)
            if userVerified:
                result = users.find_one({'discord': str(user.id)})
                channelID = result["twitch"]
                verificationDate = result["_id"].generation_time
                verificationDate = dt.strftime(verificationDate, "%m/%d/%Y %H:%M:%S")
                embed = discord.Embed(
                    title = f"Info for {user.display_name}",
                    colour = discord.Color.blurple()
                )
                embed.add_field(name="Display Name", value=user.display_name, inline=True)
                embed.add_field(name="Twitch Name", value=channelIDToName(channelID, clientID), inline=True)
                embed.add_field(name="ChannelID", value=channelID, inline=True)
                embed.add_field(name="Discord ID", value=user.id, inline=True)
                embed.add_field(name="Verification Date", value=verificationDate)
                await ctx.channel.send(embed=embed)
            else:
                await ctx.channel.send("User isn't verified")


def doesStreamerExist(streamer):
    url = "https://nopixel.hasroot.com/streamers.php"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    for x in (soup.find_all(string=re.compile(streamer, flags=re.I))):
        return True
    return False

async def addRoles(db, user, ctx):
    rolesAdded = 0
    uuid = user.id
    channelID = None
    result = db.find_one({'discord': str(uuid)})
    channelID = result["twitch"]
    twitchName = channelIDToName(channelID, clientID)
    url = f"https://modlookup.mja00.dev/api/mods/user/{twitchName}"
    data = json.loads(requests.get(url).text)
    rolesToAdd = []
    if doesStreamerExist(twitchName):
        streamerRole = discord.utils.get(user.guild.roles, name="Streamers")
        rolesToAdd.append(streamerRole)
    for channel in data["channels"]:
        modChan = channel["channel"]
        roleName = f"{modChan} mods"
        try:        
            role = discord.utils.get(user.guild.roles, name=roleName)
            if role is None:
                continue
            else:
                rolesToAdd.append(role)
                rolesAdded += 1
        except discord.DiscordException:
            pass
    await user.add_roles(*rolesToAdd)
    await ctx.channel.send(f"Roles updated for {user.display_name}")
    print(f"{user.name} has been updated.")
    return rolesAdded

async def removeRoles(user):
    authorRoles = user.roles[1:]
    dontRemoveList = ["nsfw", "pingme", "Mod", "Discord MANAGER", "Mods Moderator", "Streamers", "Twitch Staff", "Nopixel Staff", 'mcserver', 'Nitro Booster', 'Owner']
    rolesRemoved = 0
    rolesToRemove = []
    for role in authorRoles:
        roleRemoved = discord.utils.get(user.guild.roles, name=str(role))
        if roleRemoved.name in dontRemoveList:
            pass
        else:
            rolesToRemove.append(roleRemoved)
            rolesRemoved += 1
    member = user
    await member.remove_roles(*rolesToRemove)


def setup(bot):
    bot.add_cog(verifyHandler(bot))