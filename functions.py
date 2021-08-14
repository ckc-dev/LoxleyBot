"""General use functions used in other parts of the bot."""

import datetime
import io
import json
import random

from discord.ext import commands

import regexes
import settings

# Unnamed and named placeholders to use in SQL queries,
# depending on which database engine is being used.
P = "?" if settings.FILE_BASED_DATABASE else "%s"
PN = ":{}" if settings.FILE_BASED_DATABASE else "%({})s"


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
            based on the amount of characters `i` on the input string.

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
        Generate a string of characters based on input strings.

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
                weights=[1 - uppercase_chance, uppercase_chance]))

        return s

    def gen_punctuation_string(string):
        """
        Generate a string of punctuation, based on input string.

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
        {"P": [match["m"]]},
        {"O": [match["a"]]},
        {"L": [match["r"], match["c"]]},
        {"O": [match["o"]]}
    ]

    for d in character_dicts:
        s += gen_char_string(*d.values(), *d)

    if match["punctuation"]:
        s += gen_punctuation_string(match["punctuation"])

    return s


def divide_in_pairs(n):
    """
    Divide a number into a tuple containing a pair of whole numbers.

    e.g.: An input of 80 returns (40, 40), and an input of 79 returns (39, 40).

    Args:
        n (int): Number to divide.

    Returns:
        Tuple[int]: Resulting pair of numbers.
    """
    return (n // 2, n // 2) if n % 2 == 0 else (n // 2, n // 2 + 1)


def database_exists():
    """Return `True` if database already exists, `False` otherwise."""
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    if settings.FILE_BASED_DATABASE:
        CURSOR.execute("""
            SELECT name
              FROM sqlite_master
             WHERE type="table";""")
    else:
        CURSOR.execute("""
            SELECT table_name
              FROM information_schema.tables
             WHERE table_schema='public'
               AND table_type='BASE TABLE';""")

    results = CURSOR.fetchall()
    CURSOR.close()

    return bool(results)


def database_create():
    """Create database tables."""
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    CURSOR.execute("""
        CREATE TABLE message_counts(
                   guild_id BIGINT NOT NULL,
                 channel_id BIGINT NOT NULL UNIQUE,
            last_message_id BIGINT NOT NULL,
                      count INTEGER NOT NULL);""")
    CURSOR.execute("""
        CREATE TABLE copypastas(
                  id INTEGER NOT NULL,
            guild_id BIGINT NOT NULL,
               title TEXT NOT NULL,
             content TEXT NOT NULL,
               count INTEGER DEFAULT 0);""")
    CURSOR.execute("""
        CREATE TABLE guild_data(
                                   guild_id BIGINT NOT NULL UNIQUE,
                                     prefix TEXT NOT NULL,
                                     locale TEXT NOT NULL,
                                   timezone TEXT NOT NULL,
                       copypasta_channel_id BIGINT UNIQUE,
            copypasta_channel_last_saved_id BIGINT UNIQUE,
                         logging_channel_id BIGINT UNIQUE,
                        birthday_channel_id BIGINT UNIQUE);""")
    CURSOR.execute("""
        CREATE TABLE copypasta_bans(
            guild_id BIGINT NOT NULL,
             user_id BIGINT NOT NULL);""")
    CURSOR.execute("""
        CREATE TABLE birthdays(
            guild_id BIGINT NOT NULL,
             user_id BIGINT NOT NULL,
               month INTEGER NOT NULL,
                 day INTEGER NOT NULL,
         PRIMARY KEY (guild_id, user_id));""")
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


def database_guild_initialize(guild_id):
    """
    Add initial, default guild data to the database.

    Args:
        guild_id (int): ID of guild which will be initialized.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    CURSOR.execute(f"""
        INSERT INTO guild_data (guild_id, prefix, locale, timezone)
             VALUES ({P}, {P}, {P}, {P});""", (
        guild_id,
        settings.GUILD_DEFAULT_PREFIX,
        settings.GUILD_DEFAULT_LOCALE,
        settings.GUILD_DEFAULT_TIMEZONE))
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


