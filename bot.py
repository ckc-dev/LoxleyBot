# Import required modules.
import logging
import os

import discord
import dotenv

# Make sure bot token was provided.
dotenv.load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("'BOT_TOKEN' environment variable was not provided.")

# Set up logging.
LOGGER = logging.getLogger('discord')
HANDLER = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')
HANDLER.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(HANDLER)

# Initialize a client instance.
CLIENT = discord.Client()

# Once the bot is finished logging in and setting things up:
@CLIENT.event
async def on_ready():
    print("Hello, world!")

# Run bot.
CLIENT.run(TOKEN)
