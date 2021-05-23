"""Contains cogs used in guild management."""

import discord
import functions
import regexes
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
            arguments (str): Arguments passed to function.
            ban (bool, optional): Whether or not to ban members, instead of
                just kicking them. Defaults to False.
        """
        message_reference = ctx.message.reference

        if not arguments and not message_reference:
            await ctx.send(functions.get_localized_object(
                ctx.guild.id, "BAN_INVALID_ARGUMENT"
                              if ban else "KICK_INVALID_ARGUMENT"))
            return

        members = []
        reason = functions.get_localized_object(
            ctx.guild.id, "BAN_DEFAULT_REASON"
                          if ban else "KICK_DEFAULT_REASON")
        message = functions.get_localized_object(
            ctx.guild.id, "BAN_MESSAGE"
                          if ban else "KICK_MESSAGE")
        direct_message = functions.get_localized_object(
            ctx.guild.id, "BAN_MESSAGE_DIRECT"
                          if ban else "KICK_MESSAGE_DIRECT")

        if arguments:
            match_reason = regexes.REASON.search(arguments)

            if match_reason:
                reason = match_reason.group("reason")
                arguments = regexes.REASON.sub("", arguments)

            members.extend(
                i[0] + i[1]
                for i in regexes.STRINGS_BETWEEN_SPACES.findall(arguments))

        if message_reference:
            members.append(str(message_reference.resolved.author.id))

        for member in members:
            try:
                member = await commands.MemberConverter().convert(ctx, member)

                if ban:
                    await member.ban(reason=reason)
                else:
                    await member.kick(reason=reason)

                await ctx.send(message.format(member.mention, reason))

                # Catch exception in case member has disabled non-friend DMs.
                try:
                    await member.send(direct_message.format(ctx.guild, reason))
                except discord.HTTPException:
                    pass
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
            arguments (str): Arguments passed to command. Defaults to None.

        Usage:
            kick [{-r|--reason} "<reason>"] <members>
            kick (referencing/replying a message) [{-r|--reason} "<reason>"]
                                                  [<members>]

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
            kick (referencing/replying a message):
                Kick the author of the referenced message,
                providing a default reason.
            kick @member1 "Member 2" (referencing/replying a message):
                Kick the author of the referenced message and two more members,
                providing a default reason.
        """
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
            arguments (str): Arguments passed to command. Defaults to None.

        Usage:
            ban [{-r|--reason} "<reason>"] <members>
            ban (referencing/replying a message) [{-r|--reason} "<reason>"]
                                                 [<members>]

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
            ban (referencing/replying a message):
                Ban the author of the referenced message,
                providing a default reason.
            ban @member1 "Member 2" (referencing/replying a message):
                Ban the author of referenced message and two more members,
                providing a default reason.
        """
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
        users = [i[0] + i[1] for i in regexes.DISCORD_USER.findall(users)]

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
