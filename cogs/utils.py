"""
Contains cogs used for useful, often small and simple functions.
"""

# Import required modules.
import asyncio

from discord.ext import commands


class Utils(commands.Cog):
    """
    Utils cog. Contains useful, often small and simple functions.
    """

    # Initialize cog.
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """
        Gets bot latency.

        Args:
            ctx (discord.ext.commands.context.Context): Context passed to function.
        """

        await ctx.send(f"Pong! `{round(self.bot.latency * 1000)}ms`")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount=None):
        """
        Deletes an amount of messages from a channel.

        Args:
            ctx (discord.ext.commands.context.Context): Context passed to function.
            amount (str, optional): Amount of messages to delete.
                                      Either a number or "all". Defaults to None.
        """

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

    @commands.command()
    async def count(self, ctx):
        """
        Counts number of messages sent to a channel.

        Args:
            ctx (discord.ext.commands.context.Context): Context passed to function.
        """

        # Initialize empty counter.
        count = 0

        # Warn user that this might be a slow operation.
        await ctx.channel.send("Please be patient, this might take some time...")

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


def setup(bot):
    """
    Binds the cog to the bot.

    Args:
        bot (discord.ext.commands.Bot): Bot to bind cog to.
    """

    bot.add_cog(Utils(bot))
