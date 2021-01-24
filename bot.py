"""
Main bot file.
"""

# Import required modules.
import logging
import os

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

# Run bot.
BOT.run(TOKEN)
