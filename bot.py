"""Main bot file."""

import datetime
import os

import discord
from discord.ext import commands

import functions
import regexes
import settings

if not functions.database_exists():
    functions.database_create()

BOT = commands.Bot(
    command_prefix=functions.database_guild_prefix_get,
    intents=discord.Intents.all())
BOT.activity = discord.Game(settings.BOT_ACTIVITY)


async def copypasta_channel_process_message(message):
    """
    Process messages sent to copypasta channel.

    Args:
        message (discord.Message): Message to process.
    """
    functions.database_copypasta_channel_last_saved_id_set(
        message.guild.id, message.id)

    guild_prefix = functions.database_guild_prefix_get(BOT, message)
    flag = "import" if message.attachments else "add"
    message.content = (f"{guild_prefix}copypasta --{flag} {message.content}")

    await BOT.process_commands(message)


@BOT.event
async def on_ready():
    """Will run once bot is done preparing data received from Discord."""
    # Save messages sent to copypasta channel while bot was offline.
    for guild in BOT.guilds:
        copypasta_channel = BOT.get_channel(
            functions.database_copypasta_channel_get(guild.id))

        if not copypasta_channel:
            continue

        last_saved_copypasta_id = (
            functions.database_copypasta_channel_last_saved_id_get(guild.id))
        try:
            last_saved_copypasta = await copypasta_channel.fetch_message(
                last_saved_copypasta_id)
            after = last_saved_copypasta.created_at
        except discord.errors.NotFound:
            after = None

        async for message in copypasta_channel.history(
                limit=None, after=after, oldest_first=True):

            if message.id == last_saved_copypasta_id:
                break

            if message.author == BOT.user:
                continue

            # Check whether or not message invokes bot (i.e.: it is a command).
            ctx = await BOT.get_context(message)
            if ctx.valid:
                continue

            await copypasta_channel_process_message(message)


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

    # Check whether or not message invokes bot (i.e.: it is a command).
    if ctx.valid:
        await BOT.process_commands(message)
        return

    if regexes.MARCO.fullmatch(message.content):
        await ctx.send(functions.marco_polo(message.content))
        return

    guild_prefix = functions.database_guild_prefix_get(BOT, message)

    if BOT.user in message.mentions:
        await ctx.send(functions.get_localized_object(
            message.guild.id, "MENTION_HELP").format(prefix=guild_prefix))
        return

    copypasta_channel = functions.database_copypasta_channel_get(ctx.guild.id)

    if copypasta_channel and message.channel.id == copypasta_channel:
        await copypasta_channel_process_message(message)


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
        message_id = payload.message_id
        creation_time = discord.utils.snowflake_time(message_id)
        guild_date_format = functions.get_localized_object(
            guild_id, "STRFTIME_DATE")
        guild_time_format = functions.get_localized_object(
            guild_id, "STRFTIME_TIME")
        guild_format = f"{guild_date_format} | {guild_time_format}"
        utc_time = datetime.datetime.utcnow()
        local_time = functions.utc_to_local(utc_time, guild_id)
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
                        channel_name=channel.mention,
                        message_author=message.author.mention),
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
                        channel_name=channel.mention),
                inline=False)

        embed.add_field(
            name=functions.get_localized_object(
                guild_id, "LOGGING_MESSAGE_DELETED_FIELD_CREATION_TIME_NAME"),
            value=functions.get_localized_object(
                guild_id,
                "LOGGING_MESSAGE_DELETED_FIELD_CREATION_TIME_VALUE").format(
                    local_time=functions.utc_to_local(
                        creation_time, guild_id).strftime(guild_format),
                    utc_time=creation_time.strftime(guild_format)),
            inline=False)
        embed.add_field(
            name=functions.get_localized_object(
                guild_id, "LOGGING_MESSAGE_DELETED_FIELD_ID_NAME"),
            value=f"`{message_id}`",
            inline=False)
        embed.set_footer(text=functions.get_localized_object(
            guild_id, "LOGGING_MESSAGE_DELETED_FOOTER").format(
                local_time=local_time.strftime(guild_format),
                utc_time=utc_time.strftime(guild_format)))

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
                member=ctx.message.author.mention))

    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send(functions.get_localized_object(
            ctx.guild.id, "BOT_MISSING_PERMISSIONS"))

    else:
        raise error

    await ctx.send(functions.get_localized_object(
        ctx.guild.id, "MISSING_PERMISSIONS_DETAILS").format(details=error))


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
            message = functions.get_localized_object(
                guild.id, "GUILD_JOIN", locale).format(
                    locale=locale,
                    guild_name=guild.name,
                    prefix=settings.GUILD_DEFAULT_PREFIX)

            await general.send(message)


@BOT.event
async def on_guild_remove(guild):
    """
    Will run every time the bot leaves a guild.

    Args:
        guild (discord.Guild): Guild bot has left.
    """
    functions.database_guild_purge(guild.id)


@BOT.event
async def on_member_remove(member):
    """
    Will run every time a member leaves a guild.

    Args:
        member (discord.Member): Member who left the guild.
    """
    functions.database_birthday_delete(member.guild.id, member.id)
    functions.database_copypasta_unban_user(member.guild.id, member.id)

for file in os.listdir("cogs"):
    if file.endswith(".py"):
        BOT.load_extension(f"cogs.{file[:-3]}")

BOT.run(settings.BOT_TOKEN)
