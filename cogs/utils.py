"""
Contains cogs used for useful, often small and simple functions.
"""

# Import required modules.
import functions
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
    async def purge(self, ctx, amount: str = None):
        """
        Deletes an amount of messages from a channel.

        Args:
            ctx (discord.ext.commands.context.Context): Context passed to function.
            amount (str, optional): Amount of messages to delete.
                                    Either a number or "all". Defaults to None.
        """

        # Delete all messages.
        if isinstance(amount, str) and amount.upper() == "ALL":
            limit = None

        # Delete a specified amount of messages.
        else:
            try:
                # 1 is added to account for the message used to run the command.
                limit = int(amount) + 1

            # If user does not specify a valid amount, ask for it.
            except (TypeError, ValueError):
                await ctx.channel.send("Please provide an amount of messages to delete, or use 'all' to purge the channel.")
                return None

        # Delete messages.
        async for message in ctx.channel.history(limit=limit):
            await message.delete()

    @commands.command()
    async def count(self, ctx, end_message_id: int = None):
        """
        Counts number of messages sent to a channel up to a specified message ID.
        If ID is not provided, counts total number of messages sent to channel.

        Args:
            ctx (discord.ext.commands.context.Context): Context passed to function.
            end_message_id (int, optional): ID of a message to stop counting when reached. Defaults to None.
        """

        # Initialize empty counter.
        count = 0

        # Warn user that this might be a slow operation.
        await ctx.channel.send("Please be patient, this might take some time...")

        # If user does not specify when to stop counting:
        if not end_message_id:
            # Get last message information from database.
            query = functions.query_database(ctx.guild.id, ctx.channel.id)

            # If it exists, update counter and id of the message to stop counting when found.
            if query:
                end_message_id = query[1]
                count = query[0]

        # Count messages until end message is reached.
        async for message in ctx.channel.history(limit=None):
            count += 1
            if message.id == end_message_id:
                break

        # Update database.
        functions.update_database(
            ctx.guild.id, ctx.channel.id, ctx.channel.last_message_id, count)

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

        # Send message with results. 1 is added to account for the message used to run the command.
        await ctx.channel.send(f"I've found {count + 1} messages in {ctx.channel.mention}. {message}")


def setup(bot):
    """
    Binds the cog to the bot.

    Args:
        bot (discord.ext.commands.Bot): Bot to bind cog to.
    """

    bot.add_cog(Utils(bot))
