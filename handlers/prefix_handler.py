import discord
from discord.ext import commands
import json
import os
from utils import database as db
from utils import check

def setup_prefix_commands(client):
    """Sets up prefix command functionality"""
    
    # Create the prefixes.json file if it doesn't exist
    if not os.path.exists('./data'):
        os.makedirs('./data')
    
    if not os.path.exists('./data/prefixes.json'):
        with open('./data/prefixes.json', 'w') as f:
            json.dump({}, f, indent=4)
    
    # Hook into database to manage prefixes
    @client.event
    async def on_guild_join(guild):
        """Set default prefix when joining a new guild"""
        db.set_prefix(guild.id, "!")
        # Also create guild config database
        db.create(guild.id)
    
    @client.event
    async def on_guild_remove(guild):
        """Remove prefix data when leaving a guild"""
        db.remove_prefix(guild.id)
        # Also delete guild config database
        try:
            db.delete(guild.id)
        except:
            pass
    
    # Add prefix command (both slash and prefix version)
    @client.slash_command(name="prefix", description="View or change the bot's prefix for this server")
    @commands.has_permissions(manage_guild=True)
    async def prefix_slash(ctx, new_prefix: str = None):
        """Change the server's command prefix (slash version)"""
        if new_prefix is None:
            current_prefix = db.get_prefix(ctx.guild.id)
            await ctx.respond(f"Current prefix is: `{current_prefix}`")
        else:
            if len(new_prefix) > 5:
                await ctx.respond("Prefix cannot be longer than 5 characters.", ephemeral=True)
                return
                
            db.set_prefix(ctx.guild.id, new_prefix)
            await ctx.respond(f"Prefix changed to `{new_prefix}`")
    
    @client.command(name="prefix")
    @commands.has_permissions(manage_guild=True)
    async def prefix_text(ctx, new_prefix: str = None):
        """Change the server's command prefix (text version)"""
        if new_prefix is None:
            current_prefix = db.get_prefix(ctx.guild.id)
            await ctx.send(f"Current prefix is: `{current_prefix}`")
        else:
            if len(new_prefix) > 5:
                await ctx.send("Prefix cannot be longer than 5 characters.")
                return
                
            db.set_prefix(ctx.guild.id, new_prefix)
            await ctx.send(f"Prefix changed to `{new_prefix}`")
    
    # Setup prefix command error handling
    @client.event
    async def on_command_error(ctx, error):
        """Handle prefix command errors"""
        if isinstance(error, commands.CommandNotFound):
            # Don't respond to unknown commands
            return
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"I don't have the required permissions: {', '.join(error.missing_permissions)}")
        elif isinstance(error, commands.CheckFailure):
            await ctx.send("You don't have permission to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing required argument: {error.param.name}")
        else:
            # Log unexpected errors
            if hasattr(ctx.bot, 'logger'):
                ctx.bot.logger.error(f"Error in prefix command {ctx.command.name}: {error}")
            await ctx.send(f"An error occurred: {error}")