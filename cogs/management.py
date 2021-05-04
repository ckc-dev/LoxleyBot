"""Contains cogs used in guild management."""

import re

import functions
from discord.ext import commands


class Management(commands.Cog):
    """Management cog. Contains functions used in guild management."""

    def __init__(self, bot):
        """
        Initialize cog.

        Args:
            bot (discord.ext.commands.Bot): Bot to use with cog.
        """
        self.bot = bot

    async def kick_members(self, ctx, arguments, ban=False):
        """
        Kick or ban one or more members from guild.

        Args:
            ctx (discord.ext.commands.Context): Context passed to function.
            arguments (str): Arguments passed to either kick or ban commands.
            ban (bool, optional): Whether or not to ban members, instead of
                just kicking them. Defaults to False.
        """
        REGEX_REASON = re.compile(r"""
            (?:-r|--reason) # Match either "-r" or "--reason".
            \s*             # Match between 0 and ∞ whitespace characters.
            ['\"]           # Match either "'" or '"'.
            (?P<reason>.+?) # CAPTURE GROUP (reason) | Match any character
                            # between 1 and ∞ times, as few times as possible.
            ['\"]           # Match either "'" or '"'.""",
                                  flags=re.IGNORECASE | re.VERBOSE)

        REGEX_MEMBERS = re.compile(r"""
            \s*         # Match between 0 and ∞ whitespace characters.
            (?:         # Open non-capturing group.
                ['\"]   # Match either "'" or '"'.
                (.+?)   # CAPTURE GROUP | Match any character between 1 and ∞
                        # times, as few times as possible.
                ['\"]   # Match either "'" or '"'.
                |       # OR
                (\S+)   # CAPTURE GROUP | Match any non-whitespace character
                        # between 1 and ∞ times, as few times as possible.
            )           # Close non-capturing group
            \s*         # Match between 0 and ∞ whitespace characters.""",
                                   flags=re.IGNORECASE | re.VERBOSE)

        if ban:
            reason = functions.get_localized_object(
                ctx.guild.id, "BAN_DEFAULT_REASON")
            message = functions.get_localized_object(
                ctx.guild.id, "BAN_MESSAGE")
            private_message = functions.get_localized_object(
                ctx.guild.id, "BAN_MESSAGE_PRIVATE")
        else:
            reason = functions.get_localized_object(
                ctx.guild.id, "KICK_DEFAULT_REASON")
            message = functions.get_localized_object(
                ctx.guild.id, "KICK_MESSAGE")
            private_message = functions.get_localized_object(
                ctx.guild.id, "KICK_MESSAGE_PRIVATE")

        match_reason = REGEX_REASON.search(arguments)

        if match_reason:
            reason = match_reason.group("reason")
            arguments = REGEX_REASON.sub("", arguments)

        members = [i[0] + i[1] for i in REGEX_MEMBERS.findall(arguments)]

        for member in members:
            try:
                member = await commands.MemberConverter().convert(ctx, member)

                if ban:
                    await member.ban(reason=reason)
                else:
                    await member.kick(reason=reason)

                await ctx.send(message.format(member.mention, reason))
                await member.send(private_message.format(ctx.guild, reason))
            except commands.MemberNotFound:
                pass

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, *, arguments=None):
        """
        Kick one or more members from the guild.

        If no reason is specified, a default reason is provided. Reason must be
        between either single (') or double (") quotes. Members must be
        separated by spaces and if a member name contains spaces, it must also
        be between either single (') or double (") quotes.

        Args:
            arguments (str): Arguments passed to command.

        Usage:
            kick [{-r|--reason} "<reason>"] <members>

        Examples:
            kick @example_member:
                Kick "example_member" by mention, providing a default reason.
            kick "Example Member":
                Kick a member with spaces in their name, "Example member",
                providing a default reason.
            kick -r "For having a long username." example_member#1234:
                Kick a member by name#discriminator,
                providing the reason "For having a long username."
            kick @member1 "Member 2" member#0003:
                Kick three members by mention, name, and name#discriminator,
                providing a default reason.
        """
        if not arguments:
            await ctx.send(functions.get_localized_object(
                ctx.guild.id, "KICK_INVALID_ARGUMENT"))
        else:
            await self.kick_members(ctx, arguments)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, *, arguments=None):
        """
        Ban one or more members from the guild.

        If no reason is specified, a default reason is provided. Reason must be
        between either single (') or double (") quotes. Members must be
        separated by spaces and if a member name contains spaces, it must also
        be between either single (') or double (") quotes.

        Args:
            arguments (str): Arguments passed to command.

        Usage:
            ban [{-r|--reason} "<reason>"] <members>

        Examples:
            ban @example_member:
                Ban "example_member" by mention, providing a default reason.
            ban "Example Member":
                Ban a member with spaces in their name, "Example member",
                providing a default reason.
            ban -r "For having a long username." example_member#1234:
                Ban a member by name#discriminator,
                providing the reason "For having a long username."
            ban @member1 "Member 2" member#0003:
                Ban three members by mention, name, and name#discriminator,
                providing a default reason.
        """
        if not arguments:
            await ctx.send(functions.get_localized_object(
                ctx.guild.id, "BAN_INVALID_ARGUMENT"))
        else:
            await self.kick_members(ctx, arguments, True)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, users):
        """
        Remove one or more users from the guild banlist.

        Users must be formatted as "username#discriminator". Users must be
        separated by spaces and if a user name contains spaces, it must be
        between either single (') or double (") quotes.

        Args:
            users (str): String containing users to remove from guild banlist.

        Usage:
            unban <users>

        Examples:
            unban example_user#1234:
                Unban "example_user".
            unban "Example User#1234":
                Unban a user with spaces in their name, "Example user".
            unban user#0001 "Example User#0002" user#0003:
                Unban three users.
        """
        REGEX_USERS = re.compile(r"""
            \s*         # Match between 0 and ∞ whitespace characters.
            (?:         # Open non-capturing group.
                ['\"]   # Match either "'" or '"'.
                (.+?\#\d+)
                ['\"]   # Match either "'" or '"'.
                |       # OR
                (\S+\#\d+)
            )           # Close non-capturing group
            \s*         # Match between 0 and ∞ whitespace characters.""",
                                 flags=re.IGNORECASE | re.VERBOSE)

        users = [i[0] + i[1] for i in REGEX_USERS.findall(users)]

        for ban in await ctx.guild.bans():
            for user in users:
                if [ban.user.name, ban.user.discriminator] == user.split("#"):
                    await ctx.guild.unban(ban.user)
                    await ctx.send(functions.get_localized_object(
                        ctx.guild.id, "UNBAN_MESSAGE").format(
                            ban.user.name, ban.user.discriminator))


def setup(bot):
    """
    Bind cogs to the bot.

    Args:
        bot (discord.ext.commands.Bot): Bot to bind cogs to.
    """
    bot.add_cog(Management(bot))
