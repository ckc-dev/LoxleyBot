"""Contains cogs used for functions related to fun and entertainment."""

import re

import functions
import settings
from discord.ext import commands


class Entertainment(commands.Cog):
    """
    Entertainment cog.

    Contains functions related to fun and entertainment.
    """

    def __init__(self, bot):
        """
        Initialize cog.

        Args:
            bot (discord.ext.commands.Bot): Bot to use with cog.
        """
        self.bot = bot

    @commands.command()
    async def copypasta(self, ctx, *, arguments=None):
        """
        Manage and send copypastas.

        Args:
            ctx (discord.ext.commands.Context): Context passed to function.
            arguments (str, optional): Arguments passed to command.
                Defaults to None.
        """
        def format_copypasta(copypasta):
            """
            Return a string containing copypasta data formatted as a message.

            Args:
                copypasta (Tuple[int, str, str, int]): Tuple containing
                    copypasta ID, title, contents and count, respectively.

            Returns:
                str: Formatted copypasta.
            """
            return "{}: {} | **'{}'**\n{}".format(
                functions.get_localized_message(ctx.guild.id, "COPYPASTA_ID"),
                *copypasta)

        def format_copypasta_list(copypasta_list, emphasis=None):
            """
            Format a list of copypastas as one or more tables.

            Returns a list of strings formatted as tables,
            generated from a list of copypastas.

            Args:
                copypasta_list (List[Tuple[int, str, str, int]]): A list of
                    tuples containing copypasta ID, title, contents and count,
                    respectively.
                emphasis (str, optional): Snippet of text that should be
                    highlighted. If present, the function will try to keep
                    it in the center of contents column. Defaults to None.

            Returns:
                List[str]: List containing strings formatted as tables,
                in which are cells containing copypasta data.
            """
            CHARACTERS_PER_ROW = settings.COPYPASTA_LIST_CHARACTERS_PER_ROW
            HEADING_ID = functions.get_localized_message(
                ctx.guild.id, "COPYPASTA_ID")
            HEADING_TITLE = functions.get_localized_message(
                ctx.guild.id, "COPYPASTA_TITLE")
            HEADING_CONTENTS = functions.get_localized_message(
                ctx.guild.id, "COPYPASTA_CONTENTS")
            HEADING_COUNT = functions.get_localized_message(
                ctx.guild.id, "COPYPASTA_COUNT")
            SEPARATOR = "|"
            PADDING = "…"
            PADDING_LEN = len(PADDING)
            FORMAT = "{sep}{id}{sep}{title}{sep}{contents}{sep}{count}{sep}\n"

            # Initialize character length limits. These are constant and tables
            # will truncate data once a value surpass its limit. IDs and counts
            # have no limit, since they are identifiers. 5 is subtracted from
            # characters per row to account for the amount of separators used.
            # Title limit is set to a fourth of the maximum amount of
            # characters per row.
            LIMIT_LEN_LINE = CHARACTERS_PER_ROW - 5
            LIMIT_LEN_TITLE = CHARACTERS_PER_ROW // 4

            # Initialize character length max values. These are generated every
            # time a list of tables is created, based on the already defined
            # limits and values from the copypastas.
            max_len_id = max(len(HEADING_ID),
                             len(str(max(copypasta_list,
                                         key=lambda l: l[0])[0])))
            max_len_title = max(len(HEADING_TITLE),
                                min(LIMIT_LEN_TITLE, len(max(copypasta_list,
                                                             key=lambda l: len(l[1]))[1])))
            max_len_count = max(len(HEADING_COUNT),
                                len(str(max(copypasta_list,
                                            key=lambda l: l[3])[3])))
            max_len_contents = max(len(HEADING_CONTENTS),
                                   min(LIMIT_LEN_LINE
                                       - max_len_id
                                       - max_len_title
                                       - max_len_count, len(max(copypasta_list,
                                                                key=lambda l: len(l[2]))[2])))

            # Initialize first table by opening a Markdown code block.
            table_list = []
            table = "```"

            # Add heading sections to table.
            section_id = HEADING_ID.center(max_len_id)
            section_title = HEADING_TITLE.center(max_len_title)
            section_contents = HEADING_CONTENTS.center(max_len_contents)
            section_count = HEADING_COUNT.center(max_len_count)
            table += FORMAT.format(sep=SEPARATOR,
                                   id=section_id,
                                   title=section_title,
                                   contents=section_contents,
                                   count=section_count)

            for copypasta in copypasta_list:
                # Separate copypasta data into variables.
                id_, title, contents, count = copypasta

                # Initialize ID, title and count sections.
                section_id = str(id_).rjust(max_len_id)
                if len(title) <= max_len_title:
                    section_title = title.ljust(max_len_title)
                else:
                    section_title = (title[:max_len_title - PADDING_LEN]
                                     + PADDING)
                section_count = str(count).ljust(max_len_count)

                # If highlighted text is in the copypasta contents:
                # (upper() is used to do this case-insensitively).
                if emphasis and emphasis.upper() in contents.upper():
                    # Limit its length and get its starting index.
                    emphasis_len = len(emphasis)
                    if emphasis_len >= max_len_contents:
                        emphasis = emphasis[:max_len_contents]
                    emphasis_index = contents.upper().find(emphasis.upper())

                    # Get how many characters will remain after removing length
                    # of highlighted text from max length of this cell,
                    # then divide it into a pair for each side of the cell.
                    left_spaces, right_spaces = functions.divide_in_pairs(
                        max_len_contents - emphasis_len)

                    # Get strings to left and right of highlighted
                    # text in contents and their lengths.
                    left_string = contents[:emphasis_index]
                    right_string = contents[emphasis_index + emphasis_len:]
                    left_string_len = len(left_string)
                    right_string_len = len(right_string)

                    # Decide wether or not padding will be added to left and/or
                    # right of cell, checking if each side has enough spaces
                    # to accommodate its respective string.
                    padding_on_left = left_string_len > left_spaces
                    padding_on_right = right_string_len > right_spaces

                    # If there are more spaces than characters in the string on
                    # one side of the highlighted text, add those spaces to the
                    # opposite side, and remove them from this one.
                    if left_string_len < left_spaces:
                        unused_spaces = (left_spaces - left_string_len)
                        right_spaces += unused_spaces
                        left_spaces -= unused_spaces

                    if right_string_len < right_spaces:
                        unused_spaces = (right_spaces - right_string_len)
                        left_spaces += unused_spaces
                        right_spaces -= unused_spaces

                    # Initialize contents section and add padding if necessary.
                    section_contents = (left_string[left_string_len - left_spaces:]
                                        + contents[emphasis_index:emphasis_index + emphasis_len]
                                        + right_string[:right_spaces])
                    if padding_on_left:
                        section_contents = (
                            PADDING + section_contents[PADDING_LEN:])
                    if padding_on_right:
                        section_contents = section_contents[:len(section_contents)
                                                            - PADDING_LEN] + PADDING

                # If highlighted text is not in the copypasta contents:
                else:
                    # If the number of characters in copypasta contents is
                    # within its max length, don't do anything. If it's not,
                    # limit it to its max length and add padding.
                    if len(contents) <= max_len_contents:
                        section_contents = contents
                    else:
                        section_contents = contents[:max_len_contents -
                                                    PADDING_LEN] + PADDING

                # Justify cell and add this row to the table.
                section_contents = section_contents.ljust(max_len_contents)
                table += FORMAT.format(sep=SEPARATOR,
                                       id=section_id,
                                       title=section_title,
                                       contents=section_contents,
                                       count=section_count)

                # If there is no more space for another row in the table,
                # close this table, append it to list of tables,
                # and open a new table.
                # (3 is added to account for closing Markdown code block.)
                if len(table) + 3 + CHARACTERS_PER_ROW > settings.DISCORD_CHARACTER_LIMIT:
                    table += "```"
                    table_list.append(table)
                    table = "```"

                # If there is space, but this is already the last copypasta in
                # the list, close the table and add it to the list of tables.
                elif copypasta == copypasta_list[-1]:
                    table += "```"
                    table_list.append(table)

            return table_list

        # Initialize RegExes for each argument.
        REGEX_ID = re.compile(r"""
            ^               # Match line start.
            \s*             # Match between 0 and ∞ whitespace characters.
            (?:-i|--id)?    # Match either "-i" or "--id", either 0 or 1 times.
            \s*             # Match between 0 and ∞ whitespace characters.
            (?P<id>\d+)     # CAPTURE GROUP (id) | Match between 1 and ∞ digits.
            \s*             # Match between 0 and ∞ whitespace characters.
            $               # Match line end.""", flags=re.IGNORECASE | re.VERBOSE)

        REGEX_TITLE = re.compile(r"""
            ^               # Match line start.
            \s*             # Match between 0 and ∞ whitespace characters.
            (?:-t|--title)? # Match either "-t" or "--title", either 0 or 1 times.
            \s*             # Match between 0 and ∞ whitespace characters.
            (?P<title>.+)   # CAPTURE GROUP (title) | Match between 1 and ∞ characters.
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

        REGEX_LIST = re.compile(r"""
            ^                                           # Match line start.
            \s*                                         # Match between 0 and ∞ whitespace characters.
            (?:-l|--list)                               # Match either "-l" or "--list".
            \s*                                         # Match between 0 and ∞ whitespace characters.
            (-i|--id|-t|--title|-c|--contents|--count)? # CAPTURE GROUP (1 - value) Match one of "-i",
                                                        # "--id", "-t", "--title", "-c", "--contents",
                                                        # or "--count" either 1 or 0 times.
            \s*                                         # Match between 0 and ∞ whitespace characters.
            (-a|--ascending|-d|--descending)?           # CAPTURE GROUP (2 - arrangement) Match one of ["-a",
                                                        # "--ascending", "-d", "--descending"] either 0 or 1 times.
            \s*                                         # Match between 0 and ∞ whitespace characters.
            $                                           # Match line end.
            |                                           # OR (same as above but with parameters switched.)
            ^                                           # Match line start.
            \s*                                         # Match between 0 and ∞ whitespace characters.
            (?:-l|--list)                               # Match either "-l" or "--list".
            \s*                                         # Match between 0 and ∞ whitespace characters.
            (-a|--ascending|-d|--descending)?           # CAPTURE GROUP (3 - arrangement) Match one of ["-a",
                                                        # "--ascending", "-d", "--descending"] either 0 or 1 times.
            \s*                                         # Match between 0 and ∞ whitespace characters.
            (-i|--id|-t|--title|-c|--contents|--count)? # CAPTURE GROUP (4 - value) Match one of "-i",
                                                        # "--id", "-t", "--title", "-c", "--contents",
                                                        # or "--count" either 1 or 0 times.
            \s*                                         # Match between 0 and ∞ whitespace characters.
            $                                           # Match line end.""", flags=re.IGNORECASE | re.VERBOSE)

        # Send a random copypasta.
        if arguments is None:
            copypasta = functions.database_copypasta_get(ctx.guild.id)
            if not copypasta:
                await ctx.send(functions.get_localized_message(
                    ctx.guild.id, "COPYPASTA_NONE_FOUND").format(ctx.guild))
            else:
                await ctx.send(format_copypasta(copypasta))

        # Send a specific copypasta by ID.
        elif REGEX_ID.match(arguments):
            id_ = REGEX_ID.match(arguments).group("id")
            copypasta = functions.database_copypasta_get(ctx.guild.id, id_)
            if not copypasta:
                await ctx.send(functions.get_localized_message(
                    ctx.guild.id, "COPYPASTA_NONE_FOUND_ID").format(
                        id_, ctx.guild))
            else:
                await ctx.send(format_copypasta(copypasta))

        # Add a copypasta to the database.
        elif REGEX_ADD.match(arguments):
            title, contents = REGEX_ADD.match(arguments).groups()
            functions.database_copypasta_add(ctx.guild.id, title, contents)
            await ctx.send(functions.get_localized_message(
                ctx.guild.id, "COPYPASTA_ADD").format(title))

        # Delete a copypasta from the database.
        elif REGEX_DELETE.match(arguments):
            id_ = REGEX_DELETE.match(arguments).group("id")
            functions.database_copypasta_delete(ctx.guild.id, id_)
            await ctx.send(functions.get_localized_message(
                ctx.guild.id, "COPYPASTA_DELETE").format(id_))

        # Search for one or more copypastas.
        elif REGEX_SEARCH.match(arguments):
            query = REGEX_SEARCH.match(arguments).group("query")
            results = functions.database_copypasta_search(ctx.guild.id, query)
            if not results:
                await ctx.send(functions.get_localized_message(
                    ctx.guild.id, "COPYPASTA_NONE_FOUND_QUERY").format(
                        query, ctx.guild))
            else:
                if len(results) > 1:
                    for row in format_copypasta_list(results, query):
                        await ctx.send(row)
                else:
                    # Query the database instead of grabbing copypasta
                    # directly from list, so that the number of times
                    # it was sent is updated.
                    copypasta = functions.database_copypasta_get(ctx.guild.id,
                                                                 results[0][0])
                    await ctx.send(functions.get_localized_message(
                        ctx.guild.id, "COPYPASTA_ONE_FOUND_QUERY").format(
                            query))
                    await ctx.send(format_copypasta(copypasta))

        # List all available copypastas.
        elif REGEX_LIST.match(arguments):
            # Initialize dictionaries containing possible arrangements
            # and fields by which results will be ordered by.
            FIELDS = {
                "": "count",
                "-I": "id",
                "-T": "title",
                "-C": "contents",
                "--ID": "id",
                "--TITLE": "title",
                "--CONTENTS": "contents",
                "--COUNT": "count"
            }
            ARRANGEMENTS = {
                "": "DESC",
                "-A": "ASC",
                "-D": "DESC",
                "--ASCENDING": "ASC",
                "--DESCENDING": "DESC",
            }

            # Get arrangement and field arguments passed to the command.
            match = REGEX_LIST.match(arguments)
            field = ((match.group(1) or "")
                     + (match.group(4) or "")).upper()
            arrangement = ((match.group(2) or "")
                           + (match.group(3) or "")).upper()

            # Decide which field results will be ordered by,
            # and its arrangement.
            order_field = FIELDS[field]
            order_arrangement = (
                "ASC" if field and not arrangement else ARRANGEMENTS[arrangement])

            results = functions.database_copypasta_search(
                ctx.guild.id, field=order_field, arrangement=order_arrangement)

            if not results:
                await ctx.send(functions.get_localized_message(
                    ctx.guild.id, "COPYPASTA_NONE_FOUND").format(ctx.guild))
            else:
                for row in format_copypasta_list(results):
                    await ctx.send(row)

        # Send either a specific copypasta by title or a list
        # of copypastas containing user query in their title.
        elif REGEX_TITLE.match(arguments):
            title = REGEX_TITLE.match(arguments).group("title")
            results = functions.database_copypasta_search(
                ctx.guild.id, title, by_title=True)
            if not results:
                await ctx.send(functions.get_localized_message(
                    ctx.guild.id, "COPYPASTA_NONE_FOUND_TITLE").format(
                        title, ctx.guild))
            else:
                if len(results) > 1:
                    await ctx.send(functions.get_localized_message(
                        ctx.guild.id, "COPYPASTA_MULTIPLE_FOUND_TITLE").format(
                            len(results), title))
                    for row in format_copypasta_list(results):
                        await ctx.send(row)
                else:
                    # Query the database instead of grabbing copypasta
                    # directly from list, so that the number of times
                    # it was sent is updated.
                    copypasta = functions.database_copypasta_get(ctx.guild.id,
                                                                 results[0][0])
                    await ctx.send(format_copypasta(copypasta))


def setup(bot):
    """
    Bind cogs to the bot.

    Args:
        bot (discord.ext.commands.Bot): Bot to bind cogs to.
    """
    bot.add_cog(Entertainment(bot))
