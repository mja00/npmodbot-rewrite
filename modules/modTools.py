from discord.ext import commands
from colorama import init, Fore, Style, Back
from discord import File
from discord.utils import get
from pymongo import MongoClient
from pymongo.collation import Collation, CollationStrength
from modules.commonFunctions import channelIDToName, isUserVerified
from datetime import datetime as dt
from bs4 import BeautifulSoup
import discord, os, pymongo, json, requests, random, configparser, asyncio, shutil

#Read connection config
config = configparser.ConfigParser()
config.read('config.ini')

host = config['mysql']['host']
user = config['mysql']['user']
passwd = config['mysql']['passwd']
database = config['mysql']['database']
ignoredStreams = ['lirik', 'sodapoppin', 'forsen', 'timthetatman', 'kitboga', 'xqcow', 'nymn', 'moonmoon', 'mizkif', 'greekgodx', 'amouranth']

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
    @commands.has_any_role('Owner', 'Discord MANAGER', 'Mods Moderator')
    async def allroles(self, ctx, minimumUsers = 1):
        rolesInServer = ctx.message.author.guild.roles
        roleCount = len(rolesInServer)
        await ctx.channel.send(f"Getting a list, this will take **at most** {roleCount * 5} seconds to complete.")
        for role in rolesInServer:
            roleName = role.name
            memberCount = len(role.members)
            if memberCount < minimumUsers:
                if roleName not in ['@everyone', 'everyone', 'Mod', 'Streamer']:
                    await ctx.channel.send(f"{roleName} | {memberCount}")
        await ctx.channel.send("Query complete")    

    @commands.command()
    async def invite(self, ctx):
        member = ctx.message.author
        channel = ctx.channel
        invite = await channel.create_invite(max_age=10800, max_uses=5, reason=f"Auto invite for {ctx.message.author.name}")
        await member.send(f"Here's the invite. This is valid for 5 uses and for 3 hours. If you need more than 5 use please contact mja00. {invite.url}")
    
    @commands.command()
    @commands.has_any_role('Owner', 'Discord MANAGER', 'Mods Moderator')
    async def scrapestreamers(self, ctx):
        url = "https://nopixel.hasroot.com/streamers.php"
        r = requests.get(url)
        currentTime = dt.now()

        soup = BeautifulSoup(r.content, features='html.parser')
        mydivs = soup.findAll('a', {'class': 'streamerName'})
        streamerNames = []
        for streamer in mydivs:
            streamerData = soup.find('div', {'data-streamername': streamer.text})['data-lastonline']
            time = dt.strptime(streamerData, '%Y-%m-%d %H:%M:%S')
            timeSince = (currentTime - time).total_seconds()
            if timeSince <= 784000:
                streamerNames.append(streamer.text.lower())

        with open('streamers.py', 'w') as file:
            file.write('Streamers = ')
            file.write(str(streamerNames))
            shutil.copy2('streamers.py', '/home/ubuntu/nptwitchbot')
        print(f"Successfully scraped {len(streamerNames)} from HasRoot. Filed was copied to the correct directory. Have MJ reboot the Twitch bot.")
        


def setup(bot):
    bot.add_cog(modTools(bot))