"""Regular expressions used throughout the bot."""

import re

# PARAMETERS:
# RegExes used to match parameters (or flags) passed to bot commands.
#
# "Optional" parameters should be used when a flag can be omitted when passing
# the parameter. E.g.: Using an optional --id parameter should yield the same
# results in the following cases:
#   command 10
#   command -i 10
#   command --id 10
# A non-optional --id parameter, however, will only match when the flag
# {-i|--id} is passed.
#
# "Optional value" parameters should be used when the flag is required, but a
# default value is used if no value is specified. E.g.: Using an optional value
# --set-channel parameter should yield the same results in the following cases:
#   command -sc
#   command --set-channel default_channel
#
# "Independent" parameters are used by themselves, without any value. E.g.:
# Using an independent --none parameter means the string should simply contain
# "--none" in it.
#
# "Verbose" parameters can only be used in a verbose manner.

ADD_OPTIONAL_VALUE = re.compile(r"""
    (?:-a|--add)    # Match either "-a" or "--add".
    \s*             # Match between 0 and ∞ whitespace characters.
    (.+)?           # CAPTURE GROUP | Match any character between
                    # 1 and ∞ times, either 0 or 1 times""",
                                flags=re.IGNORECASE | re.VERBOSE | re.DOTALL)

ALL_INDEPENDENT = re.compile(r"""
    (?:-a|--all)    # Match either "-a" or "--all".
    \b              # Match word boundary.""",
                             flags=re.IGNORECASE | re.VERBOSE)

COPYPASTA_LIST_ARRANGEMENT = re.compile(r"""
    (?P<arrangement>    # CAPTURE GROUP (arrangement) | Open capture group.
        -a|--ascending  # Match either "-a" or "--ascending".
        |               # OR
        -d|--descending # Match either "-d" or "--descending".
    )                   # Close capture group (arrangement).
    \b                  # Match word boundary.""",
                                        flags=re.IGNORECASE | re.VERBOSE)

COPYPASTA_LIST_DATABASE_FIELDS = re.compile(r"""
    (?P<field>          # CAPTURE GROUP (field) | Open capture group.
        -i|--id         # Match either "-i" or "--id".
        |               # OR
        -t|--title      # Match either "-t" or "--title".
        |               # OR
        -c|--content    # Match either "-c" or "--content".
        |               # OR
        --count         # Match "count".
    )                   # Close capture group (field).
    \b                  # Match word boundary.""",
                                            flags=re.IGNORECASE | re.VERBOSE)

DELETE = re.compile(r"""
    (?:-d|--delete) # Match either "-d" or "--delete".
    \s*             # Match between 0 and ∞ whitespace characters.
    (?P<ids>        # CAPTURE GROUP (ids) | Open capture group.
        \d+         # Match between 1 and ∞ digits.
        (?:         # Open non-capturing group.
            \s*     # Match between 0 and ∞ whitespace characters.
            ,       # Match ",".
            \s*     # Match between 0 and ∞ whitespace characters.
            \d+     # Match between 1 and ∞ digits.
        )*          # Close non-capturing group, match between 0 and ∞ times.
    )               # Close capture group (id).""",
                    flags=re.IGNORECASE | re.VERBOSE)

EXPORT_INDEPENDENT = re.compile(r"""
    (?:-e|--export) # Match either "-e" or "--export".
    \b              # Match word boundary.""",
                                flags=re.IGNORECASE | re.VERBOSE)

ID = re.compile(r"""
    (?:-i|--id) # Match either "-i" or "--id".
    \s*         # Match between 0 and ∞ whitespace characters.
    (?P<id>\d+) # CAPTURE GROUP (id) | Match between 1 and ∞ digits.""",
                flags=re.IGNORECASE | re.VERBOSE)

ID_OPTIONAL = re.compile(r"""
    (?:-i|--id)?    # Match either "-i" or "--id", either 0 or 1 times.
    \s*             # Match between 0 and ∞ whitespace characters.
    (?P<id>\d+)     # CAPTURE GROUP (id) | Match between 1 and ∞ digits.""",
                         flags=re.IGNORECASE | re.VERBOSE)

IMPORT_INDEPENDENT_VERBOSE = re.compile(r"""
    --import    # Match "--import".
    \b          # Match word boundary.""",
                                        flags=re.IGNORECASE | re.VERBOSE)

LIMIT_OPTIONAL = re.compile(r"""
    (?:-l|--limit)? # Match either "-l" or "--limit", either 0 or 1 times.
    \s*             # Match between 0 and ∞ whitespace characters.
    (?P<limit>\d+)  # CAPTURE GROUP (limit) | Match between 1 and ∞ digits.""",
                            flags=re.IGNORECASE | re.VERBOSE)

LIST_INDEPENDENT = re.compile(r"""
    (?:-l|--list)   # Match either "-l" or "--list".
    \b              # Match word boundary.""",
                              flags=re.IGNORECASE | re.VERBOSE)

NONE_INDEPENDENT = re.compile(r"""
    (?:-n|--none)   # Match either "-n" or "--none".
    \b              # Match word boundary.""",
                              flags=re.IGNORECASE | re.VERBOSE)

REASON = re.compile(r"""
    (?:-r|--reason) # Match either "-r" or "--reason".
    \s*             # Match between 0 and ∞ whitespace characters.
    ['\"]           # Match either "'" or '"'.
    (?P<reason>.+?) # CAPTURE GROUP (reason) | Match any character
                    # between 1 and ∞ times, as few times as possible.
    ['\"]           # Match either "'" or '"'.""",
                    flags=re.IGNORECASE | re.VERBOSE)

