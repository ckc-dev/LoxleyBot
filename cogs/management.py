"""Contains cogs used in server management."""

import discord
from discord.ext import commands


class Management(commands.Cog):
    """Management cog. Contains functions used in server management."""

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
        Kick a user from the server.

        Args:
            ctx (discord.ext.commands.Context): Context passed to function.
            member (discord.Member): Discord user to be kicked from server.
            reason (str, optional): Reason why the user is being kicked.
                Defaults to None.
        """
        await member.kick(reason=reason)
        await ctx.send(f"Kicked {member.mention}. Reason: `{reason}`.")
        await member.send(f"You have been kicked from `{ctx.guild}`. Reason: `{reason}`.")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """
        Ban a user from the server.

        Args:
            ctx (discord.ext.commands.Context): Context passed to function.
            member (discord.Member): Discord user to be banned from server.
            reason (str, optional): Reason why the user is being banned.
                Defaults to None.
        """
        await member.ban(reason=reason)
        await ctx.send(f"Banned {member.mention}. Reason: `{reason}`.")
        await member.send(f"You have been banned from `{ctx.guild}`. Reason: `{reason}`.")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        """
        Remove a user from the server banlist.

        Args:
            ctx (discord.ext.commands.Context): Context passed to function.
            member (str): Discord user to be kicked from server. Must be
                a name and discriminator. E.g.: "User#1234"
        """
        for ban in await ctx.guild.bans():
            if [ban.user.name, ban.user.discriminator] == member.split("#"):
                await ctx.guild.unban(ban.user)
                await ctx.send(f"Unbanned {ban.user.name}#{ban.user.discriminator}.")
                break


class MassManagement(commands.Cog, name="Mass Management"):
    """Mass management cog. Contains functions used in server management."""

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

        Does not take a reason as an argument,
        following reason is given:
            "Kicked in a mass kick. No specific reason provided.".

        Args:
            ctx (discord.ext.commands.Context): Context passed to function.
            members (List[discord.Member]): Members to kick from server.
        """
        for member in members:
            await self.management.kick(ctx, member, reason="Kicked in a mass kick. No specific reason provided.")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def massban(self, ctx, *members: discord.Member):
        """
        Ban multiple users at once.

        Does not take a reason as an argument,
        following reason is given:
            "Banned in a mass ban. No specific reason provided.".

        Args:
            ctx (discord.ext.commands.Context): Context passed to function.
            members (List[discord.Member]): Members to ban from server.
        """
        for member in members:
            await self.management.ban(ctx, member, reason="Banned in a mass ban. No specific reason provided.")


def setup(bot):
    """
    Bind cogs to the bot.

    Args:
        bot (discord.ext.commands.Bot): Bot to bind cogs to.
    """
    bot.add_cog(Management(bot))
    bot.add_cog(MassManagement(bot))
