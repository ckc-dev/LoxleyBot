"""
Contains bot settings.
"""

# Import required modules.
import os
import sqlite3

import dotenv

# Load environment variables.
dotenv.load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_PREFIX = "./"
BOT_ACTIVITY = f"{BOT_PREFIX}help"
BOT_LOG_FILENAME = "bot.log"

DATABASE_NAME = "sqlite.db"
DATABASE_CONNECTION = sqlite3.connect(DATABASE_NAME)
