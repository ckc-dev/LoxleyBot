"""Contains cogs used for useful, often small and simple functions."""

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
        await ctx.send(f"Pong! `{round(self.bot.latency * 1000)}ms`")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: str):
        """
        Delete an amount of messages from a channel.

        Args:
            ctx (discord.ext.commands.Context): Context passed to function.
            amount (str, optional): Amount of messages to delete.
                Either a number or "all".
        """
        if isinstance(amount, str) and amount.upper() == "ALL":
            limit = None
        else:
            try:
                # 1 is added to account for the message sent by the bot.
                limit = int(amount) + 1

            # If user does not specify a valid amount, ask for it.
            except (TypeError, ValueError):
                await ctx.channel.send("Please provide an amount of messages to delete, or use 'all' to purge the channel.")
                return

        async for message in ctx.channel.history(limit=limit):
            await message.delete()

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
        await ctx.channel.send("Please be patient, this might take some time.")

        count = await self.count_messages(ctx.channel, end_message_id)

        if not end_message_id:
            functions.database_message_count_set(ctx.channel.id,
                                                 ctx.channel.last_message_id,
                                                 count)

            MESSAGES = {
                1: "Seems like it's just getting started, welcome everyone!",
                500: "Keep it up!",
                1000: "Gaining traction!",
                5000: "That's a lot!",
                10000: "Whoa! That's A LOT!"
            }

            for threshold, string in MESSAGES.items():
                if count < threshold:
                    break
                message = string

            # 1 is added to account for the message sent by the bot.
            await ctx.channel.send(f"I've found {count + 1} messages in {ctx.channel.mention}. {message}")
        else:
            end_message = await ctx.channel.fetch_message(end_message_id)
            await end_message.reply(f"I've found {count + 1} messages up to this message.", mention_author=False)

    @commands.command()
    async def prefix(self, ctx, new_prefix: str):
        """
        Change the command prefix for a guild.

        Args:
            ctx (discord.ext.commands.Context): Context passed to function.
            new_prefix (str): Prefix to change to.
        """
        current = functions.database_guild_prefix_get(self.bot, ctx)
        functions.database_guild_prefix_set(ctx.guild.id, new_prefix)
        await ctx.send(f"Prefix changed from '{current}' to '{new_prefix}'!")

    @tasks.loop(hours=24)
    async def database_message_count_auto_update(self):
        """Update message count in database every 24 hours."""
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                count = await self.count_messages(channel)
                functions.database_message_count_set(channel.id,
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
