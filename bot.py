"""Main bot file."""

import os

import discord
from discord.ext import commands

import functions
import settings

if not settings.BOT_TOKEN:
    raise ValueError("'BOT_TOKEN' environment variable was not provided.")

if not functions.database_exists():
    functions.database_create()

BOT = commands.Bot(command_prefix=functions.database_guild_prefix_get)
BOT.activity = discord.Game(settings.BOT_ACTIVITY)


@BOT.event
async def on_message(message):
    """
    Will run every time a message is received.

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

    # If message mentions bot, send a help message.
    if BOT.user in message.mentions:
        await message.channel.send(f"Hello! Use {functions.database_guild_prefix_get(BOT, message)}help to get more information on what I can do. Did you know I can play Marco Polo?")


@BOT.event
async def on_command_error(ctx, error):
    """
    Will run every time an error occurs while trying to run a command.

    Args:
        ctx (discord.ext.commands.Context): Context passed to function.
        error (discord.ext.commands.CommandError): Base exception for all
        command related errors.
    """
    if isinstance(error, commands.MissingPermissions):
        await ctx.channel.send(f"""Sorry {ctx.message.author.mention}, you don't have the permissions required to use this command.""")


@BOT.event
async def on_guild_join(guild):
    """
    Will run every time the bot joins a guild.

    Args:
        guild (discord.Guild): Guild bot has joined.
    """
    functions.database_guild_prefix_set(guild.id, settings.BOT_DEFAULT_PREFIX)


@BOT.event
async def on_guild_remove(guild):
    """
    Will run every time the bot leaves a guild.

    Args:
        guild (discord.Guild): Guild bot has left.
    """
    functions.database_guild_purge(guild.id)

for file in os.listdir("cogs"):
    if file.endswith(".py"):
        BOT.load_extension(f"cogs.{file[:-3]}")

BOT.run(settings.BOT_TOKEN)
