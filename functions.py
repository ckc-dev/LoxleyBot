"""
Contains functions used in other parts of the bot.
"""

# Import required modules.
import random
import re

import settings

REGEX_MARCO = re.compile(r"""
    ^                           # Match line start.
    \s*                         # Match between 0 and ∞ whitespace characters.
    (?P<m>m+)                   # CAPTURE GROUP ("m" character) | Match between 1 and ∞ "m".
    (?P<a>a+)                   # CAPTURE GROUP ("a" character) | Match between 1 and ∞ "a".
    (?P<r>r+)                   # CAPTURE GROUP ("r" character) | Match between 1 and ∞ "r".
    (?P<c>c+)                   # CAPTURE GROUP ("c" character) | Match between 1 and ∞ "c".
    (?P<o>o+)                   # CAPTURE GROUP ("o" character) | Match between 1 and ∞ "o".
    (?P<punctuation>[.…?!\s]*)  # CAPTURE GROUP (punctuation) | Match between 0 and ∞ of ".",
                                # "…", "?", "!", or any whitespace character.
    $                           # Match line end.""", flags=re.IGNORECASE | re.VERBOSE)


def change_guild_prefix(guild_id, prefix):
    """
    Changes the saved prefix on the database for a guild.

    Args:
        guild_id (int): ID of guild which will have its prefix changed.
        prefix (str): What to change guild prefix to.
    """

    # Connect to the database and update guild prefix.
    CURSOR = settings.DATABASE_CONNECTION.cursor()
    CURSOR.execute("""
        UPDATE guild_prefixes
           SET prefix = ?
         WHERE guild_id = ?;""", (prefix, guild_id))

    # Commit changes and close connection to the database.
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


def get_guild_prefix(client, message):
    """
    Gets a guild prefix from the database.

    Args:
        client (discord.ext.commands.Bot): Client to which guild prefix will be queried.
        message (discord.Message): Message coming from guild which prefix will be queried.

    Returns:
        str: Guild prefix.
    """

    # Initialize guild ID.
    guild_id = message.guild.id

    # Connect to the database.
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    # Get the message count for this channel and last message ID from the database.
    results = CURSOR.execute("""
        SELECT prefix
          FROM guild_prefixes
         WHERE guild_id = ?;""", (guild_id, )).fetchone()

    # Close connection to the database and return results.
    CURSOR.close()
    return results[0]


def marco_polo(string):
    """
    Returns an answer to "Marco", "Marco!", "Marco..." or something along those lines.
    The answer is based on the user input plus random chances.

    Args:
        string (str): String containing user input.

    Returns:
        str: "Polo" answer.
    """

    def gen_char_amount(group):
        """
        Returns an amount of characters to output, based on user input.
        Args:
            group (str): A group of characters to get amount from. E.g.: "MmmM" or "aAA".

        Returns:
            int: Amount of characters to output.
        """

        # Get how many characters `group` has.
        i = len(group)

        # Randomly pick an amount of characters between `I - 2` and `I + 2`.
        return max(1, *random.choices(
            [i - 2, i - 1, i, i + 1, i + 2],
            weights=[.15, .35, 9, .35, .15]
        ))

    def gen_char_string(groups, sub):
        """
        Generates a string of characters, based on user input.

        Args:
            groups (List[str]): A list containing groups of characters to generate string from.
                                E.g.: ["mm"] or ["RrrRr", "c"].
            sub (str): String (character) to substitute groups of characters with. E.g.: "P" or "L".

        Returns:
            str: Generated string. E.g.: "Pp" or "LLLllL".
        """

        # Initialize empty string.
        s = ""

        # Get the chance any character has of being uppercase, by dividing the number
        # of uppercase characters by the total number of characters in all groups.
        uppercase_chance = sum(
            1 for c in "".join(groups) if c.isupper()) / len("".join(groups))

        # Do the following a number of times equal to the average number of characters in all groups:
        for _ in range(int(sum(gen_char_amount(group) for group in groups)/len(groups))):
            # Decide whether current character will be uppercase or not, and add it to string.
            s += "".join(random.choices(
                [sub.lower(), sub.upper()],
                weights=[1 - uppercase_chance, uppercase_chance]
            ))

        # Return generated string.
        return s

    def gen_punctuation_string(group):
        """
        Generates a string of punctuation, based on user input.

        Args:
            group (str): A group of punctuation characters to generate string from. E.g.: ".?!".

        Returns:
            str: Generated string. E.g.: "..." or "!?!?!?".
        """

        # Initialize empty string and dictionary.
        s = ""
        d = {}

        # For each unique character in group:
        for char in set([char for char in group]):
            # Populate dictionary with character and amount of times it appears.
            d[char] = group.count(char)

        # Do the following a number of times generated using the group:
        for _ in range(gen_char_amount(group)):
            # Pick random character based on how many times that character appears, and add it to string.
            s += "".join(random.choices([*d], weights=[*d.values()]))

        # Return generated string.
        return s

    # Match some form of "Marco" in user string.
    match = REGEX_MARCO.match(string)

    # Key-value pairs for what each character will be substituted with.
    character_dicts = [
        {"P": [match.group("m")]},
        {"O": [match.group("a")]},
        {"L": [match.group("r"), match.group("c")]},
        {"O": [match.group("o")]},
    ]

    # Initialize empty string.
    s = ""

    # For each character:
    for d in character_dicts:
        # Generate a character string and add it to main to-be-returned string.
        s += gen_char_string(*d.values(), *d)

    # If there's punctuation present, generate a punctuation
    # string and add it to main to-be-returned string.
    p = match.group("punctuation")
    if len(p) > 0:
        s += gen_punctuation_string(p)

    # Return string.
    return s


