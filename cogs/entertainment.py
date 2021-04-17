"""
Contains cogs used for functions related to fun and entertainment.
"""

# Import required modules.
import re

import functions
from discord.ext import commands


class Entertainment(commands.Cog):
    """
    Entertainment cog. Contains functions related to fun and entertainment.
    """

    def __init__(self, bot):
        """
        Initializes cog.

        Args:
            bot (discord.ext.commands.Bot): Bot use with cog.
        """

        # Initialize bot.
        self.bot = bot

    @commands.command()
    async def copypasta(self, ctx, *, arguments=None):
        """
        Manages and sends copypastas.

        Args:
            ctx (discord.ext.commands.context.Context): Context passed to function.
            arguments (str, optional): Arguments passed to command. Defaults to None.

        Usage:
            "./copypasta"
                Sends a random copypasta.
            "./copypasta [-i|--id, optional] <id>"
                Sends a specific copypasta by ID.
            "./copypasta [-a|--add] '<title>' '<contents>'"
                Adds a copypasta to the database. Title and contents must be between single or double quotes.
            "./copypasta [-d|--delete] <id>"
                Deletes a copypasta from the database.
        """

        def copypasta_query(guild_id, copypasta_id=None):
            """
            Queries the database for a copypasta, returns either copypasta or error message.

            Args:
                guild_id (int): ID of guild to which copypasta belongs.
                copypasta_id (int, optional): ID of to-be-queried copypasta. Defaults to None.

            Returns:
                str: A string containing either the already formatted copypasta or an error message.
            """

            # Try to get a copypasta from the database.
            query = functions.database_copypasta_query(guild_id, copypasta_id)

            # If it does not exist:
            if not query:
                # Pick an error message based on whether or not the user specified a copypasta ID.
                if not copypasta_id:
                    message = f"No copypasta was found in \"{ctx.guild}\"."
                else:
                    message = f"No copypasta with ID {copypasta_id} was found in \"{ctx.guild}\"."

            # If it does exist, format copypasta data into a message.
            else:
                copypasta_id, title, contents = query
                message = f"**\"{title}\"** | ID: {copypasta_id}\n\n{contents}"
            return message

        # Initialize RegEx for each argument.
        REGEX_ID = re.compile(r"^\s*(?:(?:-i|--id)\s*)?(?P<id>\d+)\s*$")
        REGEX_ADD = re.compile(r"^\s*(?:-a|--add)\s*[\"'](?P<title>.+)[\"']\s*[\"'](?P<contents>.+)[\"']\s*$")
        REGEX_DELETE = re.compile(r"^\s*(?:(?:-d|--delete)\s*)(?P<id>\d+)\s*$")

        # If no argument was provided, send a random copypasta.
        if arguments is None:
            await ctx.send(copypasta_query(ctx.guild.id))

        # If a copypasta ID was provided, send this specific copypasta.
        elif REGEX_ID.match(arguments):
            copypasta_id = REGEX_ID.match(arguments).group("id")
            await ctx.send(copypasta_query(ctx.guild.id, copypasta_id))

        # If argument used to add a copypasta was provided:
        elif REGEX_ADD.match(arguments):
            # Get copypasta data from argument, add it to database and notify user.
            title, contents = REGEX_ADD.match(arguments).groups()
            functions.database_copypasta_add(ctx.guild.id, title, contents)
            await ctx.send(f"\"{title}\" added!")

        # If argument used to delete a copypasta was provided:
        elif REGEX_DELETE.match(arguments):
            # Get copypasta ID from argument, delete it from database and notify user.
            copypasta_id = REGEX_DELETE.match(arguments).group("id")
            functions.database_copypasta_delete(ctx.guild.id, copypasta_id)
            await ctx.send("Copypasta with ID {copypasta_id} deleted!")

        # If no valid argument was provided, send an error message.
        else:
            await ctx.send("Invalid argument.")


def setup(bot):
    """
    Binds cogs to the bot.

    Args:
        bot (discord.ext.commands.Bot): Bot to bind cog to.
    """

    bot.add_cog(Entertainment(bot))