SEARCH = re.compile(r"""
    (?:-s|--search) # Match either "-s" or "--search".
    \s*             # Match between 0 and ∞ whitespace characters.
    (?P<query>.+)   # CAPTURE GROUP (query) | Match any character
                    # between 1 and ∞ times.""",
                    flags=re.IGNORECASE | re.VERBOSE)

SET_CHANNEL_OPTIONAL_VALUE = re.compile(r"""
    (?:-sc|--set-channel)   # Match either "-sc" or "--set-channel".
    \s*                     # Match between 0 and ∞ whitespace characters.
    (?P<channel>.+)?        # CAPTURE GROUP (channel) | Match any character
                            # between 1 and ∞ times.""",
                                        flags=re.IGNORECASE | re.VERBOSE)

TITLE_OPTIONAL = re.compile(r"""
    (?:-t|--title)? # Match either "-t" or "--title", either 0 or 1 times.
    \s*             # Match between 0 and ∞ whitespace characters.
    (?P<title>.+)   # CAPTURE GROUP (title) | Match any character between
                    # 1 and ∞ times.""",
                            flags=re.IGNORECASE | re.VERBOSE)

# GENERAL USE:
# RegExes that are not parameters, but have more general use cases.

# RegEx based on restrictions described in Discord's documentation. Source:
# https://discord.com/developers/docs/resources/user#usernames-and-nicknames
DISCORD_USER = re.compile(r"""
    (?:                     # Open non-capturing group.
        ['\"]               # Match either "'" or '"'.
        (                   # CAPTURE GROUP (1) | Open capture group.
            [^#@:]{2,32}    # Match any character that is not a "#", "@" or
                            # ":", between 2 and 32 times.
            \#              # Match "#".
            \d{4}           # Match any digit, exactly 4 times.
        )                   # Close capture group (1).
        ['\"]               # Match either "'" or '"'.
        |                   # OR
        (                   # CAPTURE GROUP (2) | Open capture group.
            [^#@:\s]{2,32}  # Match any character that is not a "#", "@", ":",
                            # or a whitespace character between 2 and 32 times.
            \#              # Match "#".
            \d{4}           # Match any digit, exactly 4 times.
        )                   # Close capture group (2).
    )                       # Close non-capturing group.""",
                          flags=re.IGNORECASE | re.VERBOSE)

FIRST_FEW_WORDS = re.compile(r"""
    (               # CAPTURE GROUP (1) | Open capture group.
        \S          # Match any non-whitespace character.
        .{4,64}?    # Match any character between 4 and 64 times,
                    # as few times as possible.
        \.          # Match ".".
        |           # OR
        \S          # Match any non-whitespace character.
        .{4,64}     # Match any character between 4 and 64 times,
                    # as few times as possible.
        \S          # Match any non-whitespace character.
        \b          # Match a word boundary.
        |           # OR
        \S+         # Match any non-whitespace character between 1 and ∞ times.
    )               # Close capture group (1).""",
                             flags=re.IGNORECASE | re.VERBOSE)

MARCO = re.compile(r"""
    (?P<m>m+)               # CAPTURE GROUP (m) | Match between 1 and ∞ "m".
    (?P<a>a+)               # CAPTURE GROUP (a) | Match between 1 and ∞ "a".
    (?P<r>r+)               # CAPTURE GROUP (r) | Match between 1 and ∞ "r".
    (?P<c>c+)               # CAPTURE GROUP (c) | Match between 1 and ∞ "c".
    (?P<o>o+)               # CAPTURE GROUP (o) | Match between 1 and ∞ "o".
    (?P<punctuation>\W*)    # CAPTURE GROUP (punctuation) | Match between 0
                            # and ∞ of ".", "…", "?", "!", or any
                            # whitespace character.""",
                   flags=re.IGNORECASE | re.VERBOSE)

STRINGS_BETWEEN_SPACES = re.compile(r"""
    (?:         # Open non-capturing group.
        ['\"]   # Match either "'" or '"'.
        (.+?)   # CAPTURE GROUP | Match any character between 1 and ∞
                # times, as few times as possible.
        ['\"]   # Match either "'" or '"'.
        |       # OR
        (\S+)   # CAPTURE GROUP | Match any non-whitespace character
                # between 1 and ∞ times, as few times as possible.
    )           # Close non-capturing group.""",
                                    flags=re.IGNORECASE | re.VERBOSE)

TITLE_AND_CONTENT = re.compile(r"""
    (?:                     # Open non-capturing group.
        (?:                 # Open non-capturing group.
            ['\"]           # Match either "'" or '"'.
            (?P<title>.+)   # CAPTURE GROUP (title) | Match any character
                            # between 1 and ∞ times.
            ['\"]           # Match either "'" or '"'.
        )?                  # Close-non-capturing group. Match it either
                            # 0 or 1 times.
        \s*                 # Match between 0 and ∞ whitespace characters.
        ['\"]               # Match either "'" or '"'.
        (?P<content>.+)     # CAPTURE GROUP (content) | Match any character
                            # between 1 and ∞ times.
        ['\"]               # Match either "'" or '"'.
    )                       # Close-non-capturing group.
    |                       # OR
    (?P<content_2>.+)       # CAPTURE GROUP (content_2) | Match any character
                            # between 1 and ∞ times.""",
                               flags=re.IGNORECASE | re.VERBOSE | re.DOTALL)