def database_create():
    """
    Creates a SQLite database.
    """

    # Connect to the database.
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    # Create tables and close connection to the database.
    CURSOR.execute("""
        CREATE TABLE message_counts(
                   guild_id INTEGER NOT NULL,
                 channel_id INTEGER NOT NULL,
            last_message_id INTEGER NOT NULL,
                      count INTEGER NOT NULL);""")
    CURSOR.execute("""
        CREATE TABLE copypastas(
                  id INTEGER NOT NULL,
            guild_id INTEGER NOT NULL,
               title TEXT NOT NULL,
            contents TEXT NOT NULL,
            count INTEGER DEFAULT 0);""")
    CURSOR.execute("""
        CREATE TABLE guild_prefixes(
            guild_id INTEGER NOT NULL,
              prefix TEXT NOT NULL);""")
    CURSOR.close()


def database_message_count_update(guild_id, channel_id, last_message_id, count):
    """
    Updates database with current message count for a channel.

    Args:
        guild_id (int): ID of this guild.
        channel_id (int): ID of this channel.
        last_message_id (int): ID of the last message sent to this channel.
        count (int): Message count for this channel.
    """

    # Connect to the database.
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    # Store query parameters in a tuple.
    params = (guild_id, channel_id)

    # Try to get the message count for this channel from the database.
    results = CURSOR.execute("""
        SELECT count
          FROM message_counts
         WHERE guild_id = ?
           AND channel_id = ?;""", params).fetchone()

    # If there are no records on the database for this channel:
    if not results:
        # Save last message ID and message count to the database.
        params = (*params, last_message_id, count)
        CURSOR.execute("""
            INSERT INTO message_counts(
                guild_id,
                channel_id,
                last_message_id,
                count
            )
            VALUES(?, ?, ?, ?);""", params)

    # If there is a record on the database for this channel:
    else:
        # Update last message ID and message count.
        params = (last_message_id, count, *params)
        CURSOR.execute("""
            UPDATE message_counts
               SET last_message_id = ?,
                   count = ?
             WHERE guild_id = ?
               AND channel_id = ?;""", params)

    # Commit changes and close connection to the database.
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


def database_message_count_query(guild_id, channel_id):
    """
    Queries database for the current message count for a channel.

    Args:
        guild_id (int): ID of this guild.
        channel_id (int): ID of this channel.

    Returns:
        Tuple[int, int]: A tuple containing the message count for this channel
                         and the ID of the last message sent to this channel, respectively.
    """

    # Connect to the database.
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    # Get the message count for this channel and last message ID from the database.
    results = CURSOR.execute("""
        SELECT count,
               last_message_id
          FROM message_counts
         WHERE guild_id = ?
           AND channel_id = ?;""", (guild_id, channel_id)).fetchone()

    # Close connection to the database and return results.
    CURSOR.close()
    return results