def database_guild_prefix_get(client, message, by_id=False):
    """
    Get a guild prefix from the database.

    A guild ID can also be passed directly instead of a message, as long as
        `by_id` is also passed as `True`.

    Args:
        client (discord.Client): Client to which guild prefix will be queried.
        message (discord.Message): Message coming from guild which prefix will
            be queried.
        by_id (bool, optional): Whether or not to get prefix by passing a guild
            ID to function, instead of a message object. Defaults to False.

    Returns:
        str: Guild prefix.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    CURSOR.execute(f"""
        SELECT prefix
          FROM guild_data
         WHERE guild_id = {P};""", (message if by_id else message.guild.id,))

    results = CURSOR.fetchone()

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

    CURSOR.execute(f"""
        UPDATE guild_data
           SET prefix = {P}
         WHERE guild_id = {P};""", (prefix, guild_id))
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

    CURSOR.execute(f"""
        SELECT locale
          FROM guild_data
         WHERE guild_id = {P};""", (guild_id,))

    results = CURSOR.fetchone()

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

    CURSOR.execute(f"""
        UPDATE guild_data
           SET locale = {P}
         WHERE guild_id = {P};""", (locale, guild_id))
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


def database_guild_purge(guild_id):
    """
    Delete all data for a guild from the database.

    Args:
        guild_id (int): ID of guild which will have its data deleted.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    CURSOR.execute(f"""
        DELETE FROM message_counts
              WHERE guild_id = {P};""", (guild_id,))
    CURSOR.execute(f"""
        DELETE FROM copypastas
              WHERE guild_id = {P};""", (guild_id,))
    CURSOR.execute(f"""
        DELETE FROM guild_data
              WHERE guild_id = {P};""", (guild_id,))
    CURSOR.execute(f"""
        DELETE FROM copypasta_bans
              WHERE guild_id = {P};""", (guild_id,))
    CURSOR.execute(f"""
        DELETE FROM birthdays
              WHERE guild_id = {P};""", (guild_id,))
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


def database_message_count_get(channel_id):
    """
    Get current message count for a channel from the database.

    Args:
        channel_id (int): ID of the channel whose message count will be
            queried.

    Returns:
        Tuple[int, int]: A tuple containing the message count for this channel
            and the ID of the last message sent to this channel, respectively.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    CURSOR.execute(f"""
        SELECT count,
               last_message_id
          FROM message_counts
         WHERE channel_id = {P};""", (channel_id,))

    results = CURSOR.fetchone()

    CURSOR.close()
    return results


def database_message_count_set(guild_id, channel_id, last_message_id, count):
    """
    Set current message count for a channel on the database.

    Args:
        guild_id (int): ID of the guild containing the channel whose message
            count will be set.
        channel_id (int): ID of the channel whose message count will be set.
        last_message_id (int): ID of the last message sent to this channel.
        count (int): Total message count for this channel.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()
    params = {
        "guild_id": guild_id,
        "channel_id": channel_id,
        "last_message_id": last_message_id,
        "count": count
    }

    CURSOR.execute(f"""
        INSERT INTO message_counts (
                    guild_id,
                    channel_id,
                    last_message_id,
                    count)
             VALUES (
                    {PN.format("guild_id")},
                    {PN.format("channel_id")},
                    {PN.format("last_message_id")},
                    {PN.format("count")})
        ON CONFLICT (channel_id)
          DO UPDATE
                SET last_message_id = {PN.format("last_message_id")},
                    count = {PN.format("count")}""", params)
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


