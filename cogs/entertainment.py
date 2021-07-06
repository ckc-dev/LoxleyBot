"""Contains cogs used for functions related to fun and entertainment."""

import discord
import functions
import regexes
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

        When sending a copypasta by its title, if more than one copypasta is
        found, a list containing those is sent instead.

        When searching for copypastas, if only one copypasta matches search
        query, it is sent instead.

        When listing copypastas, by default, results are sorted by usage count,
        in descending order. If a field is specified, but not an order, will
        use ascending order by default.

        Args:
            arguments (str, optional): Arguments passed to command.
                Defaults to None.

        Usage:
            copypasta
            copypasta [{-i|--id}] <copypasta ID>
            copypasta [{-t|--title}] <copypasta title>
            copypasta {-s|--search} <search query>
            copypasta {-a|--add} "<copypasta title>" "<copypasta content>"
            copypasta {-d|--delete} <copypasta ID>
            copypasta {-l|--list} [{-a|--ascending|-d|--descending}]
                                  [{-i|--id|-t|--title|-c|--content|--count}]

        Examples:
            copypasta:
                Send a random copypasta.
            copypasta 10:
                Send copypasta with ID 10.
            copypasta example:
                Send copypasta which contains "example" in its title.
            copypasta -s example query:
                Search for "example query" in copypastas title and content.
            copypasta -a "Title" "Contents":
                Add "Contents" as a copypasta titled "Title".
            copypasta -d 8:
                Delete copypasta with ID 8.
            copypasta -l:
                List all copypastas.
            copypasta -l -t -a:
                List all copypastas, sorted by title, in ascending order.
        """
        def format_copypasta(copypasta):
            """
            Return an embed generated from copypasta data.

            Args:
                copypasta (Tuple[int, str, str, int]): Tuple containing
                    copypasta ID, title, content and count, respectively.

            Returns:
                discord.Embed: Copypasta.
            """
            id_, title, content, count = copypasta

            embed = discord.Embed(
                title=title, description=content, color=settings.EMBED_COLOR)

            # 1 is added to `count` to account for the fact that the data is
            # queried before it is updated. So if a copypasta is sent for the
            # first time, it shows a count of "1" instead of "0", and so on.
            embed.set_footer(text="{}: {} | {}: {}".format(
                functions.get_localized_object(
                    ctx.guild.id, 'COPYPASTA_TABLE_HEADER_ID'),
                id_,
                functions.get_localized_object(
                    ctx.guild.id, 'COPYPASTA_TABLE_HEADER_COUNT'),
                count + 1))

            return embed

        def format_copypasta_list(copypasta_list, emphasis=None):
            """
            Format a list of copypastas as one or more tables.

            Returns a list of strings formatted as tables,
            generated from a list of copypastas.

            Args:
                copypasta_list (List[Tuple[int, str, str, int]]): A list of
                    tuples containing copypasta ID, title, content and count,
                    respectively.
                emphasis (str, optional): Snippet of text that should be
                    highlighted. If present, the function will try to keep
                    it in the center of content column. Defaults to None.

            Returns:
                List[str]: List containing strings formatted as tables,
                in which are cells containing copypasta data.
            """
            CHARACTERS_PER_ROW = settings.COPYPASTA_LIST_CHARACTERS_PER_ROW
            HEADING_ID = functions.get_localized_object(
                ctx.guild.id, "COPYPASTA_TABLE_HEADER_ID")
            HEADING_TITLE = functions.get_localized_object(
                ctx.guild.id, "COPYPASTA_TABLE_HEADER_TITLE")
            HEADING_CONTENT = functions.get_localized_object(
                ctx.guild.id, "COPYPASTA_TABLE_HEADER_CONTENT")
            HEADING_COUNT = functions.get_localized_object(
                ctx.guild.id, "COPYPASTA_TABLE_HEADER_COUNT")
            SEPARATOR = "|"
            PADDING = "…"
            PADDING_LEN = len(PADDING)
            FORMAT = "{sep}{id}{sep}{title}{sep}{content}{sep}{count}{sep}\n"

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

            # First, get the entry with the largest ID number from copypasta
            # list, then convert entry's ID field `[0]` to a string, as to get
            # not the ID number, but it's number of digits. Finally, get the
            # max amount of characters between the ID table heading and
            # largest ID value, and assign it as the max length for the ID
            # cells for this table. A very similar process is used for the
            # other fields as well.
            max_len_id = max(
                len(HEADING_ID),
                len(str(max(copypasta_list, key=lambda l: l[0])[0])))
            max_len_title = max(
                len(HEADING_TITLE),
                min(LIMIT_LEN_TITLE,
                    len(max(copypasta_list, key=lambda l: len(l[1]))[1])))
            max_len_count = max(
                len(HEADING_COUNT),
                len(str(max(copypasta_list, key=lambda l: l[3])[3])))
            max_len_content = max(
                len(HEADING_CONTENT),
                min((LIMIT_LEN_LINE
                     - max_len_id
                     - max_len_title
                     - max_len_count),
                    len(max(copypasta_list, key=lambda l: len(l[2]))[2])))

            # Initialize first table by opening a Markdown code block.
            table_list = []
            table = "```"

            # Add heading sections to table.
            section_id = HEADING_ID.center(max_len_id)
            section_title = HEADING_TITLE.center(max_len_title)
            section_content = HEADING_CONTENT.center(max_len_content)
            section_count = HEADING_COUNT.center(max_len_count)
            table += FORMAT.format(sep=SEPARATOR,
                                   id=section_id,
                                   title=section_title,
                                   content=section_content,
                                   count=section_count)

            for copypasta in copypasta_list:
                # Separate copypasta data into variables and remove newlines
                # from content.
                id_, title, content, count = copypasta
                content = content.replace("\n", "")

                # Initialize ID, title and count sections.
                section_id = str(id_).rjust(max_len_id)
                if len(title) <= max_len_title:
                    section_title = title.ljust(max_len_title)
                else:
                    section_title = (title[:max_len_title - PADDING_LEN]
                                     + PADDING)
                section_count = str(count).ljust(max_len_count)

                # If highlighted text is in the copypasta content:
                # `upper()` is used to do this case-insensitively.
                if emphasis and emphasis.upper() in content.upper():
                    # Limit its length and get its starting index.
                    emphasis_len = len(emphasis)
                    if emphasis_len >= max_len_content:
                        emphasis = emphasis[:max_len_content]
                    emphasis_index = content.upper().find(emphasis.upper())

                    # Get how many characters will remain after removing length
                    # of highlighted text from max length of this cell, then
                    # divide it into a pair for each side of the cell.
                    left_spaces, right_spaces = functions.divide_in_pairs(
                        max_len_content - emphasis_len)

                    # Get strings to left and right of highlighted text in
                    # content and their lengths.
                    left_string = content[:emphasis_index]
                    right_string = content[emphasis_index + emphasis_len:]
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

                    # Initialize content section and add padding if necessary.
                    section_content = (
                        left_string[left_string_len - left_spaces:]
                        + content[emphasis_index:emphasis_index + emphasis_len]
                        + right_string[:right_spaces])
                    if padding_on_left:
                        section_content = (
                            PADDING + section_content[PADDING_LEN:])
                    if padding_on_right:
                        section_content = section_content[:len(
                            section_content) - PADDING_LEN] + PADDING

                # If highlighted text is not in the copypasta content:
                else:
                    # If the number of characters in copypasta content is
                    # within its max length, don't do anything. If it's not,
                    # limit it to its max length and add padding.
                    if len(content) <= max_len_content:
                        section_content = content
                    else:
                        section_content = content[:max_len_content
                                                  - PADDING_LEN] + PADDING

                # Justify cell and add this row to the table.
                section_content = section_content.ljust(max_len_content)
                table += FORMAT.format(sep=SEPARATOR,
                                       id=section_id,
                                       title=section_title,
                                       content=section_content,
                                       count=section_count)

                # If there is no more space for another row in the table,
                # close this table, append it to list of tables,
                # and open a new table.
                # (3 is added to account for closing Markdown code block.)
                if (len(table) + CHARACTERS_PER_ROW + 3
                        > settings.DISCORD_CHARACTER_LIMIT):
                    table += "```"
                    table_list.append(table)
                    table = "```"

                # If there is space, but this is already the last copypasta in
                # the list, close the table and add it to the list of tables.
                elif copypasta == copypasta_list[-1]:
                    table += "```"
                    table_list.append(table)

            return table_list

        # Send a random copypasta.
        if arguments is None:
            copypasta = functions.database_copypasta_get(ctx.guild.id)

            if not copypasta:
                await ctx.send(functions.get_localized_object(
                    ctx.guild.id, "COPYPASTA_NONE_FOUND").format(
                        guild_name=ctx.guild))
            else:
                await ctx.send(embed=format_copypasta(copypasta))

        # Send a specific copypasta by ID.
        elif regexes.ID_OPTIONAL.fullmatch(arguments):
            id_ = regexes.ID_OPTIONAL.fullmatch(arguments).group("id")
            copypasta = functions.database_copypasta_get(ctx.guild.id, id_)

            if not copypasta:
                await ctx.send(functions.get_localized_object(
                    ctx.guild.id, "COPYPASTA_NONE_FOUND_ID").format(
                        copypasta_id=id_,
                        guild_name=ctx.guild))
            else:
                await ctx.send(embed=format_copypasta(copypasta))

        # Add a copypasta to the database.
        elif regexes.ADD_OPTIONAL_VALUE.fullmatch(arguments):
            message_reference = ctx.message.reference
            remaining_string = regexes.ADD_OPTIONAL_VALUE.fullmatch(
                arguments).group(1)
            title = None

            if not remaining_string and not message_reference:
                await ctx.send(functions.get_localized_object(
                    ctx.guild.id, "COPYPASTA_INVALID_USAGE").format(
                        prefix=functions.database_guild_prefix_get(
                            self.bot, ctx)))
                return

            if remaining_string:
                match = regexes.TITLE_AND_CONTENT.fullmatch(
                    remaining_string.strip())
                title = match.group("title")

                # `or ""` is used just in case group is empty. Otherwise,
                # a NoneType would be used as an operand, raising an error.
                content = (match.group("content") or ""
                           + match.group("content_2") or "")

                if message_reference:
                    title = content if not title else title
                    content = message_reference.resolved.content
            else:
                content = message_reference.resolved.content

            exists = functions.database_copypasta_search(
                ctx.guild.id, content, exact_match=True)

            if not exists:
                if not title:
                    title = regexes.FIRST_FEW_WORDS.match(content).group(1)

                if (len(content) > settings.DISCORD_EMBED_DESCRIPTION_LIMIT
                        or len(title) > settings.DISCORD_EMBED_TITLE_LIMIT):
                    await ctx.send(functions.get_localized_object(
                        ctx.guild.id, "COPYPASTA_ADD_CHARACTER_LIMIT"))
                    return

                functions.database_copypasta_add(ctx.guild.id, title, content)
                await ctx.send(functions.get_localized_object(
                    ctx.guild.id, "COPYPASTA_ADD").format(
                        copypasta_title=title))
            else:
                # Query the database instead of grabbing copypasta
                # directly if it exists, so that the number of times
                # it was sent is updated.
                copypasta = functions.database_copypasta_get(
                    ctx.guild.id, exists[0][0])

                await ctx.send(functions.get_localized_object(
                    ctx.guild.id, "COPYPASTA_ADD_ALREADY_EXISTS"))
                await ctx.send(embed=format_copypasta(copypasta))

        # Delete a copypasta from the database.
        elif regexes.DELETE.fullmatch(arguments):
            id_ = regexes.DELETE.fullmatch(arguments).group("id")

            functions.database_copypasta_delete(ctx.guild.id, id_)
            await ctx.send(functions.get_localized_object(
                ctx.guild.id, "COPYPASTA_DELETE").format(copypasta_id=id_))

        # Search for one or more copypastas.
        elif regexes.SEARCH.fullmatch(arguments):
            query = regexes.SEARCH.fullmatch(arguments).group("query")
            results = functions.database_copypasta_search(ctx.guild.id, query)

            if not results:
                await ctx.send(functions.get_localized_object(
                    ctx.guild.id, "COPYPASTA_NONE_FOUND_QUERY").format(
                        query=query,
                        guild_name=ctx.guild))
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
                    await ctx.send(functions.get_localized_object(
                        ctx.guild.id, "COPYPASTA_ONE_FOUND_QUERY").format(
                            query=query))
                    await ctx.send(embed=format_copypasta(copypasta))

        # List all available copypastas.
        elif regexes.LIST_INDEPENDENT.match(arguments):
            # Initialize dictionaries containing possible arrangements
            # and fields by which results will be ordered by.
            FIELDS = {
                "": "count",
                "-I": "id",
                "-T": "title",
                "-C": "content",
                "--ID": "id",
                "--TITLE": "title",
                "--CONTENT": "content",
                "--COUNT": "count"
            }
            ARRANGEMENTS = {
                "": "DESC",
                "-A": "ASC",
                "-D": "DESC",
                "--ASCENDING": "ASC",
                "--DESCENDING": "DESC",
            }

            # Decide field and arrangement which results will be ordered by.
            field = ""
            arrangement = ""

            if regexes.COPYPASTA_LIST_DATABASE_FIELDS.search(arguments):
                field = regexes.COPYPASTA_LIST_DATABASE_FIELDS.search(
                    arguments).group("field").upper()

            if regexes.COPYPASTA_LIST_ARRANGEMENT.search(arguments):
                arrangement = regexes.COPYPASTA_LIST_ARRANGEMENT.search(
                    arguments).group("arrangement").upper()

            order_field = FIELDS[field]
            order_arrangement = (
                "ASC" if field and not arrangement else ARRANGEMENTS[arrangement])

            results = functions.database_copypasta_search(
                ctx.guild.id, field=order_field, arrangement=order_arrangement)

            if not results:
                await ctx.send(functions.get_localized_object(
                    ctx.guild.id, "COPYPASTA_NONE_FOUND").format(
                        guild_name=ctx.guild))
            else:
                for row in format_copypasta_list(results):
                    await ctx.send(row)

        # Set a channel where all messsages will be saved as copypastas.
        elif regexes.SET_CHANNEL_OPTIONAL_VALUE.fullmatch(arguments):
            if regexes.NONE_INDEPENDENT.search(arguments):
                functions.database_copypasta_channel_set(ctx.guild.id, None)

                await ctx.send(functions.get_localized_object(
                    ctx.guild.id, "COPYPASTA_SET_CHANNEL_NONE"))
                return

            channel_name = regexes.SET_CHANNEL_OPTIONAL_VALUE.fullmatch(
                arguments).group("channel") or ctx.channel.name

            try:
                channel = await commands.TextChannelConverter().convert(
                    ctx, channel_name)

                functions.database_copypasta_channel_set(
                    ctx.guild.id, channel.id)
                await ctx.send(functions.get_localized_object(
                    ctx.guild.id, "COPYPASTA_SET_CHANNEL").format(
                        channel_name=channel.mention))
            except commands.ChannelNotFound:
                await ctx.send(functions.get_localized_object(
                    ctx.guild.id, "SET_CHANNEL_NOT_FOUND").format(
                        channel_name=channel_name,
                        guild_name=ctx.guild))

        # Export copypastas to a JSON file.
        elif regexes.EXPORT_INDEPENDENT.fullmatch(arguments):
            await ctx.send(functions.get_localized_object(
                ctx.guild.id, "BE_PATIENT"))

            buffers = functions.copypasta_export_json(ctx.guild.id)

            for i, buffer in enumerate(buffers, start=1):
                name = f"export{'_' + str(i) if len(buffers) > 1 else ''}.json"
                await ctx.send(file=discord.File(buffer, name))

        # Import copypastas from a JSON file.
        elif (regexes.IMPORT_INDEPENDENT_VERBOSE.match(arguments)
              and ctx.message.attachments):
            await ctx.send(functions.get_localized_object(
                ctx.guild.id, "BE_PATIENT"))

            attachment = ctx.message.attachments[0]
            data = await attachment.read()
            results = functions.copypasta_import_json(data, ctx.guild.id)

            if not results:
                await ctx.send(functions.get_localized_object(
                    ctx.guild.id, "COPYPASTA_IMPORT_INVALID_FILE"))
                return

            parsed, imported, ignored, invalid = results
            parsed_count = len(parsed)

            if not parsed:
                await ctx.send(functions.get_localized_object(
                    ctx.guild.id, "COPYPASTA_IMPORT_NONE_PARSED"))
                return

            if imported:
                await ctx.send(functions.get_localized_object(
                    ctx.guild.id, "COPYPASTA_IMPORT_IMPORTED").format(
                        imported_copypasta_count=(
                            f"({len(imported)}/{parsed_count})")))

            if ignored:
                await ctx.send(functions.get_localized_object(
                    ctx.guild.id, "COPYPASTA_IMPORT_IGNORED").format(
                        ignored_copypasta_count=(
                            f"({len(ignored)}/{parsed_count})")))

            if invalid:
                await ctx.send(functions.get_localized_object(
                    ctx.guild.id, "COPYPASTA_IMPORT_INVALID").format(
                        invalid_copypasta_count=(
                            f"({len(invalid)}/{parsed_count})")))

                for i in invalid:
                    # 6 is removed from Discord's character limit when limiting
                    # string length to account for Markdown code block used.
                    await ctx.send("```{}```".format(
                        str(i)[:settings.DISCORD_CHARACTER_LIMIT - 6]))

        # Send either a specific copypasta by title or a list
        # of copypastas containing user query in their title.
        elif regexes.TITLE_OPTIONAL.fullmatch(arguments):
            title = regexes.TITLE_OPTIONAL.fullmatch(arguments).group("title")
            results = functions.database_copypasta_search(
                ctx.guild.id, title, by_title=True)
            if not results:
                await ctx.send(functions.get_localized_object(
                    ctx.guild.id, "COPYPASTA_NONE_FOUND_TITLE").format(
                        query=title,
                        guild_name=ctx.guild))
            else:
                if len(results) > 1:
                    await ctx.send(functions.get_localized_object(
                        ctx.guild.id, "COPYPASTA_MULTIPLE_FOUND_TITLE").format(
                            copypasta_count=len(results),
                            query=title))
                    for row in format_copypasta_list(results):
                        await ctx.send(row)
                else:
                    # Query the database instead of grabbing copypasta
                    # directly from list, so that the number of times
                    # it was sent is updated.
                    copypasta = functions.database_copypasta_get(
                        ctx.guild.id, results[0][0])
                    await ctx.send(embed=format_copypasta(copypasta))


def setup(bot):
    """
    Bind cogs to the bot.

    Args:
        bot (discord.ext.commands.Bot): Bot to bind cogs to.
    """
    bot.add_cog(Entertainment(bot))
