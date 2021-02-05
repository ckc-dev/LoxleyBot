"""
Main bot file.
"""

# Import required modules.
import logging
import os

import discord
from discord.ext import commands

import functions
import settings

# Make sure bot token was provided.
if not settings.BOT_TOKEN:
    raise ValueError("'BOT_TOKEN' environment variable was not provided.")

# Set up logging.
LOGGER = logging.getLogger('discord')
HANDLER = logging.FileHandler(
    filename=settings.BOT_LOG_FILENAME,
    encoding='utf-8',
    mode='w')
HANDLER.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(HANDLER)

# If database file does not exist, create it.
cursor = settings.DATABASE_CONNECTION.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
database_has_tables = cursor.fetchall()
cursor.close()
if not database_has_tables:
    functions.create_database()

# Initialize a Bot instance.
BOT = commands.Bot(command_prefix=settings.BOT_PREFIX)
BOT.activity = discord.Game(settings.BOT_ACTIVITY)


@BOT.event
async def on_ready():
    """
    Runs once the bot is finished logging in and setting things up.
    """

    print("Hello, world!")


@BOT.event
async def on_message(message):
    """
    Runs every time a message is received.

    Args:
        message (discord.Message): Received message.
    """

    # If message was sent by the bot, just return.
    if message.author == BOT.user:
        return

    # First, try processing message as a command.
    await BOT.process_commands(message)

    # If message matches some form of "Marco", play Marco Polo.
    if functions.REGEX_MARCO.match(message.content):
        await message.channel.send(functions.marco_polo(message.content))


@BOT.event
async def on_command_error(ctx, error):
    """
    Runs every time an error occurs while trying to run a command.

    Args:
        ctx (discord.ext.commands.context.Context): Context passed to function.
        error (discord.ext.commands.CommandError): Base exception for all command related errors.
    """

    # Warn for missing permissions.
    if isinstance(error, commands.MissingPermissions):
        await ctx.channel.send(f"Sorry {ctx.message.author.mention}, you don't have the permissions required to use this command.")

# Load all cogs.
for file in os.listdir("cogs"):
    if file.endswith(".py"):
        BOT.load_extension(f"cogs.{file[:-3]}")

# Run bot.
BOT.run(settings.BOT_TOKEN)