def database_copypasta_get(guild_id, copypasta_id=None):
    """
    Get data for a copypasta from the database.

    If no copypasta ID is passed, will return data for a random copypasta.

    Args:
        guild_id (int): ID of the guild to which copypasta belongs.
        copypasta_id (int, optional): ID of to-be-queried copypasta.
            Defaults to None.

    Returns:
        Tuple[int, str, str, int]: Tuple containing copypasta ID, title,
            content and count, respectively.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()
    params = {"guild_id": guild_id, "id": copypasta_id}

    CURSOR.execute(f"""
        SELECT id,
               title,
               content,
               count
          FROM copypastas
         WHERE guild_id = {PN.format("guild_id")}
        {f'AND id = {PN.format("id")}'
            if copypasta_id else
        'ORDER BY RANDOM()'};""", params)

    results = CURSOR.fetchone()

    if results:
        CURSOR.execute(f"""
            UPDATE copypastas
               SET count = count + 1
             WHERE guild_id = {P}
               AND id = {P};""", (guild_id, results[0]))

    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()

    return results


def database_copypasta_search(guild_id, query=None, by_title=False,
                              exact_match=False, field="count",
                              arrangement="DESC"):
    """
    Search for one or more copypastas on the database.

    If query is `None`, all copypastas belonging to the guild will be returned.

    Args:
        guild_id (int): ID of guild to which copypastas belong.
        query (str, optional): What to search for in copypasta title or
            content. Defaults to None.
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
    params = {
        "guild_id": guild_id,
        "query": f"{'%' if not exact_match else ''}{query or ''}{'%' if not exact_match else ''}"
    }

    CURSOR.execute(f"""
          SELECT id,
                 title,
                 content,
                 count
            FROM copypastas
           WHERE guild_id = {PN.format("guild_id")}
             AND(title LIKE {PN.format("query")}
           {f'OR content LIKE {PN.format("query")}' if not by_title else ''})
        ORDER BY {field} {arrangement};""", params)

    results = CURSOR.fetchall()

    CURSOR.close()
    return results


def database_copypasta_add(guild_id, title, content):
    """
    Add a copypasta to the database.

    Args:
        guild_id (int): ID of guild to which copypasta will belong.
        title (str): Title of the copypasta.
        content (str): Content of the copypasta.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    CURSOR.execute(f"""
        INSERT INTO copypastas(
                    id,
                    guild_id,
                    title,
                    content)
             VALUES (
                    COALESCE (
                              (SELECT id
                                 FROM copypastas
                                WHERE guild_id = {P}
                             ORDER BY id DESC
                                LIMIT 1) + 1,
                             1),
                    {P},
                    {P},
                    {P});""", (guild_id, guild_id, title, content))
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

    CURSOR.execute(f"""
        DELETE FROM copypastas
              WHERE guild_id = {P}
                AND id = {P};""", (guild_id, copypasta_id))
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

    CURSOR.execute(f"""
        SELECT copypasta_channel_id
          FROM guild_data
         WHERE guild_id = {P};""", (guild_id,))

    results = CURSOR.fetchone()

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

    CURSOR.execute(f"""
        UPDATE guild_data
           SET copypasta_channel_id = {P}
         WHERE guild_id = {P};""", (channel_id, guild_id))
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


def database_copypasta_channel_last_saved_id_get(guild_id):
    """
    Get the ID for the last copypasta saved on a guild's copypasta channel.

    Args:
        guild_id (int): ID of guild which will have the ID of the last saved
            copypasta on the copypasta channel queried.

    Returns:
        int: ID of the last saved copypasta on guild's copypasta channel.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    CURSOR.execute(f"""
        SELECT copypasta_channel_last_saved_id
          FROM guild_data
         WHERE guild_id = {P};""", (guild_id,))

    results = CURSOR.fetchone()

    CURSOR.close()
    return results[0]


def database_copypasta_channel_last_saved_id_set(guild_id, last_saved_id):
    """
    Set the ID for the last copypasta saved on a guild's copypasta channel.

    Args:
        guild_id (int): ID of guild which will have the ID of the last saved
            copypasta on the copypasta channel set.
        last_saved_id (int): What to set the ID of the last saved copypasta
            on the copypasta channel to.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    CURSOR.execute(f"""
        UPDATE guild_data
           SET copypasta_channel_last_saved_id = {P}
         WHERE guild_id = {P};""", (last_saved_id, guild_id))
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


