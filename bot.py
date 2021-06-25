"""Main bot file."""

import datetime
import os

import discord
from discord.ext import commands

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

    Only runs on channels bot has permission to access and read messages on.

    Args:
        message (discord.Message): Received message.
    """
    if message.author == BOT.user:
        return

    ctx = await BOT.get_context(message)

    # Check whether or not message invokes bot (i.e., it is a command).
    if ctx.valid:
        await BOT.process_commands(message)
        return

    if regexes.MARCO.fullmatch(message.content):
        await ctx.send(functions.marco_polo(message.content))
        return

    guild_prefix = functions.database_guild_prefix_get(BOT, message)

    if BOT.user in message.mentions:
        await ctx.send(functions.get_localized_object(
            message.guild.id, "MENTION_HELP").format(guild_prefix))
        return

    copypasta_channel = functions.database_copypasta_channel_get(ctx.guild.id)

    if copypasta_channel and message.channel.id == copypasta_channel:
        flag = "import" if message.attachments else "add"
        message.content = (
            f"{guild_prefix}copypasta --{flag} {message.content}")
        await BOT.process_commands(message)


@BOT.event
async def on_raw_message_delete(payload):
    """
    Will run every time a message is deleted, whether it is cached or not.

    Only runs on channels bot has permission to access and read messages on.

    Args:
        payload (discord.RawMessageDeleteEvent): Raw event payload data.
    """
    guild_id = payload.guild_id
    logging_channel = BOT.get_channel(
        functions.database_logging_channel_get(guild_id))

    if logging_channel:
        message = payload.cached_message
        id_ = payload.message_id
        date = discord.utils.snowflake_time(id_)
        strftime_format = functions.get_localized_object(guild_id, "STRFTIME")
        channel = BOT.get_channel(payload.channel_id)
        embed = discord.Embed(color=settings.EMBED_COLOR)

        if message:
            embed.set_thumbnail(url=message.author.avatar_url)
            embed.add_field(
                name=functions.get_localized_object(
                    guild_id, "LOGGING_MESSAGE_DELETED_FIELD_HEADER_NAME"),
                value=functions.get_localized_object(
                    guild_id,
                    "LOGGING_MESSAGE_DELETED_FIELD_HEADER_VALUE").format(
                        channel.mention, message.author.mention),
                inline=False)
            embed.add_field(
                name=functions.get_localized_object(
                    guild_id, "LOGGING_MESSAGE_DELETED_FIELD_CONTENT_NAME"),
                # `or None` is used just in case message was an embed and
                # therefore has no content. This prevents an exception from
                # being raised due to an embed field with an empty value.
                value=message.content or None,
                inline=False)
        else:
            embed.add_field(
                name=functions.get_localized_object(
                    guild_id, "LOGGING_MESSAGE_DELETED_FIELD_HEADER_NAME"),
                value=functions.get_localized_object(
                    guild_id,
                    "LOGGING_MESSAGE_DELETED_FIELD_HEADER_VALUE_NO_CACHE").format(
                        channel.mention),
                inline=False)

        embed.add_field(
            name=functions.get_localized_object(
                guild_id, "LOGGING_MESSAGE_DELETED_FIELD_CREATION_TIME_NAME"),
            value=date.strftime(strftime_format),
            inline=False)
        embed.add_field(
            name=functions.get_localized_object(
                guild_id, "LOGGING_MESSAGE_DELETED_FIELD_ID_NAME"),
            value=f"`{id_}`",
            inline=False)
        embed.set_footer(
            text=functions.get_localized_object(
                guild_id, "LOGGING_MESSAGE_DELETED_FOOTER").format(
                    datetime.datetime.utcnow().strftime(strftime_format)))

        await logging_channel.send(embed=embed)


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

    general = discord.utils.find(lambda c: any(
        name in c.name for name in settings.COMMON_GENERAL_TEXT_CHANNEL_NAMES),
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
