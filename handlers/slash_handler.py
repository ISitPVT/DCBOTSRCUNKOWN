import discord
from discord.ext import commands
import os
from utils import database as db

def setup_slash_commands(client):
    """Sets up slash commands and related functionality"""
    
    # Original global command sync
    @client.event
    async def on_connect():
        """Sync commands on connect if auto_sync_commands is True"""
        if client.auto_sync_commands:
            await client.sync_commands()
    
    # Development command sync (faster for testing)
    @commands.is_owner()
    @commands.slash_command(name="sync", description="Sync commands to development guilds")
    async def sync_commands(ctx, guild_only: bool = False):
        if guild_only:
            # Sync to current guild only
            synced = await ctx.bot.sync_commands(guild_ids=[ctx.guild.id])
            await ctx.respond(f"Synced {len(synced)} commands to the current guild.")
        else:
            # Sync commands to owner guilds
            owner_guilds = db.owner_guild_ids()
            synced = await ctx.bot.sync_commands(guild_ids=owner_guilds)
            await ctx.respond(f"Synced {len(synced)} commands to development guilds.")
    
    # Setup slash command error handling
    @client.event
    async def on_application_command_error(ctx, error):
        """Handle slash command errors"""
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds.", ephemeral=True)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.respond("You don't have permission to use this command.", ephemeral=True)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.respond(f"I don't have the required permissions: {', '.join(error.missing_permissions)}", ephemeral=True)
        elif isinstance(error, commands.CheckFailure):
            await ctx.respond("You don't have permission to use this command.", ephemeral=True)
        else:
            # Log unexpected errors
            if hasattr(ctx.bot, 'logger'):
                ctx.bot.logger.error(f"Error in slash command {ctx.command.name}: {error}")
            await ctx.respond(f"An error occurred: {error}", ephemeral=True)