def database_copypasta_ban_get(guild_id, user_id):
    """
    Get ban status for a user's capability to add copypastas to a guild.

    Args:
        guild_id (int): ID of guild which user belongs to.
        user_id (int): ID of user which will have ban status queried.

    Returns:
        Tuple[int]: Tuple containing user ID.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    CURSOR.execute(f"""
        SELECT user_id
          FROM copypasta_bans
         WHERE guild_id = {P}
           AND user_id = {P};""", (guild_id, user_id))

    results = CURSOR.fetchone()

    CURSOR.close()
    return results


def database_copypasta_ban_user(guild_id, user_id):
    """
    Ban a user from adding copypastas to a guild.

    Args:
        guild_id (int): ID of guild from which user will be banned
            from adding copypastas.
        user_id (int): ID of user who will be banned from adding copypastas to
            the guild.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    CURSOR.execute(f"""
        INSERT INTO copypasta_bans(
                    guild_id,
                    user_id)
             VALUES ({P}, {P});""", (guild_id, user_id))
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


def database_copypasta_unban_user(guild_id, user_id):
    """
    Unban a user from adding copypastas to a guild.

    Args:
        guild_id (int): ID of guild from which user will be unbanned
            from adding copypastas.
        user_id (int): ID of user who will be unbanned from adding copypastas
            to the guild.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    CURSOR.execute(f"""
        DELETE FROM copypasta_bans
              WHERE guild_id = {P}
                AND user_id = {P};""", (guild_id, user_id))
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

    CURSOR.execute(f"""
        SELECT logging_channel_id
          FROM guild_data
         WHERE guild_id = {P};""", (guild_id,))

    results = CURSOR.fetchone()

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

    CURSOR.execute(f"""
        UPDATE guild_data
           SET logging_channel_id = {P}
         WHERE guild_id = {P};""", (channel_id, guild_id))
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


def database_guild_timezone_get(guild_id):
    """
    Get the timezone for a guild from the database.

    Args:
        guild_id (int): ID of guild which will have its timezone queried.

    Returns:
        str: Guild's timezone, formatted as {+|-}HH:MM, e.g.: +00:00.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    CURSOR.execute(f"""
        SELECT timezone
          FROM guild_data
         WHERE guild_id = {P};""", (guild_id,))

    results = CURSOR.fetchone()

    CURSOR.close()
    return results[0]


def database_guild_timezone_set(guild_id, timezone):
    """
    Set the timezone for a guild on the database.

    Args:
        guild_id (int): ID of guild which will have its timezone set.
        timezone (str): What to set guild's timezone to.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    CURSOR.execute(f"""
        UPDATE guild_data
           SET timezone = {P}
         WHERE guild_id = {P};""", (timezone, guild_id))
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


def database_birthday_channel_get(guild_id):
    """
    Get the ID for a guild's birthday announcement channel from the database.

    Args:
        guild_id (int): ID of guild which will have its birthday
            announcement channel ID queried.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    CURSOR.execute(f"""
        SELECT birthday_channel_id
          FROM guild_data
         WHERE guild_id = {P};""", (guild_id,))

    results = CURSOR.fetchone()

    CURSOR.close()

    # Since this is used in a loop, `if results else None` is added just in
    # case guild does not have a birthday announcement channel set up.
    return results[0] if results else None


def database_birthday_channel_set(guild_id, channel_id):
    """
    Set the ID for a guild's birthday announcement channel on the database.

    Args:
        guild_id (int): ID of guild which will have its birthday
            announcement channel ID set.
        channel_id (int): What to set guild's birthday
            announcement channel ID to.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    CURSOR.execute(f"""
        UPDATE guild_data
           SET birthday_channel_id = {P}
         WHERE guild_id = {P};""", (channel_id, guild_id))
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


def database_birthday_add(guild_id, user_id, month, day):
    """
    Add a birthday to the database.

    Args:
        guild_id (int): ID of guild to which birthday belongs.
        user_id (int): ID of user who will have birthday added.
        month (int): Birthday month.
        day (int):  Birthday day.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()
    params = {
        "guild_id": guild_id,
        "user_id": user_id,
        "month": month,
        "day": day
    }

    CURSOR.execute(f"""
        INSERT INTO birthdays (
                    guild_id,
                    user_id,
                    month,
                    day)
             VALUES (
                    {PN.format("guild_id")},
                    {PN.format("user_id")},
                    {PN.format("month")},
                    {PN.format("day")})
        ON CONFLICT (guild_id, user_id)
          DO UPDATE
                SET month = {PN.format("month")},
                    day = {PN.format("day")};""", params)
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


