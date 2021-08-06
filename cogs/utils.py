"""Contains cogs used for useful, often small and simple functions."""

import datetime

import discord
import functions
import regexes
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
        self.check_for_birthdays.start()

    def cog_unload(self):
        """Will run when cog is unloaded."""
        self.database_message_count_auto_update.cancel()
        self.check_for_birthdays.cancel()

    @commands.command()
    async def ping(self, ctx):
        """
        Get bot latency.

        Usage:
            ping

        Examples:
            ping:
                Get bot latency.
        """
        await ctx.send(functions.get_localized_object(
            ctx.guild.id, "PING").format(
                latency=round(self.bot.latency * 1000)))

    @commands.command()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, *, arguments=None):
        """
        Delete an amount of messages from a channel.

        Args:
            arguments (str): Arguments passed to command. Defaults to None.

        Usage:
            purge [{-l|--limit}] <limit>
            purge {-i|--id} <message ID>
            purge {-a|--all}
            purge (referencing/replying a message)

        Examples:
            purge 10:
                Delete the last 10 messages.
            purge -i 838498717459415081:
                Delete all messages up to message with ID "838498717459415081".
            purge -a:
                Delete all messages.
            purge (referencing/replying a message):
                Delete all messages up to referenced message.
        """
        message_reference = ctx.message.reference

        if not arguments and not message_reference:
            await ctx.send(functions.get_localized_object(
                ctx.guild.id, "PURGE_INVALID_USAGE").format(flag_all="-a"))
            return

        limit = None
        end_message_id = None

        if message_reference:
            end_message_id = message_reference.message_id
        elif regexes.LIMIT_OPTIONAL.fullmatch(arguments):
            # 1 is added to account for the message used to run the command.
            limit = int(
                regexes.LIMIT_OPTIONAL.fullmatch(arguments).group("limit")) + 1
        elif regexes.ID.fullmatch(arguments):
            end_message_id = int(regexes.ID.fullmatch(arguments).group("id"))
        elif not regexes.ALL_INDEPENDENT.fullmatch(arguments):
            await ctx.send(functions.get_localized_object(
                ctx.guild.id, "PURGE_INVALID_USAGE"))
            return

        async for message in ctx.channel.history(limit=limit):
            await message.delete()
            if message.id == end_message_id:
                break

    async def count_messages(self, channel, end_message_id=None):
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
    async def count(self, ctx, *, arguments=None):
        """
        Count number of messages sent to a channel up to a specified message.

        If no end message ID is specified, all messages will be counted.

        Args:
            arguments (str, optional): Arguments passed to command.
                Defaults to None.

        Usage:
            count [{-a|--all}]
            count [{-i|--id}] <message ID>
            count (referencing/replying a message)

        Examples:
            count:
                Count all messages.
            count 838498717459415081:
                Count all messages up to message with ID "838498717459415081".
            count (referencing/replying a message):
                Count all messages up to referenced message.
        """
        message_reference = ctx.message.reference

        if message_reference:
            end_message_id = message_reference.message_id
        elif not arguments or regexes.ALL_INDEPENDENT.fullmatch(arguments):
            end_message_id = None
        elif regexes.ID_OPTIONAL.fullmatch(arguments):
            end_message_id = int(
                regexes.ID_OPTIONAL.fullmatch(arguments).group("id"))
        else:
            await ctx.send(functions.get_localized_object(
                ctx.guild.id, "COUNT_INVALID_USAGE"))
            return

        await ctx.send(functions.get_localized_object(
            ctx.guild.id, "BE_PATIENT"))

        count = await self.count_messages(ctx.channel, end_message_id)

        if end_message_id:
            try:
                end_message = await ctx.channel.fetch_message(end_message_id)

                # 1 is added to account for the message sent by the bot.
                await end_message.reply(
                    functions.get_localized_object(
                        ctx.guild.id, "COUNT_FOUND_REPLY").format(
                            message_count=count + 1),
                    mention_author=False)
                return
            # Catch exception just in case message is deleted before the bot
            # has the chance to reply to it.
            except discord.NotFound:
                await ctx.send(functions.get_localized_object(
                    ctx.guild.id, "COUNT_REPLY_DELETED"))
                return

        functions.database_message_count_set(
            ctx.guild.id, ctx.channel.id, ctx.channel.last_message_id, count)

        message_dict = functions.get_localized_object(
            ctx.guild.id, "COUNT_THRESHOLD_DICT")

        for string, threshold in message_dict.items():
            if count < threshold:
                break
            threshold_message = string

        # 1 is added to account for the message sent by the bot.
        await ctx.send(functions.get_localized_object(
            ctx.guild.id, "COUNT_FOUND_MESSAGE").format(
                message_count=count + 1,
                channel_name=ctx.channel.mention,
                threshold_message=threshold_message))

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx, new=None):
        """
        Change the guild prefix.

        Args:
            new (str): Prefix to change to. Defaults to None.

        Usage:
            prefix <new prefix>

        Examples:
            prefix >>:
                Change prefix to ">>".
            prefix ./:
                Change prefix to "./".
        """
        current = functions.database_guild_prefix_get(self.bot, ctx)

        if not new:
            await ctx.send(functions.get_localized_object(
                ctx.guild.id, "PREFIX_REQUIRE"))
        else:
            functions.database_guild_prefix_set(ctx.guild.id, new)
            await ctx.send(functions.get_localized_object(
                ctx.guild.id, "PREFIX_CHANGE").format(
                    current_prefix=current,
                    new_prefix=new))

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def locale(self, ctx, new=None):
        """
        Change guild locale.

        Args:
            new (str): Locale to change to. Defaults to None.

        Usage:
            locale <new locale>

        Examples:
            locale en-US:
                Change locale to "en-US".
            locale pt-BR:
                Change locale to "pt-BR".
        """
        current = functions.database_guild_locale_get(ctx.guild.id)
        available = functions.get_available_locales()

        if not new or not new.upper() in [i.upper() for i in available]:
            await ctx.send(functions.get_localized_object(
                ctx.guild.id, "LOCALE_INVALID_USAGE").format(
                    available_locales=", ".join(f"`{i}`" for i in available)))
        else:
            new = available[[i.upper() for i in available].index(new.upper())]

            functions.database_guild_locale_set(ctx.guild.id, new)
            await ctx.send(functions.get_localized_object(
                ctx.guild.id, "LOCALE_CHANGE").format(
                    current_locale=current,
                    new_locale=new))

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def timezone(self, ctx, new=None):
        """
        Change guild timezone.

        Is is required to use the following format: {+|-}HH:MM.
            E.g.: -03:00 or +12:30.

        Args:
            new (str): Timezone to change to. Defaults to None.

        Usage:
            timezone <new timezone>

        Examples:
            timezone -03:00:
                Change timezone to -03:00.
            locale +12:30:
                Change timezone to +12:30".
        """
        if not new or not regexes.TIMEZONE.fullmatch(new):
            await ctx.send(functions.get_localized_object(
                ctx.guild.id, "TIMEZONE_INVALID_USAGE"))
            return

        current = functions.database_guild_timezone_get(ctx.guild.id)

        functions.database_guild_timezone_set(ctx.guild.id, new)

        await ctx.send(functions.get_localized_object(
            ctx.guild.id, "TIMEZONE_CHANGE").format(
                current_timezone=current,
                new_timezone=new))

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def logging(self, ctx, *, arguments=None):
        """
        Set a text channel for logging deleted messages.

        Args:
            arguments (str, optional): Arguments passed to command.
                Defaults to None.

        Usage:
            logging {-sc|--set-channel} [<channel>]

        Examples:
            logging -sc:
                Set logging channel to channel on which command was used.
            logging -sc #log:
                Set logging channel to #log.
        """
        if not arguments or not regexes.SET_CHANNEL_OPTIONAL_VALUE.fullmatch(
                arguments):
            await ctx.send(functions.get_localized_object(
                ctx.guild.id, "LOGGING_INVALID_USAGE"))
            return

        if regexes.NONE_INDEPENDENT.search(arguments):
            functions.database_logging_channel_set(ctx.guild.id, None)
            await ctx.send(functions.get_localized_object(
                ctx.guild.id, "LOGGING_SET_CHANNEL_NONE"))
            return

        channel_name = regexes.SET_CHANNEL_OPTIONAL_VALUE.fullmatch(
            arguments).group("channel") or ctx.channel.name

        try:
            channel = await commands.TextChannelConverter().convert(
                ctx, channel_name)

            functions.database_logging_channel_set(ctx.guild.id, channel.id)
            await ctx.send(functions.get_localized_object(
                ctx.guild.id, "LOGGING_SET_CHANNEL").format(
                    channel_name=channel.mention))
        except commands.ChannelNotFound:
            await ctx.send(functions.get_localized_object(
                ctx.guild.id, "SET_CHANNEL_NOT_FOUND").format(
                    channel_name=channel_name, guild_name=ctx.guild))

    @commands.command()
    async def birthday(self, ctx, *, arguments=None):
        """
        Manage birthdays.

        The format used in the date when running command depends on the
            guild locale. To check which format to use, simply run this
            command without any argument and read the help message.

        When saving birthday information, albeit required due to
            localization issues, birth year is not saved.

        Args:
            arguments (str, optional): Arguments passed to command.
                Defaults to None.

        Usage:
            birthday {-sc|--set-channel} [<channel>]
            birthday {-n|--none}
            birthday <date>

        Examples:
            birthday -sc:
                Set birthday announcement channel to channel on which
                    command was used.
            birthday -sc #announcements:
                Set birthday announcement channel to #announcements.
            birthday -n:
                Delete birthday information.
            birthday 30/01/2000:
                Save birthday information as January 30.
        """
        if not arguments:
            await ctx.send(functions.get_localized_object(
                ctx.guild.id, "BIRTHDAY_INVALID_USAGE"))
            return
        if regexes.SET_CHANNEL_OPTIONAL_VALUE.fullmatch(arguments):
            if not ctx.channel.permissions_for(ctx.author).manage_guild:
                permissions = discord.Permissions(manage_guild=True)
                functions.raise_missing_permissions(permissions)

            if regexes.NONE_INDEPENDENT.search(arguments):
                functions.database_birthday_channel_set(ctx.guild.id, None)
                await ctx.send(functions.get_localized_object(
                    ctx.guild.id, "BIRTHDAY_SET_CHANNEL_NONE"))
                return

            channel_name = regexes.SET_CHANNEL_OPTIONAL_VALUE.fullmatch(
                arguments).group("channel") or ctx.channel.name

            try:
                channel = await commands.TextChannelConverter().convert(
                    ctx, channel_name)

                functions.database_birthday_channel_set(
                    ctx.guild.id, channel.id)
                await ctx.send(functions.get_localized_object(
                    ctx.guild.id, "BIRTHDAY_SET_CHANNEL").format(
                        channel_name=channel.mention))
            except commands.ChannelNotFound:
                await ctx.send(functions.get_localized_object(
                    ctx.guild.id, "SET_CHANNEL_NOT_FOUND").format(
                        channel_name=channel_name,
                        guild_name=ctx.guild))
        elif regexes.NONE_INDEPENDENT.fullmatch(arguments):
            functions.database_birthday_delete(ctx.guild.id, ctx.author.id)
            await ctx.send(functions.get_localized_object(
                ctx.guild.id, "BIRTHDAY_DELETED"))
        elif regexes.DIGITS.search(arguments):
            date_string = "".join(regexes.DIGITS.findall(arguments))
            date_format = functions.get_localized_object(
                ctx.guild.id, "STRFTIME_DATE")
            cleaned_date_format = "".join(
                regexes.DATETIME_FORMAT_CODE.findall(date_format))
            try:
                date = datetime.datetime.strptime(
                    date_string, cleaned_date_format)

                functions.database_birthday_add(
                    ctx.guild.id, ctx.author.id, date.month, date.day)
                await ctx.send(functions.get_localized_object(
                    ctx.guild.id, "BIRTHDAY_ADDED"))
            except ValueError:
                await ctx.send(functions.get_localized_object(
                    ctx.guild.id, "BIRTHDAY_INVALID_USAGE"))
        else:
            await ctx.send(functions.get_localized_object(
                ctx.guild.id, "BIRTHDAY_INVALID_USAGE"))

    @tasks.loop(hours=24)
    async def database_message_count_auto_update(self):
        """Update message count in database every 24 hours."""
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).read_messages:
                    count = await self.count_messages(channel)
                    functions.database_message_count_set(
                        guild.id, channel.id, channel.last_message_id, count)

    @tasks.loop(hours=24)
    async def check_for_birthdays(self):
        """Check each guild for birthdays, every 24 hours."""
        for guild in self.bot.guilds:
            birthday_channel = guild.get_channel(
                functions.database_birthday_channel_get(guild.id))
            if not birthday_channel:
                continue
            utc_time = datetime.datetime.utcnow()
            local_time = functions.utc_to_local(utc_time, guild.id)
            birthday_list = functions.database_birthday_list_get(
                guild.id, local_time.month, local_time.day)
            for birthday in birthday_list:
                try:
                    member = guild.get_member(birthday[0])
                    await birthday_channel.send(functions.get_localized_object(
                        guild.id, "BIRTHDAY_MESSAGE").format(
                            user=member.mention))
                except commands.MemberNotFound:
                    pass

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
