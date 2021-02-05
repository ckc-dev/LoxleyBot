"""
Contains functions used in other parts of the bot.
"""

# Import required modules.
import random
import re

import settings

REGEX_MARCO = re.compile(r"^\s*(m+)(a+)(r+)(c+)(o+)([.…?!\s]*)$", re.I)


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

    # Initialize strings for each letter in matched pattern, plus punctuation.
    m = match.group(1)
    a = match.group(2)
    r = match.group(3)
    c = match.group(4)
    o = match.group(5)
    p = match.group(6)

    # Key-value pairs for what each character will be substituted with.
    character_dicts = [
        {"P": [m]},
        {"O": [a]},
        {"L": [r, c]},
        {"O": [o]},
    ]

    # Initialize empty string.
    s = ""

    # For each character:
    for d in character_dicts:
        # Generate a character string and add it to main to-be-returned string.
        s += gen_char_string(*d.values(), *d)

    # If there's punctuation present, generate a punctuation
    # string and add it to main to-be-returned string.
    if len(p) > 0:
        s += gen_punctuation_string(p)

    # Return string.
    return s


def create_database():
    """
    Creates a SQLite database.
    """

    # Connect to the database.
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    # Create tables and close connection to the database.
    CURSOR.execute(
        """CREATE TABLE message_counts (
            guild_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            last_message_id INTEGER NOT NULL,
            count INTEGER NOT NULL);""")
    CURSOR.close()


def update_database(guild_id, channel_id, last_message_id, count):
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
    results = CURSOR.execute(
        """SELECT count
            FROM message_counts
            WHERE guild_id=? AND channel_id=?;""", params).fetchone()

    # If there are no records on the database for this channel:
    if not results:
        # Save last message ID and message count to the database.
        params = (*params, last_message_id, count)
        CURSOR.execute(
            """INSERT INTO
                message_counts (
                    guild_id,
                    channel_id,
                    last_message_id,
                    count)
                VALUES (?, ?, ?, ?);""", params)

    # If there is a record on the database for this channel:
    else:
        # Update last message ID and message count.
        params = (count, last_message_id, *params)
        CURSOR.execute(
            """UPDATE
                message_counts
                SET count = ?, last_message_id = ?
                WHERE guild_id=? AND channel_id=?;""", params)

    # Commit changes and close connection to the database.
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


def query_database(guild_id, channel_id):
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
    results = CURSOR.execute(
        """SELECT
            count, last_message_id
            FROM message_counts
            WHERE guild_id=? AND channel_id=?;""", (guild_id, channel_id)).fetchone()

    # Close connection to the database and return results.
    CURSOR.close()
    return results