def database_birthday_delete(guild_id, user_id):
    """
    Delete a birthday from the database.

    Args:
        guild_id (int): ID of guild to which birthday belongs.
        user_id (int): ID of user who will have birthday deleted.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    CURSOR.execute(f"""
        DELETE FROM birthdays
              WHERE guild_id = {P}
                AND user_id = {P};""", (guild_id, user_id))
    settings.DATABASE_CONNECTION.commit()
    CURSOR.close()


def database_birthday_list_get(guild_id, month, day):
    """
    Get a list of birthdays for a guild and date.

    Args:
        guild_id (int): ID of guild which will have birthdays queried.
        month (int): Month to use when querying birthdays.
        day (int): Day to use when querying birthdays.

    Returns:
        List[Tuple[int]]: A list of tuples containing the IDs of users whose
            birthday is on this day and month in this guild as their first and
            only item.
    """
    CURSOR = settings.DATABASE_CONNECTION.cursor()

    CURSOR.execute(f"""
        SELECT user_id
          FROM birthdays
         WHERE guild_id = {P}
           AND month = {P}
           AND day = {P};""", (guild_id, month, day))

    results = CURSOR.fetchall()

    CURSOR.close()
    return results


def copypasta_export_json(guild_id):
    """
    Return memory buffers containing all guild copypastas, formatted as JSON.

    Args:
        guild_id (int): ID of guild which will have its copypastas exported.

    Returns:
        List[io.BytesIO]: A list of memory buffers containing copypastas,
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

    Returns `None` if an error occurs when trying to load JSON data.

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
                    title = regexes.FIRST_FEW_WORDS.match(content)[1]

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
        List[str]: A list of strings containing available bot locales.
    """
    return list(LOCALIZATION.keys())


def get_localized_object(guild_id, reference, locale=None, as_list=False):
    """
    Get a localized object from the localization file for a guild.

    This object may be a string, list of objects, or dictionary.

    If no specific locale code is passed, guild locale will be used.

    If the object is a list and `as_list` is `False`, a random object from it
        will be returned.

    Args:
        guild_id (int): ID of guild to get localized object for.
        reference (str): Reference to which object to get.
        locale (str, optional): Locale code used to get the object.
            Defaults to none.
        as_list (bool, optional): Whether or not to return the whole list when
            getting a list object. Defaults to False.

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


def raise_missing_permissions(permissions):
    """
    Raise commands.MissingPermissions for missing permissions to run a command.

    Gets required permissions as an input, creates a list of missing
        permissions, and raises exception using those.

    Args:
        permissions (discord.Permissions): Permissions required to run command.

    Raises:
        commands.MissingPermissions: Raised when the command invoker does not
            have the permissions required to run a command.
    """
    missing = ([perm for perm, required in iter(permissions) if required])

    raise commands.MissingPermissions(missing)


def utc_to_local(utc_time, guild_id):
    """
    Adjust a UTC datetime object to a guild's timezone.

    Args:
        utc_time (datetime.datetime): UTC time.
        guild_id (int): ID of guild for which time will be adjusted.

    Returns:
        datetime.datetime: Adjusted datetime object.
    """
    guild_timezone = database_guild_timezone_get(guild_id)
    match = regexes.TIMEZONE.fullmatch(guild_timezone)
    hour_adjustment = int(match["sign"] + match["hours"])
    minute_adjustment = int(match["sign"] + match["minutes"])
    adjusted_time = utc_time + datetime.timedelta(
        hours=hour_adjustment, minutes=minute_adjustment)

    return adjusted_time
