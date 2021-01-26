"""
Main bot file.
"""

# Import required modules.
import logging
import os

import discord
import dotenv
from discord.ext import commands

import functions

# Make sure bot token was provided.
dotenv.load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("'BOT_TOKEN' environment variable was not provided.")

# Set up logging.
LOGGER = logging.getLogger('discord')
HANDLER = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')
HANDLER.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(HANDLER)

# Initialize a Bot instance.
BOT = commands.Bot(command_prefix='./')
BOT.activity = discord.Game("./help")

# Once the bot is finished logging in and setting things up:
@BOT.event
async def on_ready():
    print("Hello, world!")


# Every time a message is received:
@BOT.event
async def on_message(message):
    # If message was sent by the bot, just return.
    if message.author == BOT.user:
        return

    # First, try processing message as a command.
    await BOT.process_commands(message)

    # If message matches some form of "Marco", play Marco Polo.
    if functions.REGEX_MARCO.match(message.content):
        await message.channel.send(functions.marco_polo(message.content))


# When an error occurs while trying to run a command:
@BOT.event
async def on_command_error(ctx, error):
    # Warn for missing permissions.
    if isinstance(error, commands.MissingPermissions):
        await ctx.channel.send(f"Sorry {ctx.message.author.mention}, you don't have the permissions required to use this command.")


# Load all cogs.
for file in os.listdir("cogs"):
    if file.endswith(".py"):
        BOT.load_extension(f"cogs.{file[:-3]}")

# Run bot.
BOT.run(TOKEN)
