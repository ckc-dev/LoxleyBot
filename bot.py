"""
Main bot file.
"""

# Import required modules.
import asyncio
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


# Get bot latency.
@BOT.command()
async def ping(ctx):
    await ctx.send(f"Pong! `{round(BOT.latency * 1000)}ms`")


# Delete channel messages.
@BOT.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount=None):
    # If user does not specify an amount, ask for it.
    if not amount:
        await ctx.channel.send("Please provide an amount of messages to delete, or use 'all' to purge the channel.")

    # Delete all messages.
    elif amount.upper() == "ALL":
        # Initialize empty counter.
        count = 0

        # Warn user that this might be a slow operation.
        await ctx.channel.send("Please be patient, this might take some time...")

        # Count all messages in channel.
        async for _ in ctx.channel.history(limit=None):
            count += 1

        # Pause for a few seconds while user reads the message.
        await asyncio.sleep(5)

        # 1 is added to account for the message used to run the command.
        await ctx.channel.purge(limit=count + 1)

    # Delete a specified amount of messages.
    else:
        # 1 is added to account for the message used to run the command.
        await ctx.channel.purge(limit=int(amount) + 1)


# If user does not have permission to manage messages, send an error message.
@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.channel.send(f"Sorry {ctx.message.author.mention}, you don't have the permissions required to use this command.")


# Count channel messages.
@BOT.command()
async def count(ctx):
    # Initialize empty counter.
    count = 0

    # Count all channel messages.
    async for _ in ctx.channel.history(limit=None):
        count += 1

    # Initialize empty message string and dictionary
    # containing thresholds and messages as key-value pairs.
    message = ""
    messages = {
        1: "Seems like it's just getting started, welcome everyone!",
        500: "Keep it up!",
        1000: "Gaining traction!",
        5000: "That's a lot!",
        10000: "Whoa! That's A LOT!"
    }

    # Select a message to send based on total number of messages sent to channel.
    for threshold, string in messages.items():
        if count < threshold:
            break
        message = string

    # Send message with results.
    await ctx.channel.send(f"I've found {count + 1} messages in {ctx.channel.mention}. {message}")


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
