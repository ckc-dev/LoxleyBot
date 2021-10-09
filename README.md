# [Meet Loxley](https://github.com/ckc-dev/LoxleyBot)

![Icon](README/icon.png) ![Logo](README/logo.png)

Loxley is a Discord bot that I made just for fun using [discord.py](https://github.com/Rapptz/discord.py). Some friends and I wanted a bot with specific functions and requirements (e.g.: Being open source) for our guild, and we couldn't find any that had everything we wanted and nothing we didn't want, so I just decided to make one myself. It may or may not have features you're interested in, so feel free to deploy your own instance and try it out!

## Technologies used

- JSON
- Python
- RegEx
- SQL

## Table of contents

- [Meet Loxley](#meet-loxley)
  - [Technologies used](#technologies-used)
  - [Table of contents](#table-of-contents)
  - [File tree](#file-tree)
- [Available commands](#available-commands)
- [Other functions](#other-functions)
- [Deploying your own instance](#deploying-your-own-instance)
  - [Create a bot and get its token](#create-a-bot-and-get-its-token)
  - [Clone this repository and install dependencies](#clone-this-repository-and-install-dependencies)
  - [Provide the environment variables](#provide-the-environment-variables)
  - [Provide the required intents](#provide-the-required-intents)
  - [Provide the required permissions](#provide-the-required-permissions)
  - [Run the bot](#run-the-bot)
- [Configuring Loxley to your guild](#configuring-loxley-to-your-guild)
- [Command usage](#command-usage)
- [Contributing](#contributing)

## File tree

```
LoxleyBot
├ .gitignore          Files/directories ignored by git.
├ bot.py              Main bot file.
├ cogs/               Files containing different collections of commands.
│ ├ entertainment.py  Cogs used for functions related to fun and entertainment.
│ ├ management.py     Cogs used in guild management.
│ └ utils.py          Cogs used for useful, often small and simple functions.
├ functions.py        General use functions used in other parts of the bot.
├ LICENSE             Project license.
├ localization.json   Localized bot messages.
├ Pipfile             Requirements.
├ Pipfile.lock        Requirements.
├ Procfile            A list of processes executed at app startup. Used on deployment.
├ README/             Files used in the README.
│ ├ icon.png          Image used in the README.
│ └ logo.png          Image used in the README.
├ README.md           Project README.
├ regexes.py          Regular expressions used throughout the bot.
└ settings.py         Bot settings.
```

# Available commands

These are the currently available commands and their respective functions. A list containing detailed descriptions and usage examples is also available [later in this document](#command-usage).

- `about`: Get more information about the bot.
- `birthday`: Manage birthdays.
- `copypasta`: Manage and send copypastas.
- `count`: Count number of messages sent to a channel up to a specified message.
- `help`: Send a help message.
- `locale`: Change guild locale.
- `logging`: Set a text channel for logging deleted messages.
- `ping`: Get bot latency.
- `prefix`: Change the guild prefix.
- `purge`: Delete an amount of messages from a channel.
- `timezone`: Change guild timezone.
- `kick`: Kick one or more members from the guild.
- `ban`: Ban one or more members from the guild.
- `unban`: Remove one or more users from the guild banlist.

Of course, if you want to deploy your own instance, feel free to modify and create your own commands.

# Other functions

In addition to the commands, the bot will also play Marco Polo when some form of "Marco" is sent to a text channel it can read and send messages on. Furthermore, it will also respond with a help message when mentioned in a message, which is useful in case someone forgets which prefix to use in commands.

# Deploying your own instance

## Create a bot and get its token

First, create an application in the Discord Developer Portal, then, under the bot settings, create a bot and take note of its token.

## Clone this repository and install dependencies

1. On the terminal, run `git clone https://github.com/ckc-dev/LoxleyBot` to clone this repository.
2. Run `cd LoxleyBot` to change the current directory into the cloned repository directory.
3. - If `pipenv` is installed: run `pipenv install` to install the dependencies.
   - If `pipenv` is not installed: either install `pipenv` and then run `pipenv install`, or manually install the dependencies listed in the Pipfile using `pip`.

## Provide the environment variables

Make sure you have provided the required `BOT_TOKEN` environment variable, containing your token found in the Discord Developer Portal. If you are using a PostgreSQL database, be sure to also provide the `DATABASE_URL` environment variable, containing the URL to your database.

This can be done either by using a `.env` file or by setting the variables directly.

## Provide the required intents

Make sure to have the "Server Members" privileged gateway intent activated in the Discord Developer Portal, as this is required for some of the bot's functions, such as deleting the data related to a member when the member leaves the guild.

## Provide the required permissions

Here is a list containing each command and the permissions required for it to function properly. Be sure to enable the required permissions for commands you want to use:

- Every command
  - Send Messages
  - View Channels
- `copypasta`
  - Attach Files
  - Embed Links
- `count`
  - Read Message History
- `logging`
  - Embed Links
- `purge`
  - Manage Messages
  - Read Message History
- `kick`
  - Kick Members
- `ban`
  - Ban Members
- `unban`
  - Ban Members

## Run the bot

On the terminal, run `python bot.py` to run the bot.

# Configuring Loxley to your guild

Once you have deployed your own instance and invited the bot to join your guild, be sure to configure the guild's prefix, timezone and locale, as these are used in many functions throughout the bot, such as checking for birthdays. Optionally, also configure the guild's birthday, copypasta, and logging channels.

# Command usage

- `about`: Get more information about the bot.
  - Usage:
    - `about`
  - Examples:
    - `about`
      - Get more information about the bot.
- `birthday`: Manage birthdays.
  - Usage:
    - `birthday {-sc|--set-channel} [<channel>|-n|--none]`
    - `birthday {-n|--none}`
    - `birthday <date>`
  - Examples:
    - `birthday -sc`
      - Set birthday announcement channel to channel on which command was used.
    - `birthday -sc #announcements`
      - Set birthday announcement channel to #announcements.
    - `birthday -n`
      - Delete birthday information.
    - `birthday 30/01/2000`
      - Save birthday information as January 30, given the guild uses a DD/MM/YYY date format.
- `copypasta`: Manage and send copypastas.
  - Usage:
    - `copypasta`
    - `copypasta [{-i|--id}] <copypasta ID>`
    - `copypasta [{-t|--title}] <copypasta title>`
    - `copypasta {-s|--search} <search query>`
    - `copypasta {-a|--add} ["<copypasta title>"] "<copypasta content>"`
    - `copypasta {-a|--add} ["<copypasta title>"] (referencing/replying a message)`
    - `copypasta {-d|--delete} <copypasta ID>`
    - `copypasta {-l|--list} [{-a|--ascending|-d|--descending}] [{-i|--id|-t|--title|-c|--content|--count}]`
    - `copypasta {-sc|--set-channel} [<channel>|-n|--none]`
    - `copypasta {-e|--export}`
    - `copypasta {--import} (embedding a file to the message)`
    - `copypasta {-b|--ban} <members>`
    - `copypasta {-u|--unban} <members>`
  - Examples:
    - `copypasta`
      - Send a random copypasta.
    - `copypasta 10`
      - Send copypasta with ID 10.
    - `copypasta example`
      - Send copypasta which contains "example" in its title.
    - `copypasta -s example query`
      - Search for "example query" in copypastas title and content.
    - `copypasta -a "Content"`
      - Add "Content" as a copypasta, which will have its title generated automatically.
    - `copypasta -a "Title" "Content"`
      - Add "Content" as a copypasta titled "Title".
    - `copypasta -a (referencing/replying a message)`
      - Add referenced message as a copypasta, which will have its title generated automatically.
    - `copypasta -a (referencing/replying a message) "Title"`
      - Add referenced message as a copypasta titled "Title".
    - `copypasta -d 8`
      - Delete copypasta with ID 8.
    - `copypasta -d 1, 2, 3`
      - Delete copypastas with IDs 1, 2, and 3.
    - `copypasta -l`
      - List all copypastas.
    - `copypasta -l -t -a`
      - List all copypastas, sorted by title, in ascending order.
    - `copypasta -sc`
      - Set copypasta channel to channel on which command was used.
    - `copypasta -sc #copypastas`
      - Set copypasta channel to #copypastas.
    - `copypasta -e`
      - Export copypasta list to a .JSON file.
    - `copypasta --import`
      - Import an exported .JSON file containing a copypasta list.
    - `copypasta -b @example_member`
      - Ban "example_member" from adding copypastas, by mention.
    - `copypasta -u @member1 "Member 2" member#0003`
      - Unban three members from adding copypastas, by mention, name, and name#discriminator.
- `count`: Count number of messages sent to a channel up to a specified message.
  - Usage:
    - `count [{-a|--all}]`
    - `count [{-i|--id}] <message ID>`
    - `count (referencing/replying a message)`
  - Examples:
    - `count`
      - Count all messages.
    - `count 838498717459415081`
      - Count all messages up to message with ID "838498717459415081".
    - `count (referencing/replying a message)`
      - Count all messages up to referenced message.
- `help`: Send a help message.
  - Usage:
    - `help`
    - `help {category}`
    - `help {command}`
  - Examples:
    - `help`
      - Get a help message including small descriptions of available commands.
    - `help Utils`
      - Get a help message including descriptions of the "Utils" category and its available commands.
    - `help help`
      - Get a help message on the "help" command.
- `locale`: Change guild locale.
  - Usage:
    - `locale <new locale>`
  - Examples:
    - `locale en-US`
      - Change locale to "en-US".
    - `locale pt-BR`
      - Change locale to "pt-BR".
- `logging`: Set a text channel for logging deleted messages.
  - Usage:
    - `logging {-sc|--set-channel} [<channel>|-n|--none]`
  - Examples:
    - `logging -sc`
      - Set logging channel to channel on which command was used.
    - `logging -sc #log`
      - Set logging channel to #log.
- `ping`: Get bot latency.
  - Usage:
    - `ping`
  - Examples:
    - `ping`
      - Get bot latency.
- `prefix`: Change the guild prefix.
  - Usage:
    - `prefix <new prefix>`
  - Examples:
    - `prefix >>`
      - Change prefix to ">>".
    - `prefix ./`
      - Change prefix to "./".
- `purge`: Delete an amount of messages from a channel.
  - Usage:
    - `purge [{-l|--limit}] <limit>`
    - `purge {-i|--id} <message ID>`
    - `purge {-a|--all}`
    - `purge (referencing/replying a message)`
  - Examples:
    - `purge 10`
      - Delete the last 10 messages.
    - `purge -i 838498717459415081`
      - Delete all messages up to message with ID "838498717459415081".
    - `purge -a`
      - Delete all messages.
    - `purge (referencing/replying a message)`
      - Delete all messages up to referenced message.
- `timezone`: Change guild timezone.
  - Usage:
    - `timezone <new timezone>`
  - Examples:
    - `timezone -03:00`
      - Change timezone to -03:00.
    - `timezone +12:30`
      - Change timezone to +12:30.
- `kick`: Kick one or more members from the guild.
  - Usage:
    - `kick [{-r|--reason} "<reason>"] <members>`
    - `kick (referencing/replying a message) [{-r|--reason} "<reason>"] [<members>]`
  - Examples:
    - `kick @example_member`
      - Kick "example_member" by mention, providing a default reason.
    - `kick "Example Member"`
      - Kick a member with spaces in their name, "Example member", providing a default reason.
    - `kick -r "For having a long username." example_member#1234`
      - Kick a member by name#discriminator, providing the reason "For having a long username."
    - `kick @member1 "Member 2" member#0003`
      - Kick three members by mention, name, and name#discriminator, providing a default reason.
    - `kick (referencing/replying a message)`
      - Kick the author of the referenced message, providing a default reason.
    - `kick @member1 "Member 2" (referencing/replying a message)`
      - Kick the author of the referenced message and two more members, providing a default reason.
- `ban`: Ban one or more members from the guild.
  - Usage:
    - `ban [{-r|--reason} "<reason>"] <members>`
    - `ban (referencing/replying a message) [{-r|--reason} "<reason>"] [<members>]`
  - Examples:
    - `ban @example_member`
      - Ban "example_member" by mention, providing a default reason.
    - `ban "Example Member"`
      - Ban a member with spaces in their name, "Example member", providing a default reason.
    - `ban -r "For having a long username." example_member#1234`
      - Ban a member by name#discriminator, providing the reason "For having a long username."
    - `ban @member1 "Member 2" member#0003`
      - Ban three members by mention, name, and name#discriminator, providing a default reason.
    - `ban (referencing/replying a message)`
      - Ban the author of the referenced message, providing a default reason.
    - `ban @member1 "Member 2" (referencing/replying a message)`
      - Ban the author of referenced message and two more members, providing a default reason.
- `unban`: Remove one or more users from the guild banlist.
  - Usage:
    - `unban <users>`
    - `unban (referencing/replying a message) [<users>]`
  - Examples:
    - `unban example_user#1234`
      - Unban "example_user".
    - `unban "Example User#1234"`
      - Unban a user with spaces in their name, "Example user".
    - `unban user#0001 "Example User#0002" user#0003`
      - Unban three users.
    - `unban (referencing/replying a message) user#0001 user#0003`
      - Unban the author of referenced message and two more users.

# Contributing

Pull requests are welcome.

Please open an issue to discuss what you'd like to change before making major changes.

Please make sure to update and/or add appropriate tests when applicable.

This project is licensed under the [GPL-3.0 License](https://github.com/ckc-dev/LoxleyBot/blob/main/LICENSE).
