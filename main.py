from discord.ext import commands
from colorama import init, Fore, Style, Back
from datetime import datetime as dt
from os import listdir
from os.path import isfile, join
import discord, os, sys, traceback, asyncio

print(f"{Fore.GREEN}Starting up.")

#Read token file
try:
    token_file = open("token", "r")
    tokenForm = token_file.readline()
    token = str.strip(tokenForm)
except:
    print("No token file")
    sys.exit(1)
init(convert=True)

cogs_dir = "modules"

bot = commands.Bot(command_prefix="!", status=discord.Status.do_not_disturb, activity=discord.Streaming(name="Starting...", url="https://twitch.tv/mja00"))
bot.remove_command("help")

initHandlers = ['verifyHandler', 'modTools', 'roleHandler', 'banHandler', 'updateHandler']

#Create the logs dirs
print(f"{Fore.GREEN}Checking for a logs directory")
if not os.path.exists("logs"):
    os.makedirs("logs")
else:
    print("Main log directory found.\n")
if not os.path.exists("logs/chat"):
    print(Fore.RED + "chat log directory not found. Creating it.")
    os.makedirs("logs/chat")
else:
    print(Fore.GREEN + "chat log directory found.")



@bot.event
async def on_ready():
    print(f"{Fore.GREEN}NoPixel Modbot V2 Initialized\n")
    await bot.change_presence(status=discord.Status.online, activity=discord.Streaming(name="!verify to get started", url="https://nopixel.mja00.dev/auth"))

#Shutdown bot - rarely used with new cog system
@bot.command()
@commands.has_any_role('Owner', 'Discord MANAGER')
async def shutdown(ctx):
    await ctx.channel.send("Shutting down main process.")
    await bot.logout()

#Load cog command
@bot.command()
@commands.has_any_role('Owner', 'Discord MANAGER')
async def load(ctx, extension):
    try:
        bot.load_extension(cogs_dir + "." + extension)
        await ctx.channel.send(f"{extension} loaded.")
    except commands.ExtensionAlreadyLoaded:
        await ctx.channel.send(f"The extension {extension} is already loaded.")
    except commands.ExtensionNotLoaded:
        bot.load_extension(cogs_dir + "." + extension)
    except commands.ExtensionNotFound:
        await ctx.channel.send(f"The extension {extension} was not found.")
    except commands.ExtensionFailed as error:
        await ctx.channel.send("{} cannot be loaded. [{}]".format(extension, error))
#Unload cog command
@bot.command()
@commands.has_any_role('Owner', 'Discord MANAGER')
async def unload(ctx, extension):
    try:
        bot.unload_extension(cogs_dir + "." + extension)
        await ctx.channel.send(f"{extension} unloaded.")
    except commands.ExtensionNotFound:
        await ctx.channel.send(f"The extension {extension} was not found.")
    except commands.ExtensionFailed as error:
        await ctx.channel.send("{} cannot be unloaded. [{}]".format(extension, error))
#Reload cog
@bot.command()
@commands.has_any_role('Owner', 'Discord MANAGER')
async def reload(ctx, extension):
    try:
        bot.reload_extension(cogs_dir + "." + extension)
        await ctx.channel.send(f"{extension} reloaded.")
    except commands.ExtensionAlreadyLoaded:
        await ctx.channel.send(f"The extension {extension} is already loaded.")
    except commands.ExtensionNotLoaded:
        bot.load_extension(cogs_dir + "." + extension)
    except commands.ExtensionNotFound:
        await ctx.channel.send(f"The extension {extension} was not found.")
    except commands.ExtensionFailed as error:
        await ctx.channel.send("{} cannot be reloaded. [{}]".format(extension, error))

#Handle command errors
@bot.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, 'on_error'):
        return
    ignored = (commands.CommandNotFound, commands.UserInputError)

    error = getattr(error, 'original', error)

    if isinstance(error, ignored):
        return

    elif isinstance(error, commands.DisabledCommand):
        return await ctx.send(f'{ctx.command} has been disabled.')
    elif isinstance(error, commands.NotOwner):
        return await ctx.send(f'This command can only be ran by Discord MANAGERs.')
    elif isinstance(error, commands.MissingAnyRole):
        return await ctx.send(error)
    elif isinstance(error, commands.CommandOnCooldown):
        return await ctx.send(f'{ctx.command} is on cooldown.')
    elif isinstance(error, commands.NoPrivateMessage):
        try:
            return await ctx.author.send(f'{ctx.command} cannot be used in DMs')
        except discord.DiscordException:
            pass
    elif isinstance(error, commands.BadArgument):
        if ctx.command.qualified_name == 'tag list':
            return await ctx.send("I could not find that member. Please try again")
    print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

#Mark a command as complete once completed
@bot.event
async def on_command_completion(ctx):
    try:
        if isinstance(ctx.channel, discord.DMChannel):
            pass
        else:
            await ctx.message.add_reaction(u"\u2705")
            await asyncio.sleep(5)
            await ctx.message.clear_reactions()
    except RuntimeError:
        pass

# Load all extensions automatically before starting bot
for extension in initHandlers:
    try:
        bot.load_extension(cogs_dir + "." + extension)
        print(f"{extension} loaded.")
    except commands.ExtensionAlreadyLoaded:
        print(f"The extension {extension} is already loaded.")
    except commands.ExtensionNotLoaded:
        bot.load_extension(cogs_dir + "." + extension)
    except commands.ExtensionNotFound:
        print(f"The extension {extension} was not found.")
    except commands.ExtensionFailed as error:
        print("{} cannot be loaded. [{}]".format(extension, error))

#Log all chat messages
@bot.event
async def on_message(message):
    author = message.author
    if author.bot is False:
        content = message.content
        channel = message.channel
        time = dt.now()
        try:
            print(Fore.CYAN + f"#{channel} | {author}:{content}")
            filename = time.strftime("%Y-%m-%d")
            with open(os.path.join("logs/chat", filename), "a") as logs:
                logs.write("\n"+ time.strftime("%Y-%m-%d %H:%M:%S") +f" || {author}:{content}")
            await bot.process_commands(message)
        except discord.DiscordException:
            print("Error in processing message contents.")
            await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    userid = member.id
    if channel is not None:
        print(f"{member.name} has joined the server.")
        await channel.send(f"Welcome to the NoPixel Moderator Discord <@{userid}>. Authenticate yourself here: https://nopixel.mja00.dev/auth and then run !update in <#579450156039012385>")

bot.run(token)