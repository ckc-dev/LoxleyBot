"""Contains cogs used in guild management."""

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

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """
        Kick a user from the guild.

        Args:
            ctx (discord.ext.commands.Context): Context passed to function.
            member (discord.Member): Discord user to be kicked from guild.
            reason (str, optional): Reason why the user is being kicked.
                Defaults to None.
        """
        await member.kick(reason=reason)
        await ctx.send(functions.get_localized_message(
            ctx.guild.id, "KICK_MESSAGE").format(member.mention, reason))
        await member.send(functions.get_localized_message(
            ctx.guild.id, "KICK_MESSAGE_PRIVATE").format(ctx.guild, reason))

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """
        Ban a user from the guild.

        Args:
            ctx (discord.ext.commands.Context): Context passed to function.
            member (discord.Member): Discord user to be banned from guild.
            reason (str, optional): Reason why the user is being banned.
                Defaults to None.
        """
        await member.ban(reason=reason)
        await ctx.send(functions.get_localized_message(
            ctx.guild.id, "BAN_MESSAGE").format(member.mention, reason))
        await member.send(functions.get_localized_message(
            ctx.guild.id, "BAN_MESSAGE_PRIVATE").format(ctx.guild, reason))

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


class MassManagement(commands.Cog, name="Mass Management"):
    """Mass management cog. Contains functions used in guild management."""

    def __init__(self, bot):
        """
        Initialize cog.

        Args:
            bot (discord.ext.commands.Bot): Bot to use with cog.
        """
        self.bot = bot
        self.management = self.bot.get_cog("Management")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def masskick(self, ctx, *members: discord.Member):
        """
        Kick multiple users at once.

        Does not take a reason as an argument, and a default message is sent.

        Args:
            ctx (discord.ext.commands.Context): Context passed to function.
            members (List[discord.Member]): Members to kick from guild.
        """
        for member in members:
            await self.management.kick(ctx,
                                       member,
                                       reason=functions.get_localized_message(
                                           ctx.guild.id, "MASSKICK_MESSAGE"))

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def massban(self, ctx, *members: discord.Member):
        """
        Ban multiple users at once.

        Does not take a reason as an argument, and a default message is sent.

        Args:
            ctx (discord.ext.commands.Context): Context passed to function.
            members (List[discord.Member]): Members to ban from guild.
        """
        for member in members:
            await self.management.ban(ctx,
                                      member,
                                      reason=functions.get_localized_message(
                                          ctx.guild.id, "MASSBAN_MESSAGE"))


def setup(bot):
    """
    Bind cogs to the bot.

    Args:
        bot (discord.ext.commands.Bot): Bot to bind cogs to.
    """
    bot.add_cog(Management(bot))
    bot.add_cog(MassManagement(bot))
