"""Bot settings."""

import logging
import os
import sqlite3

import dotenv
import psycopg2

# Load environment variables (such as bot token).
dotenv.load_dotenv()

# Values to use when initializing bot.
LOCALIZATION_FILE_NAME = "localization.json"
BOT_ACTIVITY = "@me for help! | https://github.com/ckc-dev/LoxleyBot"
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("'BOT_TOKEN' environment variable was not provided.")

# Values to use when bot first enters a guild.
GUILD_DEFAULT_PREFIX = "./"
GUILD_DEFAULT_LOCALE = "en-US"
GUILD_DEFAULT_TIMEZONE = "+00:00"

# Names commonly used for "general" text channel.
COMMON_GENERAL_TEXT_CHANNEL_NAMES = ["general", "geral", "chat", "common"]

# Values to use when setting up logging.
LOGGER = logging.getLogger("discord")
HANDLER = logging.FileHandler(filename="bot.log", encoding="utf-8", mode="w")
LOG_FORMAT = "%(asctime)s:%(levelname)s:%(name)s: %(message)s"
HANDLER.setFormatter(logging.Formatter(LOG_FORMAT))
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(HANDLER)

# Values to use when working with the database.

# If `True`, SQLite will be used as the database engine, otherwise,
# PostgreSQL will be used.
FILE_BASED_DATABASE = False
SQLITE_DATABASE_NAME = "sqlite.db"
POSTGRESQL_DATABASE_URL = os.getenv("DATABASE_URL")

if FILE_BASED_DATABASE:
    DATABASE_CONNECTION = sqlite3.connect(SQLITE_DATABASE_NAME)
else:
    if not POSTGRESQL_DATABASE_URL:
        raise ValueError(
            "'DATABASE_URL' environment variable was not provided.")

    DATABASE_CONNECTION = psycopg2.connect(POSTGRESQL_DATABASE_URL)

# Values to use when generating copypasta embeds.
DISCORD_EMBED_TITLE_LIMIT = 256
DISCORD_EMBED_DESCRIPTION_LIMIT = 2048
EMBED_COLOR = 0x1794be

# Values to use when generating a list of copypastas.
DISCORD_CHARACTER_LIMIT = 2000
COPYPASTA_LIST_CHARACTERS_PER_ROW = 80

# Values to use when generating a copypasta JSON file to be exported.
DISCORD_FILE_BYTE_LIMIT = 8388608
COPYPASTA_JSON_INDENT_AMOUNT = 2
