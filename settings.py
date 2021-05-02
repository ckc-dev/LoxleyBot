"""Bot settings."""

import logging
import os
import sqlite3

import dotenv

# Load environment variables (such as bot token).
dotenv.load_dotenv()

# Values to use when initializing bot.
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_DEFAULT_PREFIX = "./"
BOT_DEFAULT_LOCALE = "en-US"
LOCALIZATION_FILE_NAME = "localization.json"
BOT_ACTIVITY = f"{BOT_DEFAULT_PREFIX}help"

# Values to use when seting up logging.
LOGGER = logging.getLogger("discord")
HANDLER = logging.FileHandler(filename="bot.log", encoding="utf-8", mode="w")
LOG_FORMAT = "%(asctime)s:%(levelname)s:%(name)s: %(message)s"
HANDLER.setFormatter(logging.Formatter(LOG_FORMAT))
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(HANDLER)

# Values to use when working with the database.
DATABASE_NAME = "sqlite.db"
DATABASE_CONNECTION = sqlite3.connect(DATABASE_NAME)


# Values to use when generating a list of copypastas.
DISCORD_CHARACTER_LIMIT = 2000
COPYPASTA_LIST_CHARACTERS_PER_ROW = 80
