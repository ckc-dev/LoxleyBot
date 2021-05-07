"""Main bot file."""

import os

import discord
from discord.ext import commands
from discord.utils import find

import functions
import regexes
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
    if message.author == BOT.user:
        return

    await BOT.process_commands(message)

    if regexes.MARCO.fullmatch(message.content):
        await message.channel.send(functions.marco_polo(message.content))

    if BOT.user in message.mentions:
        await message.channel.send(
            functions.get_localized_object(
                message.guild.id, "MENTION_HELP").format(
                    functions.database_guild_prefix_get(BOT, message)))


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
        await ctx.send(functions.get_localized_object(
            ctx.guild.id, "MISSING_PERMISSIONS").format(
                ctx.message.author.mention))


@BOT.event
async def on_guild_join(guild):
    """
    Will run every time the bot joins a guild.

    Args:
        guild (discord.Guild): Guild bot has joined.
    """
    functions.database_guild_initialize(guild.id)

    NAMES = settings.COMMON_GENERAL_TEXT_CHANNEL_NAMES
    general = find(lambda c: any(name in c.name for name in NAMES),
                   guild.text_channels)

    if general and general.permissions_for(guild.me).send_messages:
        message = ""

        for locale in functions.get_available_locales():
            message += functions.get_localized_object(
                guild.id, "BOT_GUILD_JOIN", locale).format(
                    locale,
                    guild.name,
                    settings.BOT_DEFAULT_PREFIX,
                    settings.BOT_DEFAULT_PREFIX) + "\n"

        await general.send(message)


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
