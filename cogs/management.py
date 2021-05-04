"""Contains cogs used in guild management."""

import re

import discord
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
            reason = functions.get_localized_message(
                ctx.guild.id, "BAN_DEFAULT_REASON")
            message = functions.get_localized_message(
                ctx.guild.id, "BAN_MESSAGE")
            private_message = functions.get_localized_message(
                ctx.guild.id, "BAN_MESSAGE_PRIVATE")
        else:
            reason = functions.get_localized_message(
                ctx.guild.id, "KICK_DEFAULT_REASON")
            message = functions.get_localized_message(
                ctx.guild.id, "KICK_MESSAGE")
            private_message = functions.get_localized_message(
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
        Kick one or more users from the guild.

        If no reason is specified, a default reason is provided. Reason must be
        between either single (') or double (") quotes. Users must be separated
        by spaces and if a user name contains spaces, it must also be between
        either single (') or double (") quotes.

        Args:
            arguments (str): Arguments passed to command.

        Usage:
            kick [{-r|--reason} "<reason>"] <members>

        Examples:
            kick @example_user:
                Kick "example_user" by mention, providing a default reason.
            kick "Example User":
                Kick a user with spaces in their name, "Example user",
                providing a default reason.
            kick -r "For having a long username." example_user#1234:
                Kick a user by name#discriminator,
                providing the reason "For having a long username."
            kick @user1 "User 2" user#0003:
                Kick three users by mention, name, and name#discriminator,
                providing a default reason.
        """
        if not arguments:
            await ctx.send(functions.get_localized_message(
                ctx.guild.id, "KICK_INVALID_ARGUMENT"))
        else:
            await self.kick_members(ctx, arguments)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, *, arguments=None):
        """
        Ban one or more users from the guild.

        If no reason is specified, a default reason is provided. Reason must be
        between either single (') or double (") quotes. Users must be separated
        by spaces and if a user name contains spaces, it must also be between
        either single (') or double (") quotes.

        Args:
            arguments (str): Arguments passed to command.

        Usage:
            ban [{-r|--reason} "<reason>"] <members>

        Examples:
            ban @example_user:
                ban "example_user" by mention, providing a default reason.
            ban "Example User":
                ban a user with spaces in their name, "Example user",
                providing a default reason.
            ban -r "For having a long username." example_user#1234:
                ban a user by name#discriminator,
                providing the reason "For having a long username."
            ban @user1 "User 2" user#0003:
                ban three users by mention, name, and name#discriminator,
                providing a default reason.
        """
        if not arguments:
            await ctx.send(functions.get_localized_message(
                ctx.guild.id, "BAN_INVALID_ARGUMENT"))
        else:
            await self.kick_members(ctx, arguments, True)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        """
        Remove a user from the guild banlist.

        Args:
            ctx (discord.ext.commands.Context): Context passed to function.
            member (str): Discord user to be kicked from guild. Must be
                a name and discriminator. E.g.: "User#1234"
        """
        for ban in await ctx.guild.bans():
            if [ban.user.name, ban.user.discriminator] == member.split("#"):
                await ctx.guild.unban(ban.user)
                await ctx.send(functions.get_localized_message(
                    ctx.guild.id, "UNBAN_MESSAGE").format(
                        ban.user.name, ban.user.discriminator))
                break


def setup(bot):
    """
    Bind cogs to the bot.

    Args:
        bot (discord.ext.commands.Bot): Bot to bind cogs to.
    """
    bot.add_cog(Management(bot))
