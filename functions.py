"""Contains general use functions used in other parts of the bot."""

import json
import random

import regexes
import settings


def marco_polo(string):
    """
    Return an answer to "Marco", "Marco!", "Marco..." or another variation.

    The answer is based on the user input plus random chances.

    Args:
        string (str): String containing user input.

    Returns:
        str: "Polo" answer.
    """
    def gen_char_amount(string):
        """
        Generate a random integer, to be used as a number of characters.

        Randomly picks a number of characters between `i - 2` and `i + 2`,
        based on the amount of characters on the user input.

        Args:
            string (str): A string of characters to get amount from.

        Returns:
            int: Number of characters.
        """
        i = len(string)

        return max(1, *random.choices(
            [i - 2, i - 1, i, i + 1, i + 2],
            weights=[.15, .35, 9, .35, .15]
        ))

    def gen_char_string(strings, sub):
        """
        Generate a string of characters based on user input.

        Args:
            strings (List[str]): A list containing strings used to
                generate results from.
            sub (str): String or character to substitute strings with.

        Returns:
            str: Generated string.
        """
        s = ""

        # Get the chance any character has of being uppercase,
        # by dividing the number of uppercase characters by
        # the total number of characters in all strings.
        uppercase_chance = sum(
            1 for c in "".join(strings) if c.isupper()) / len("".join(strings))

        # Decide whether current character will be uppercase or not,
        # and add it to string. Do this a number of times equal to
        # the average number of characters in all strings:
        for _ in range(sum(gen_char_amount(s) for s in strings) // len(strings)):
            s += "".join(random.choices(
                [sub.lower(), sub.upper()],
                weights=[1 - uppercase_chance, uppercase_chance]
            ))

        return s

    def gen_punctuation_string(string):
        """
        Generate a string of punctuation, based on user input.

        Args:
            string (str): A group of punctuation characters
                to generate string from.

        Returns:
            str: Generated string.
        """
        s = ""
        d = {}

        # Populate dictionary with each unique character and
        # the amount of times it appears in input string.
        for c in set([c for c in string]):
            d[c] = string.count(c)

        # Pick a random character based on how many times that
        # character appears, then add it to main, to-be-returned string.
        # Do this a number of times generated using input string.
        for _ in range(gen_char_amount(string)):
            s += "".join(random.choices([*d], weights=[*d.values()]))

        return s

    s = ""
    match = regexes.MARCO.fullmatch(string)
    character_dicts = [
        {"P": [match.group("m")]},
        {"O": [match.group("a")]},
        {"L": [match.group("r"), match.group("c")]},
        {"O": [match.group("o")]},
    ]

    for d in character_dicts:
        s += gen_char_string(*d.values(), *d)

    if match.group("punctuation"):
        s += gen_punctuation_string(match.group("punctuation"))

    return s


def divide_in_pairs(n):
    """
    Divide a number into a tuple containing a pair of whole numbers.

    E.g.: 80 returns (40, 40), 79 returns (39, 40).

    Args:
        n (int): Number to divide.

    Returns:
        Tuple[int]: Resulting pair of numbers.
    """
    return (n // 2, n // 2) if n % 2 == 0 else (n // 2, n // 2 + 1)


def database_exists():
    """Return True if database file already exists, False otherwise."""
    CURSOR = settings.DATABASE_CONNECTION.cursor()
    results = CURSOR.execute("""
        SELECT name
          FROM sqlite_master
         WHERE type="table";""").fetchall()
    CURSOR.close()

    return bool(results)


def database_create():
    """Create a SQLite database."""
    CURSOR = settings.DATABASE_CONNECTION.cursor()
    CURSOR.execute("""
        CREATE TABLE message_counts(
                   guild_id INTEGER NOT NULL,
                 channel_id INTEGER NOT NULL UNIQUE,
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
        CREATE TABLE guild_data(
            guild_id INTEGER NOT NULL UNIQUE,
              prefix TEXT NOT NULL,
              locale TEXT NOT NULL);""")
    CURSOR.close()


def database_guild_initialize(guild_id):
    """
    Add initial, default guild data to the database.

    Args:
        guild_id (int): ID of guild which will be initialized.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()
    CURSOR.execute("""
        INSERT INTO guild_data (guild_id, prefix, locale)
             VALUES (?, ?, ?);""", (guild_id, settings.BOT_DEFAULT_PREFIX,
                                    settings.BOT_DEFAULT_LOCALE))
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


def database_guild_prefix_get(_client, message):
    """
    Get a guild prefix from the database.

    Args:
        client (discord.Client): Client to which guild prefix will be queried.
        message (discord.Message): Message coming from guild which prefix
            will be queried.

    Returns:
        str: Guild prefix.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()
    results = CURSOR.execute("""
        SELECT prefix
          FROM guild_data
         WHERE guild_id = ?;""", (message.guild.id,)).fetchone()
    CURSOR.close()

    return results[0]


def database_guild_prefix_set(guild_id, prefix):
    """
    Set a prefix for a guild on the database.

    Args:
        guild_id (int): ID of guild which will have its prefix set.
        prefix (str): What to set guild prefix to.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()
    CURSOR.execute("""
        UPDATE guild_data
           SET prefix = ?
         WHERE guild_id = ?;""", (prefix, guild_id))
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


def database_guild_locale_get(guild_id):
    """
    Get a guild locale from the database.

    Args:
        guild_id (int): ID of guild which will have its locale queried.

    Returns:
        str: Guild locale.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()
    results = CURSOR.execute("""
        SELECT locale
          FROM guild_data
         WHERE guild_id = ?;""", (guild_id,)).fetchone()
    CURSOR.close()

    return results[0]


def database_guild_locale_set(guild_id, locale):
    """
    Set a locale for a guild on the database.

    Args:
        guild_id (int): ID of guild which will have its locale set.
        locale (str): What to set guild locale to.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()
    CURSOR.execute("""
        UPDATE guild_data
           SET locale = ?
         WHERE guild_id = ?;""", (locale, guild_id))
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


def database_guild_purge(guild_id):
    """
    Delete all data for a guild from the database.

    Args:
        guild_id (int): ID of guild which will have its data deleted.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()
    CURSOR.execute("""
        DELETE FROM message_counts
              WHERE guild_id = ?;""", (guild_id,))
    CURSOR.execute("""
        DELETE FROM copypastas
              WHERE guild_id = ?;""", (guild_id,))
    CURSOR.execute("""
        DELETE FROM guild_data
              WHERE guild_id = ?;""", (guild_id,))
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


def database_message_count_get(channel_id):
    """
    Get current message count for a channel from the database.

    Args:
        channel_id (int): ID of the channel whose number of messages
            will be queried.

    Returns:
        Tuple[int, int]: A tuple containing the message count for this channel
            and the ID of the last message sent to this channel, respectively.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()
    results = CURSOR.execute("""
        SELECT count,
               last_message_id
          FROM message_counts
         WHERE channel_id = ?;""", (channel_id,)).fetchone()
    CURSOR.close()

    return results


def database_message_count_set(guild_id, channel_id, last_message_id, count):
    """
    Set current message count for a channel on the database.

    Args:
        channel_id (int): ID of the channel whose number of messages
            will be set.
        last_message_id (int): ID of the last message sent to this channel.
        count (int): Total message count for this channel.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()
    CURSOR.execute("""
        INSERT OR REPLACE
                     INTO message_counts (
                          guild_id,
                          channel_id,
                          last_message_id,
                          count)
                   VALUES (?, ?, ?, ?);""", (guild_id, channel_id,
                                             last_message_id, count))
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


def database_copypasta_get(guild_id, copypasta_id=None):
    """
    Get data for a copypasta from the database.

    Args:
        guild_id (int): ID of the guild to which copypasta belongs.
        copypasta_id (int, optional): ID of to-be-queried copypasta.
            If no ID is passed, will return data for a random copypasta.
            Defaults to None.

    Returns:
        Tuple[int, str, str, int]: Tuple containing copypasta ID, title,
            contents and count, respectively.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    params = {"guild_id": guild_id, "id": copypasta_id}
    results = CURSOR.execute(f"""
        SELECT id,
               title,
               contents
          FROM copypastas
         WHERE guild_id = :guild_id
         {'AND id = :id'
            if copypasta_id else
        'ORDER BY RANDOM()'};""", params).fetchone()

    if results:
        CURSOR.execute("""
            UPDATE copypastas
               SET count = count + 1
             WHERE guild_id = ?
               AND id = ?;""", (guild_id, results[0]))

    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()

    return results


def database_copypasta_search(guild_id, query=None, by_title=False,
                              field="count", arrangement="DESC"):
    """
    Search for one or more copypastas on the database.

    Args:
        guild_id (int): ID of guild to which copypastas belong.
        query (str, optional): What to search for in copypasta title or
            contents. If query is None, all copypastas that
            belong to this guild will be returned. Defaults to None.
        by_title (bool, optional): Whether or not to search only by
            title and not by contents. Defaults to False.
        field (str, optional): Which field results will be ordered by.
            Defaults to "count".
        arrangement (str, optional): Which arrangement results will follow.
            "ASC" for ascending or "DESC" for descending. Defaults to "DESC".

    Returns:
        List[Tuple[int, str, str, int]]: A list of tuples containing
            copypasta ID, title, contents and count, respectively.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()
    params = {"guild_id": guild_id, "query": f"%{query or ''}%"}
    results = CURSOR.execute(f"""
          SELECT id,
                 title,
                 contents,
                 count
            FROM copypastas
           WHERE guild_id = :guild_id
             AND(title LIKE :query
            {'OR contents LIKE :query' if not by_title else ''})
        ORDER BY {field} {arrangement};""", params).fetchall()
    CURSOR.close()

    return results


def database_copypasta_add(guild_id, title, contents):
    """
    Add a copypasta to the database.

    Args:
        guild_id (int): ID of guild to which copypasta will belong.
        title (str): Title of the copypasta.
        contents (str): Contents of the copypasta.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()
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
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


def database_copypasta_delete(guild_id, copypasta_id):
    """
    Delete a copypasta from the database.

    Args:
        guild_id (int): ID of guild to which copypasta belongs.
        copypasta_id (int): ID of to-be-deleted copypasta.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()
    CURSOR.execute("""
        DELETE FROM copypastas
              WHERE guild_id = ?
                AND id = ?;""", (guild_id, copypasta_id))
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


with open(settings.LOCALIZATION_FILE_NAME) as f:
    LOCALIZED_MESSAGES = json.loads(f.read())


def get_available_locales():
    """
    Get current available bot locales.

    Returns:
        List(str): A list of strings containing available bot locales.
    """
    return list(LOCALIZED_MESSAGES.keys())


def get_localized_object(guild_id, message, locale=None):
    """
    Get a localized object from the localization file for a guild.

    This object may be a string, list of strings, or dictionary.
    If no specific locale code is passed, guild locale will be used.

    Args:
        guild_id (int): ID of guild to get localized message for.
        message (str): What message to get.
        locale (str, optional): Locale code used to get the message.
            Defaults to none.

    Returns:
        One of the following:

        str: Localized message.
        dict: Localized dictionary.
        list: Localized list.
    """
    if not locale:
        locale = database_guild_locale_get(guild_id)

    return LOCALIZED_MESSAGES[locale][message]
