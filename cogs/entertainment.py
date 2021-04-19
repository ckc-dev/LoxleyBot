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
            bot (discord.ext.commands.Bot): Bot to use with cog.
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
            "./copypasta [-s|--search] <query>"
                Searches for a copypasta by title or contents.
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

        def copypasta_list(copypastas, query=None):
            """
            Returns a string formatted as a table from a list of copypastas.

            Args:
                copypastas (List[Tuple[int, str, str, int]]): A list of tuples containing copypasta data.
                query (str, optional): What user is searching for in copypasta title or contents. Defaults to None.

            Returns:
                str: String containing a list of copypastas, formatted as a table.
            """

            # If list is empty, either no copypasta matches user query or no copypasta belongs to guild.
            if not copypastas:
                if query:
                    return f"No copypasta matching the query \"{query}\" was found in \"{ctx.guild}\"."
                return f"No copypasta was found in \"{ctx.guild}\"."

            def divide_in_pairs(n):
                """
                Divides a number into a tuple containing a pair of whole numbers.
                E.g.: divide_in_pairs(80) returns (40, 40).
                      divide_in_pairs(79) returns (39, 40).

                Args:
                    n (int): Number to divide.

                Returns:
                    Tuple[int, int]: Resulting pair of numbers.
                """

                return (n // 2, n // 2) if n % 2 == 0 else (n // 2, n // 2 + 1)

            # Initialize main string by opening a Markdown code block.
            string = "```"

            # Initialize table headings, separator and padding.
            HEADING_ID = "ID"
            HEADING_TITLE = "TITLE"
            HEADING_CONTENTS = "CONTENTS"
            HEADING_COUNT = "COUNT"
            SEPARATOR = "|"
            PADDING = "…"

            # Initialize character length limits.
            # These are constant and tables will truncate data once a value surpass its limit.
            # IDs have no limit, since they are unique identifiers.
            # 5 is subtracted from line limit to account for the amount of separators used.
            LIMIT_LEN_LINE = 80 - 5
            LIMIT_LEN_TITLE = 16

            # Initialize character length max values.
            # These are generated every time a table is created,
            # based on the already defined limits and values from the copypasta.
            max_len_id = max(len(HEADING_ID),
                             len(str(max(copypastas, key=lambda l: l[0])[0])))
            max_len_title = max(len(HEADING_TITLE),
                                min(LIMIT_LEN_TITLE, len(max(copypastas, key=lambda l: len(l[1]))[1])))
            max_len_count = max(len(HEADING_COUNT),
                                len(str(max(copypastas, key=lambda l: l[3])[3])))
            max_len_contents = max(len(HEADING_CONTENTS),
                                   min(LIMIT_LEN_LINE
                                       - max_len_id
                                       - max_len_title
                                       - max_len_count, len(max(copypastas, key=lambda l: len(l[2]))[2])))

            # Initialize heading sections and add them to main string.
            section_id = HEADING_ID.center(max_len_id)
            section_title = HEADING_TITLE.center(max_len_title)
            section_contents = HEADING_CONTENTS.center(max_len_contents)
            section_count = HEADING_COUNT.center(max_len_count)
            string += f"{SEPARATOR}{section_id}{SEPARATOR}{section_title}{SEPARATOR}{section_contents}{SEPARATOR}{section_count}{SEPARATOR}\n"

            # For each row in table (or copypasta in list):
            for copypasta in copypastas:
                # Initialize copypasta data.
                id, title, contents, count = copypasta

                # Initialize ID, title and count sections.
                section_id = str(id).rjust(max_len_id)
                if len(title) <= max_len_title:
                    section_title = title.ljust(max_len_title)
                else:
                    section_title = title[:max_len_title
                                          - len(PADDING)] + PADDING
                section_count = str(count).ljust(max_len_count)

                # If user query is in the copypasta contents:
                if query in contents:
                    # Limit query length.
                    if len(query) >= max_len_contents:
                        query = query[:max_len_contents]

                    # Get index at which user query starts in contents.
                    query_start_index = contents.find(query)

                    # Check how many characters will remain after removing length of query from max length.
                    remaining_characters = max_len_contents - len(query)
                    left_remaining_characters, right_remaining_characters = divide_in_pairs(
                        remaining_characters)

                    # Get characters to left and right of query.
                    characters_to_left_of_query = contents[:query_start_index]
                    characters_to_right_of_query = contents[query_start_index
                                                            + len(query):]

                    # By default, add padding to both sides of table cell (copypasta contents).
                    padding_on_left, padding_on_right = True, True

                    # If there are more "open spaces" than characters to left of query:
                    if len(characters_to_left_of_query) <= left_remaining_characters:
                        # Add those "spaces" to the ones on the right and remove them from here.
                        unused_spaces = (left_remaining_characters
                                         - len(characters_to_left_of_query))
                        right_remaining_characters += unused_spaces
                        left_remaining_characters -= unused_spaces

                        # Disable padding on the left, since this cell starts with the first character on `contents`.
                        padding_on_left = False

                    # If there are more "open spaces" than characters to left of query:
                    if len(characters_to_right_of_query) <= right_remaining_characters:
                        # Add those "spaces" to the ones on the left and remove them from here.
                        unused_spaces = (right_remaining_characters
                                         - len(characters_to_right_of_query))
                        left_remaining_characters += unused_spaces
                        right_remaining_characters -= unused_spaces

                        # Disable padding on the right, since this cell ends with the last character on `contents`.
                        padding_on_right = False

                    # Initialize contents section.
                    section_contents = (characters_to_left_of_query[len(characters_to_left_of_query) - left_remaining_characters:]
                                        + query
                                        + characters_to_right_of_query[:right_remaining_characters])

                    # Add padding to cell, if required.
                    if padding_on_left:
                        section_contents = (PADDING
                                            + section_contents[len(PADDING):])
                    if padding_on_right:
                        section_contents = section_contents[:len(section_contents)
                                                            - len(PADDING)] + PADDING

                # If user query is not in the copypasta contents:
                else:
                    # If the number of characters in `content` is within max length, don't do anything.
                    if len(contents) <= max_len_contents:
                        section_contents = contents

                    # Otherwise, limit it to max length and add some padding.
                    else:
                        section_contents = contents[:max_len_contents -
                                                    len(PADDING)] + PADDING

                # Justify cell to the left.
                section_contents = section_contents.ljust(max_len_contents)

                # Add this row (or copypasta) to main string.
                string += f"{SEPARATOR}{section_id}{SEPARATOR}{section_title}{SEPARATOR}{section_contents}{SEPARATOR}{section_count}{SEPARATOR}\n"

            # Close Markdown code block and return main string.
            string += "```"
            return string

        # Initialize RegExes for each argument.
        REGEX_ID = re.compile(r"""
            ^               # Match line start.
            \s*             # Match between 0 and ∞ whitespace characters.
            (?:-i|--id)?    # Match either "-i" or "--id", either 0 or 1 times.
            \s*             # Match between 0 and ∞ whitespace characters.
            (?P<id>\d+)     # CAPTURE GROUP (id) | Match between 1 and ∞ digits.
            \s*             # Match between 0 and ∞ whitespace characters.
            $               # Match line end.""", flags=re.IGNORECASE | re.VERBOSE)

        REGEX_ADD = re.compile(r"""
            ^                   # Match line start.
            \s*                 # Match between 0 and ∞ whitespace characters.
            (?:-a|--add)        # Match either "-a" or "--add".
            \s*                 # Match between 0 and ∞ whitespace characters.
            [\"']               # Match either '"' or "'".
            (?P<title>.+)       # CAPTURE GROUP (title) | Match any character between 1 and ∞ times.
            [\"']               # Match either '"' or "'".
            \s*                 # Match between 0 and ∞ whitespace characters.
            [\"']               # Match either '"' or "'".
            (?P<contents>.+)    # CAPTURE GROUP (contents) | Match any character between 1 and ∞ times.
            [\"']               # Match either '"' or "'".
            \s*                 # Match between 0 and ∞ whitespace characters.
            $                   # Match line end.""", flags=re.IGNORECASE | re.VERBOSE)

        REGEX_DELETE = re.compile(r"""
            ^               # Match line start.
            \s*             # Match between 0 and ∞ whitespace characters.
            (?:-d|--delete) # Match either "-d" or "--delete".
            \s*             # Match between 0 and ∞ whitespace characters.
            (?P<id>\d+)     # CAPTURE GROUP (id) | Match between 1 and ∞ digits.
            \s*             # Match between 0 and ∞ whitespace characters.
            $               # Match line end.""", flags=re.IGNORECASE | re.VERBOSE)

        REGEX_SEARCH = re.compile(r"""
            ^               # Match line start.
            \s*             # Match between 0 and ∞ whitespace characters.
            (?:-s|--search) # Match either "-s" or "--search".
            \s*             # Match between 0 and ∞ whitespace characters.
            (?P<query>.+)   # CAPTURE GROUP (query) | Match any character between 1 and ∞ times.
            \s*             # Match between 0 and ∞ whitespace characters.
            $               # Match line end.""", flags=re.IGNORECASE | re.VERBOSE)

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

        # If argument used to search for a copypasta was provided:
        elif REGEX_SEARCH.match(arguments):
            # Get search results from database.
            query = REGEX_SEARCH.match(arguments).group("query")
            results = functions.database_copypasta_search(ctx.guild.id, query)

            # Send results formatted as a table.
            await ctx.send(copypasta_list(results, query))

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