def database_copypasta_query(guild_id, copypasta_id=None):
    """
    Queries database for a copypasta.

    Args:
        guild_id (int): ID of guild to which copypasta belongs.
        copypasta_id (int, optional): ID of to-be-queried copypasta. Defaults to None.

    Returns:
        Tuple[int, str, str]: Tuple containing copypasta data.
    """

    # Connect to the database.
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    # Get either a random or specific copypasta from database,
    # based on whether or not the user specifies a copypasta ID.
    if not copypasta_id:
        results = CURSOR.execute("""
            SELECT id,
                   title,
                   contents
              FROM copypastas
             WHERE guild_id = ?
             ORDER BY RANDOM();""", (guild_id, )).fetchone()
    else:
        results = CURSOR.execute("""
            SELECT id,
                   title,
                   contents
              FROM copypastas
             WHERE guild_id = ?
               AND id = ?;""", (guild_id, copypasta_id)).fetchone()

    # Add 1 to number of times this copypasta was sent, if it exists.
    if results:
        CURSOR.execute("""
            UPDATE copypastas
               SET count = count + 1
             WHERE guild_id = ?
               AND id = ?;""", (guild_id, results[0]))

    # Commit changes, close connection to the database and return results.
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()
    return results


def database_copypasta_add(guild_id, title, contents):
    """
    Adds a copypasta to the database.

    Args:
        guild_id (int): ID of guild to which copypasta will belong.
        title (str): Title of the copypasta.
        contents (str): Contents of the copypasta.
    """

    # Connect to the database.
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    # Add copypasta to the database.
    CURSOR.execute("""
        INSERT INTO copypastas(
            id,
            guild_id,
            title,
            contents
        )
        VALUES(
            COALESCE(
                 (SELECT id
                    FROM copypastas
                   WHERE guild_id = ?
                ORDER BY id DESC
                   LIMIT 1) + 1,
                1
            ), ?, ?, ?
        );""", (guild_id, guild_id, title, contents))

    # Commit changes and close connection to the database.
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


def database_copypasta_delete(guild_id, copypasta_id):
    """
    Deletes a copypasta from the database.

    Args:
        guild_id (int): ID of guild to which copypasta belongs.
        copypasta_id (int): ID of to-be-deleted copypasta.
    """

    # Connect to the database.
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    # Delete copypasta from database.
    CURSOR.execute("""
        DELETE FROM copypastas
              WHERE guild_id = ?
                AND id = ?;""", (guild_id, copypasta_id))

    # Commit changes and close connection to the database.
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


def database_copypasta_search(guild_id, query=None, search_by_title=False, order_field="count", order_arrangement="DESC"):
    """
    Searches for one or more copypastas on the database.

    Args:
        guild_id (int): ID of guild to which copypastas belong.
        query (str, optional): What to search for in copypasta title or contents. Defaults to None.
                               If query is None, all copypastas that belong to this guild will be returned.
        search_by_title (bool, optional): Whether or not to search only by title. Defaults to False.
        order_field (str, optional): Which field results will be ordered by. Defaults to "count".
        order_arrangement (str, optional): Which arrangement results will follow. Defaults to "DESC".

    Returns:
        List[Tuple[int, str, str, int]]: A list of tuples containing copypasta data.
    """

    # Connect to the database.
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    # Initialize search parameters.
    params = {
        "guild_id": guild_id,
        "query": f"%{query or ''}%"
    }

    # Search for copypastas that contain query in either their title or contents.
    results = CURSOR.execute(f"""
          SELECT id,
                 title,
                 contents,
                 count
            FROM copypastas
           WHERE guild_id = :guild_id
             AND(title LIKE :query
            {'OR contents LIKE :query' if not search_by_title else ''})
        ORDER BY {order_field} {order_arrangement};""", params).fetchall()

    # Close connection to the database and return results.
    CURSOR.close()
    return results
