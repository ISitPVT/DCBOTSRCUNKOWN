import discord
from discord.ext import commands
import json
import os
from utils import database as db
from utils import check

class NoPrefixHandler(commands.Cog):
    def __init__(self, client):
        self.client = client
        
        # Create the noprefix.json file if it doesn't exist
        if not os.path.exists('./data'):
            os.makedirs('./data')
        
        if not os.path.exists('./data/noprefix.json'):
            with open('./data/noprefix.json', 'w') as f:
                json.dump({"users": []}, f, indent=4)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for messages and process no-prefix commands if applicable"""
        # Skip processing bot messages
        if message.author.bot:
            return
            
        # Skip messages in DMs (no-prefix only works in servers)
        if not message.guild:
            return
            
        # Check if user has no-prefix permission
        if not (db.is_owner(message.author.id) or 
                db.is_dev(message.author.id) or 
                message.author.id in db._load_noprefix().get("users", [])):
            return
            
        # Don't process messages that start with a prefix
        prefix = db.get_prefix(message.guild.id)
        if message.content.startswith(prefix):
            return
            
        # Create context
        ctx = await self.client.get_context(message)
        
        # Process the potential command
        await self.process_noprefix_commands(ctx)
    
    async def process_noprefix_commands(self, ctx):
        """Process commands without prefix for authorized users"""
        message = ctx.message
        content = message.content.strip()
        
        # Get first word as command
        command_parts = content.split(' ', 1)
        command_name = command_parts[0].lower()
        
        # Check for specific utility commands
        utility_commands = [
            "ping", "uptime", "stats", "avatar", "userinfo", "serverinfo", "emojiinfo"
        ]
        
        # Special handling for help command
        if command_name == "help":
            help_cog = self.client.get_cog("HelpCommands")
            if help_cog and hasattr(help_cog, "process_noprefix_help"):
                await help_cog.process_noprefix_help(ctx)
                return
        
        # Special handling for dev commands
        dev_commands = {
            "dev-add": "process_noprefix_dev_add",
            "dev-remove": "process_noprefix_dev_remove", 
            "dev-list": "process_noprefix_dev_list",
            "lockdown": "process_noprefix_lockdown",
            "restart": "process_noprefix_restart",
            "reload-cogs": "process_noprefix_reload_cogs",
            "shutdown": "process_noprefix_shutdown",
            "status": "process_noprefix_status",
            "guild-list": "process_noprefix_guild_list",
            "guild-leave": "process_noprefix_guild_leave"
        }
        
        if command_name in dev_commands:
            dev_cog = self.client.get_cog("PrefixDevCommands")
            if dev_cog and hasattr(dev_cog, dev_commands[command_name]):
                # Parse arguments if any
                args = []
                if len(command_parts) > 1:
                    args = command_parts[1].strip().split()
                
                # Call the method with appropriate arguments
                method = getattr(dev_cog, dev_commands[command_name])
                if args:
                    await method(ctx, *args)
                else:
                    await method(ctx)
                return
        
        # Otherwise, check if this is a standard utility command
        if command_name in utility_commands:
            # Create a fake context with the command name prefixed
            default_prefix = self.client.command_prefix(self.client, message)[0]
            new_content = default_prefix + content
            message.content = new_content
            
            # Process this command
            new_ctx = await self.client.get_context(message)
            await self.client.invoke(new_ctx)
            
            # Restore original content
            message.content = content
            return
        
        # Otherwise, check the NoPrefixCommands cog for any other commands
        no_prefix_cog = self.client.get_cog("NoPrefixCommands")
        if no_prefix_cog:
            for command in no_prefix_cog.get_commands():
                if command.name == command_name or command_name in getattr(command, "aliases", []):
                    # Create a fake context with the command name prefixed
                    default_prefix = self.client.command_prefix(self.client, message)[0]
                    new_content = default_prefix + content
                    message.content = new_content
                    
                    # Process this command
                    new_ctx = await self.client.get_context(message)
                    await self.client.invoke(new_ctx)
                    
                    # Restore original content
                    message.content = content
                    return

def setup_noprefix_commands(client):
    """Sets up no-prefix command functionality"""
    client.add_cog(NoPrefixHandler(client))
    
    # Add commands to manage no-prefix users (both slash and prefix versions)
    @client.slash_command(name="noprefix", description="View, add, or remove no-prefix privileges")
    @commands.has_permissions(administrator=True)
    async def noprefix_slash(ctx, action: str = "list", user: discord.Member = None):
        """Manage no-prefix privileges (slash version)"""
        if action == "list":
            # List users with no-prefix
            noprefix_data = db._load_noprefix()
            user_list = []
            
            # Add owner and devs (they always have no-prefix)
            owner_id = db.owner_id()
            user_list.append(f"<@{owner_id}> (Owner)")
            
            for dev_id in db.dev_ids():
                if dev_id != owner_id:  # Don't duplicate owner
                    user_list.append(f"<@{dev_id}> (Developer)")
            
            # Add regular users with no-prefix
            for user_id in noprefix_data.get("users", []):
                if user_id not in db.dev_ids() and user_id != owner_id:  # Don't duplicate
                    user_list.append(f"<@{user_id}>")
            
            if not user_list:
                await ctx.respond("No users have no-prefix privileges.")
            else:
                await ctx.respond(f"Users with no-prefix privileges:\n" + "\n".join(user_list))
                
        elif action == "add":
            if user is None:
                await ctx.respond("Please specify a user to add.", ephemeral=True)
                return
                
            if db.add_noprefix(user.id):
                await ctx.respond(f"User {user.mention} can now use commands without prefix.")
            else:
                await ctx.respond(f"User {user.mention} already has no-prefix permission.", ephemeral=True)
                
        elif action == "remove":
            if user is None:
                await ctx.respond("Please specify a user to remove.", ephemeral=True)
                return
                
            if db.is_owner(user.id) or db.is_dev(user.id):
                await ctx.respond(f"Cannot remove no-prefix privilege from owners or developers.", ephemeral=True)
                return
                
            if db.remove_noprefix(user.id):
                await ctx.respond(f"User {user.mention} can no longer use commands without prefix.")
            else:
                await ctx.respond(f"User {user.mention} didn't have no-prefix permission.", ephemeral=True)
        
        else:
            await ctx.respond("Invalid action. Use 'list', 'add', or 'remove'.", ephemeral=True)
    
    @client.command(name="noprefix")
    @commands.has_permissions(administrator=True)
    async def noprefix_text(ctx, action: str = "list", user: discord.Member = None):
        """Manage no-prefix privileges (text version)"""
        if action == "list":
            # List users with no-prefix
            noprefix_data = db._load_noprefix()
            user_list = []
            
            # Add owner and devs (they always have no-prefix)
            owner_id = db.owner_id()
            user_list.append(f"<@{owner_id}> (Owner)")
            
            for dev_id in db.dev_ids():
                if dev_id != owner_id:  # Don't duplicate owner
                    user_list.append(f"<@{dev_id}> (Developer)")
            
            # Add regular users with no-prefix
            for user_id in noprefix_data.get("users", []):
                if user_id not in db.dev_ids() and user_id != owner_id:  # Don't duplicate
                    user_list.append(f"<@{user_id}>")
            
            if not user_list:
                await ctx.send("No users have no-prefix privileges.")
            else:
                await ctx.send(f"Users with no-prefix privileges:\n" + "\n".join(user_list))
                
        elif action == "add":
            if user is None:
                await ctx.send("Please specify a user to add.")
                return
                
            if db.add_noprefix(user.id):
                await ctx.send(f"User {user.mention} can now use commands without prefix.")
            else:
                await ctx.send(f"User {user.mention} already has no-prefix permission.")
                
        elif action == "remove":
            if user is None:
                await ctx.send("Please specify a user to remove.")
                return
                
            if db.is_owner(user.id) or db.is_dev(user.id):
                await ctx.send(f"Cannot remove no-prefix privilege from owners or developers.")
                return
                
            if db.remove_noprefix(user.id):
                await ctx.send(f"User {user.mention} can no longer use commands without prefix.")
            else:
                await ctx.send(f"User {user.mention} didn't have no-prefix permission.")
        
        else:
            await ctx.send("Invalid action. Use 'list', 'add', or 'remove'.")
