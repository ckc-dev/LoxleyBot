"""
Contains functions used in other parts of the bot.
"""

# Import required modules.
import random
import re
import sqlite3

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
        I = len(group)

        # Randomly pick an amount of characters between `I - 2` and `I + 2`.
        return max(1, *random.choices(
            [I - 2, I - 1, I, I + 1, I + 2],
            weights=[.15, .35, 9, .35, .15]
        ))

    def gen_char_string(groups, sub):
        """
        Generates a string of characters, based on user input.

        Args:
            groups ([str]): A list containing groups of characters to generate string from.
                            E.g.: ["mm"] or ["RrrRr", "c"].
            sub (str): String (character) to substitute groups of characters with. E.g.: "P" or "L".

        Returns:
            str: Generated string. E.g.: "Pp" or "LLLllL".
        """

        # Initialize empty string.
        s = ""

        # Get the chance any character has of being uppercase, by dividing the number
        # of uppercase characters by the total number of characters in all groups.
        UPPERCASE_CHANCE = sum(
            1 for c in "".join(groups) if c.isupper()) / len("".join(groups))

        # Do the following a number of times equal to the average number of characters in all groups:
        for _ in range(int(sum(gen_char_amount(group) for group in groups)/len(groups))):
            # Decide whether current character will be uppercase or not, and add it to string.
            s += "".join(random.choices(
                [sub.lower(), sub.upper()],
                weights=[1 - UPPERCASE_CHANCE, UPPERCASE_CHANCE]
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
    MATCH = REGEX_MARCO.match(string)

    # Initialize strings for each letter in matched pattern, plus punctuation.
    M = MATCH.group(1)
    A = MATCH.group(2)
    R = MATCH.group(3)
    C = MATCH.group(4)
    O = MATCH.group(5)
    P = MATCH.group(6)

    # Key-value pairs for what each character will be substituted with.
    CHARACTER_DICTS = [
        {"P": [M]},
        {"O": [A]},
        {"L": [R, C]},
        {"O": [O]},
    ]

    # Initialize empty string.
    s = ""

    # For each character:
    for d in CHARACTER_DICTS:
        # Generate a character string and add it to main to-be-returned string.
        s += gen_char_string(*d.values(), *d)

    # If there's punctuation present, generate a punctuation
    # string and add it to main to-be-returned string.
    if len(P) > 0:
        s += gen_punctuation_string(P)

    # Return string.
    return s


def create_database():
    """
    Creates a SQLite database.
    """

    # Connect to the database file or create a new one, if it doesn't exist.
    connection = sqlite3.connect("sqlite.db")
    cursor = connection.cursor()

    # Create tables and close connection to the database.
    cursor.execute(
        """CREATE TABLE message_counts (
            guild_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            last_message_id INTEGER NOT NULL,
            count INTEGER NOT NULL);""")
    connection.close()
