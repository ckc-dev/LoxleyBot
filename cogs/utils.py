"""Contains cogs used for useful, often small and simple functions."""

import re

import functions
from discord.ext import commands, tasks


class Utils(commands.Cog):
    """Utils cog. Contains useful, often small and simple functions."""

    def __init__(self, bot):
        """
        Initialize cog.

        Args:
            bot (discord.ext.commands.Bot): Bot to use with cog.
        """
        self.bot = bot
        self.database_message_count_auto_update.start()

    def cog_unload(self):
        """Will run when cog is unloaded."""
        self.database_message_count_auto_update.cancel()

    @commands.command()
    async def ping(self, ctx):
        """
        Get bot latency.

        Args:
            ctx (discord.ext.commands.Context): Context passed to function.
        """
        await ctx.send(functions.get_localized_message(
            ctx.guild.id, "PING").format(round(self.bot.latency * 1000)))

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, *, arguments=None):
        """
        Delete an amount of messages from a channel.

        Args:
            ctx (discord.ext.commands.Context): Context passed to function.
            arguments (str, optional): Arguments passed to command.
                Defaults to None.

        Usage:
            purge [{-l|--limit}] <limit>
            purge {-i|--id} <message ID>
            purge {-a|--all}

        Examples:
            purge 10:
                Delete the last 10 messages.
            purge -i 838498717459415081:
                Delete all messages up to message with ID "838498717459415081".
            purge -a:
                Delete all messages.
        """
        REGEX_LIMIT = re.compile(r"""
            ^               # Match line start.
            \s*             # Match between 0 and ∞ whitespace characters.
            (?:-l|--limit)? # Match either "-c" or "--count", either 0 or 1 times.
            \s*             # Match between 0 and ∞ whitespace characters.
            (?P<limit>\d+)  # CAPTURE GROUP (count) | Match between 1 and ∞ digits.
            \s*             # Match between 0 and ∞ whitespace characters.
            $               # Match line end.""", flags=re.IGNORECASE | re.VERBOSE)

        REGEX_ID = re.compile(r"""
            ^               # Match line start.
            \s*             # Match between 0 and ∞ whitespace characters.
            (?:-i|--id)     # Match either "-i" or "--id".
            \s*             # Match between 0 and ∞ whitespace characters.
            (?P<id>\d+)     # CAPTURE GROUP (id) | Match between 1 and ∞ digits.
            \s*             # Match between 0 and ∞ whitespace characters.
            $               # Match line end.""", flags=re.IGNORECASE | re.VERBOSE)

        REGEX_ALL = re.compile(r"""
            ^               # Match line start.
            \s*             # Match between 0 and ∞ whitespace characters.
            (?:-a|--all)    # Match either "-a" or "--all".
            \s*             # Match between 0 and ∞ whitespace characters.
            $               # Match line end.""", flags=re.IGNORECASE | re.VERBOSE)

        if not arguments:
            await ctx.send(functions.get_localized_message(
                ctx.guild.id, "PURGE_INVALID_ARGUMENT"))
            return

        limit = None
        end_message_id = None
        if REGEX_LIMIT.match(arguments):
            # 1 is added to account for the message sent by the bot.
            limit = int(REGEX_LIMIT.match(arguments).group("limit")) + 1
        elif REGEX_ID.match(arguments):
            end_message_id = int(REGEX_ID.match(arguments).group("id"))
        elif not REGEX_ALL.match(arguments):
            await ctx.send(functions.get_localized_message(
                ctx.guild.id, "PURGE_INVALID_ARGUMENT"))
            return

        async for message in ctx.channel.history(limit=limit):
            await message.delete()
            if message.id == end_message_id:
                break

    async def count_messages(self, channel, end_message_id: int = None):
        """
        Count number of messages sent to a channel up to a specified message.

        Args:
            channel (discord.TextChannel): Text channel which will have its
                number of messages counted.
            end_message_id (int, optional): ID of a message to stop counting
                when reached. If not provided, will count total number of
                messages sent to channel. Defaults to None.

        Returns:
            int: Message count for this channel.
        """
        count = 0
        count_all = False

        if not end_message_id:
            count_all = True
            current_count = functions.database_message_count_get(channel.id)
            if current_count:
                end_message_id = current_count[1]

        async for message in channel.history(limit=None):
            if message.id == end_message_id:
                if count_all:
                    count += current_count[0]
                break
            count += 1

        return count

    @commands.command()
    async def count(self, ctx, end_message_id: int = None):
        """
        Count number of messages sent to a channel up to a specified message.

        Args:
            ctx (discord.ext.commands.Context): Context passed to function.
            end_message_id (int, optional): ID of a message to stop counting
                when reached. If not provided, will count total number of
                messages sent to channel. Defaults to None.
        """
        await ctx.send(functions.get_localized_message(
            ctx.guild.id, "COUNT_BE_PATIENT"))

        count = await self.count_messages(ctx.channel, end_message_id)

        if not end_message_id:
            functions.database_message_count_set(ctx.guild.id,
                                                 ctx.channel.id,
                                                 ctx.channel.last_message_id,
                                                 count)

            MESSAGES = {
                1: functions.get_localized_message(
                    ctx.guild.id, "COUNT_THRESHOLD_1"),
                500: functions.get_localized_message(
                    ctx.guild.id, "COUNT_THRESHOLD_500"),
                1000: functions.get_localized_message(
                    ctx.guild.id, "COUNT_THRESHOLD_1000"),
                5000: functions.get_localized_message(
                    ctx.guild.id, "COUNT_THRESHOLD_5000"),
                10000: functions.get_localized_message(
                    ctx.guild.id, "COUNT_THRESHOLD_10000")
            }

            for threshold, string in MESSAGES.items():
                if count < threshold:
                    break
                message = string

            # 1 is added to account for the message sent by the bot.
            await ctx.send(functions.get_localized_message(
                ctx.guild.id, "COUNT_FOUND_MESSAGE").format(
                    count + 1, ctx.channel.mention, message))
        else:
            end_message = await ctx.channel.fetch_message(end_message_id)
            await end_message.reply(
                functions.get_localized_message(
                    ctx.guild.id, "COUNT_FOUND_REPLY").format(count + 1),
                mention_author=False)

    @commands.command()
    async def prefix(self, ctx, new: str):
        """
        Change the guild prefix.

        Args:
            ctx (discord.ext.commands.Context): Context passed to function.
            new (str): Prefix to change to.
        """
        current = functions.database_guild_prefix_get(self.bot, ctx)
        functions.database_guild_prefix_set(ctx.guild.id, new)
        await ctx.send(functions.get_localized_message(
            ctx.guild.id, "PREFIX_CHANGE").format(current, new))

    @commands.command()
    async def locale(self, ctx, new: str):
        """
        Change guild locale.

        Args:
            ctx (discord.ext.commands.Context): Context passed to function.
            new (str): Locale to change to.
        """
        current = functions.database_guild_locale_get(ctx.guild.id)
        available = functions.get_available_locales()
        if new.upper() in [i.upper() for i in available]:
            new = available[[i.upper() for i in available].index(new.upper())]
            functions.database_guild_locale_set(ctx.guild.id, new)
            await ctx.send(functions.get_localized_message(
                ctx.guild.id, "LOCALE_CHANGE").format(current, new))
        else:
            await ctx.send(functions.get_localized_message(
                ctx.guild.id, "LOCALE_UNAVAILABLE").format(available))

    @tasks.loop(hours=24)
    async def database_message_count_auto_update(self):
        """Update message count in database every 24 hours."""
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).read_messages:
                    count = await self.count_messages(channel)
                    functions.database_message_count_set(guild.id,
                                                         channel.id,
                                                         channel.last_message_id,
                                                         count)

    @database_message_count_auto_update.before_loop
    async def wait_until_ready(self):
        """Wait until bot is ready before updating database."""
        await self.bot.wait_until_ready()


def setup(bot):
    """
    Bind cogs to the bot.

    Args:
        bot (discord.ext.commands.Bot): Bot to bind cogs to.
    """
    bot.add_cog(Utils(bot))
