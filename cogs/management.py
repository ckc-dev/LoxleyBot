"""
Contains cogs used in server management.
"""

# Import required modules.
import discord
from discord.ext import commands


class Management(commands.Cog):
    """
    Management cog. Contains functions used in server management.
    """

    # Initialize cog.
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """
        Kicks a user from the server.

        Args:
            ctx (discord.ext.commands.context.Context): Context passed to function.
            member (discord.Member): Discord user to be kicked from server.
            reason (str, optional): Reason why the user is being kicked. Defaults to None.
        """

        # Kick user from server.
        await member.kick(reason=reason)

        # Send a message warning user was kicked, both to channel command was run on and to kicked user.
        await ctx.send(f"Kicked {member.mention}. Reason: `{reason}`.")
        await member.send(f"You have been kicked from `{ctx.guild}`. Reason: `{reason}`.")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """
        Bans a user from the server.

        Args:
            ctx (discord.ext.commands.context.Context): Context passed to function.
            member (discord.Member): Discord user to be banned from server.
            reason (str, optional): Reason why the user is being banned. Defaults to None.
        """

        # Ban user from server.
        await member.ban(reason=reason)

        # Send a message warning user was banned, both to channel command was run on and to kicked user.
        await ctx.send(f"Banned {member.mention}. Reason: `{reason}`.")
        await member.send(f"You have been banned from `{ctx.guild}`. Reason: `{reason}`.")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        """
        Removes a user from the server banlist.

        Args:
            ctx (discord.ext.commands.context.Context): Context passed to function.
            member (str): Discord user to be kicked from server.
                          Must be a name and discriminator. E.g.: "User#1234"
        """

        # Get user name and discriminator.
        name, discriminator = member.split("#")

        # Look for user in ban list.
        for ban in await ctx.guild.bans():
            # If user is found, unban them and send a message to the channel command was run on.
            if (ban.user.name, ban.user.discriminator) == (name, discriminator):
                await ctx.guild.unban(ban.user)
                await ctx.send(f"Unbanned {ban.user.name}#{ban.user.discriminator}.")


def setup(bot):
    """
    Binds the cog to the bot.

    Args:
        bot (discord.ext.commands.Bot): Bot to bind cog to.
    """

    bot.add_cog(Management(bot))
