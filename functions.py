"""Contains general use functions used in other parts of the bot."""

import io
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
            strings (List[str]): A list containing strings used to generate
                results from.
            sub (str): String or character to substitute strings with.

        Returns:
            str: Generated string.
        """
        s = ""

        # Get the chance any character has of being uppercase, by dividing the
        # number of uppercase characters by the total number of characters in
        # all strings.
        uppercase_chance = sum(
            1 for c in "".join(strings) if c.isupper()) / len("".join(strings))

        # Decide whether current character will be uppercase or not and add it
        # to string. Do this a number of times equal to the average number of
        # characters in all strings.
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
            string (str): A group of punctuation characters used to generate
                string.

        Returns:
            str: Generated string.
        """
        s = ""
        d = {}

        # Populate dictionary with each unique character and the amount of
        # times it appears in input string.
        for c in set([c for c in string]):
            d[c] = string.count(c)

        # Pick a random character based on how many times that character
        # appears, then add it to main, to-be-returned string. Do this a number
        # of times generated using input string.
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
             content TEXT NOT NULL,
               count INTEGER DEFAULT 0);""")
    CURSOR.execute("""
        CREATE TABLE guild_data(
                        guild_id INTEGER NOT NULL UNIQUE,
                          prefix TEXT NOT NULL,
                          locale TEXT NOT NULL,
            copypasta_channel_id INTEGER UNIQUE,
              logging_channel_id INTEGER UNIQUE);""")
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


def database_guild_prefix_get(client, message):
    """
    Get a guild prefix from the database.

    Args:
        client (discord.Client): Client to which guild prefix will be queried.
        message (discord.Message): Message coming from guild which prefix will
            be queried.

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
            content and count, respectively.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    params = {"guild_id": guild_id, "id": copypasta_id}
    results = CURSOR.execute(f"""
        SELECT id,
               title,
               content,
               count
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
                              exact_match=False, field="count",
                              arrangement="DESC"):
    """
    Search for one or more copypastas on the database.

    Args:
        guild_id (int): ID of guild to which copypastas belong.
        query (str, optional): What to search for in copypasta title or
            content. If query is None, all copypastas that
            belong to this guild will be returned. Defaults to None.
        by_title (bool, optional): Whether or not to search only by
            title and not by content. Defaults to False.
        exact_match (bool, optional): Whether or not to search for an exact
            match. Defaults to False.
        field (str, optional): Which field results will be ordered by.
            Defaults to "count".
        arrangement (str, optional): Which arrangement results will follow.
            "ASC" for ascending or "DESC" for descending. Defaults to "DESC".

    Returns:
        List[Tuple[int, str, str, int]]: A list of tuples containing
            copypasta ID, title, content and count, respectively.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()
    params = {"guild_id": guild_id,
              "query": f"{'%' if not exact_match else ''}{query or ''}{'%' if not exact_match else ''}"}
    results = CURSOR.execute(f"""
          SELECT id,
                 title,
                 content,
                 count
            FROM copypastas
           WHERE guild_id = :guild_id
             AND(title LIKE :query
            {'OR content LIKE :query' if not by_title else ''})
        ORDER BY {field} {arrangement};""", params).fetchall()
    CURSOR.close()

    return results


def database_copypasta_add(guild_id, title, content):
    """
    Add a copypasta to the database.

    Args:
        guild_id (int): ID of guild to which copypasta will belong.
        title (str): Title of the copypasta.
        content (str): Contents of the copypasta.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()
    CURSOR.execute("""
        INSERT INTO copypastas(
            id,
            guild_id,
            title,
            content
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
        );""", (guild_id, guild_id, title, content))
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


def database_copypasta_channel_get(guild_id):
    """
    Get the ID for a guild's copypasta channel from the database.

    Args:
        guild_id (int): ID of guild which will have its copypasta
            channel ID queried.

    Returns:
        int: Guild's copypasta channel ID.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()
    results = CURSOR.execute("""
        SELECT copypasta_channel_id
          FROM guild_data
         WHERE guild_id = ?;""", (guild_id,)).fetchone()
    CURSOR.close()

    return results[0]


def database_copypasta_channel_set(guild_id, channel_id):
    """
    Set the ID for a guild's copypasta channel on the database.

    Args:
        guild_id (int): ID of guild which will have its copypasta
            channel ID set.
        channel_id (int): What to set guild's copypasta channel ID to.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()
    CURSOR.execute("""
        UPDATE guild_data
           SET copypasta_channel_id = ?
         WHERE guild_id = ?;""", (channel_id, guild_id))
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


def database_logging_channel_get(guild_id):
    """
    Get the ID for a guild's logging channel from the database.

    Args:
        guild_id (int): ID of guild which will have its logging channel ID
            queried.

    Returns:
        int: Guild's logging channel ID.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()
    results = CURSOR.execute("""
        SELECT logging_channel_id
          FROM guild_data
         WHERE guild_id = ?;""", (guild_id,)).fetchone()
    CURSOR.close()

    return results[0]


def database_logging_channel_set(guild_id, channel_id):
    """
    Set the ID for a guild's logging channel on the database.

    Args:
        guild_id (int): ID of guild which will have its logging channel ID set.
        channel_id (int): What to set guild's logging channel ID to.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()
    CURSOR.execute("""
        UPDATE guild_data
           SET logging_channel_id = ?
         WHERE guild_id = ?;""", (channel_id, guild_id))
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


def copypasta_export_json(guild_id):
    """
    Return memory buffers containing all guild copypastas, formatted as JSON.

    Args:
        guild_id (int): ID of guild which will have its copypastas exported.

    Returns:
        List(io.BytesIO): A list of memory buffers containing copypastas,
            formatted as JSON.
    """
    # A number of bytes (or characters) is removed from Discord's file size
    # limit to calculate a maximum file size. This is done to account for a
    # margin of error on individual copypasta sizes due to JSON indentation and
    # commas. Otherwise, the final file size could be larger than the limit,
    # after converting it to JSON.
    MAX_FILE_SIZE = settings.DISCORD_FILE_BYTE_LIMIT - 65536
    copypastas = database_copypasta_search(
        guild_id, field="id", arrangement="ASC")
    keys = ("id", "title", "content", "count")
    copypasta_dicts = [dict(zip(keys, copypasta)) for copypasta in copypastas]
    cur_file_size = 0
    copypastas_within_limit = []
    copypasta_lists = []

    for dict_ in copypasta_dicts:
        formatted = json.dumps(
            dict_,
            indent=settings.COPYPASTA_JSON_INDENT_AMOUNT,
            ensure_ascii=False)
        size = io.BytesIO(formatted.encode("utf-8")).getbuffer().nbytes

        if cur_file_size + size > MAX_FILE_SIZE and copypastas_within_limit:
            copypasta_lists.append(copypastas_within_limit)
            copypastas_within_limit = []

        if size > MAX_FILE_SIZE:
            continue

        copypastas_within_limit.append(dict_)

        if dict_ == copypasta_dicts[-1]:
            copypasta_lists.append(copypastas_within_limit)

        formatted_file = json.dumps(
            copypastas_within_limit,
            indent=settings.COPYPASTA_JSON_INDENT_AMOUNT,
            ensure_ascii=False)
        cur_file_size = io.BytesIO(
            formatted_file.encode("utf-8")).getbuffer().nbytes

    buffers = []

    for list_ in copypasta_lists:
        formatted = json.dumps(
            list_,
            indent=settings.COPYPASTA_JSON_INDENT_AMOUNT,
            ensure_ascii=False)
        buffers.append(io.BytesIO(formatted.encode("utf-8")))

    return buffers


def copypasta_import_json(data, guild_id):
    """
    Load copypastas from a JSON file and import them to the database.

    After data is saved, operation results are returned.

    Args:
        data (str, bytes): Data to be loaded as JSON.
        guild_id (int): ID of guild which will have copypastas imported to.

    Returns:
        Tuple[List, List, List, List]: A tuple which contains lists containing
            data for copypastas parsed from JSON, imported to the database,
            ignored (already on the database), and invalid (due to invalid
            keys), respectively.
    """
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError:
        return

    imported = []
    ignored = []
    invalid = []

    for copypasta in parsed:
        try:
            title = copypasta["title"]
            content = copypasta["content"]
            exists = database_copypasta_search(
                guild_id, content, exact_match=True)

            if not exists:
                if not title:
                    title = regexes.FIRST_FEW_WORDS.match(content).group(1)

                if (len(content) > settings.DISCORD_EMBED_DESCRIPTION_LIMIT
                        or len(title) > settings.DISCORD_EMBED_TITLE_LIMIT):
                    invalid.append(copypasta)
                    continue

                database_copypasta_add(guild_id, title, content)
                imported.append(copypasta)
            else:
                ignored.append(copypasta)

        # Catch exceptions in case user has modified exported files manually.
        # KeyError: Raised due to invalid key values.
        # TypeError: Raised due to invalid nesting level, which would result in
        # code using "title" as a positional index to a string.
        except (KeyError, TypeError):
            invalid.append(copypasta)

    return (parsed, imported, ignored, invalid)


with open(settings.LOCALIZATION_FILE_NAME, encoding="utf8") as f:
    LOCALIZATION = json.load(f)


def get_available_locales():
    """
    Get current available bot locales.

    Returns:
        List(str): A list of strings containing available bot locales.
    """
    return list(LOCALIZATION.keys())


def get_localized_object(guild_id, reference, locale=None, as_list=False):
    """
    Get a localized object from the localization file for a guild.

    This object may be a string, list of objects, or dictionary.
    If no specific locale code is passed, guild locale will be used.

    Args:
        guild_id (int): ID of guild to get localized object for.
        reference (str): Reference to which object to get.
        locale (str, optional): Locale code used to get the object.
            Defaults to none.
        as_list (bool, optional): Whether or not to return the whole list when
            getting a list object. If False, a random object from the list is
            returned. Defaults to False

    Returns:
        One of the following:

        str: Localized string.
        list: Localized list.
        dict: Localized dictionary.
    """
    if not locale:
        locale = database_guild_locale_get(guild_id)

    obj = LOCALIZATION[locale][reference]

    if not as_list and isinstance(obj, list):
        return random.choice(obj)

    return obj
