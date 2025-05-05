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
    
    async def process_noprefix_commands(self, ctx):
        """Process commands without prefix for authorized users"""
        # This method will be called from on_message if the user has no-prefix permission
        
        message = ctx.message
        content = message.content.strip()
        
        # Special handling for help command
        if content.lower() == "help":
            help_cog = self.client.get_cog("HelpCommands")
            if help_cog:
                # If our custom help command cog exists, use the special method
                if hasattr(help_cog, "process_noprefix_help"):
                    await help_cog.process_noprefix_help(ctx)
                    return
        
        # Get first word as command
        command_name = content.split(' ')[0].lower()
        
        # Check if this command exists in the no-prefix commands cog
        for command in self.client.walk_commands():
            if not command.cog:
                continue
                
            if command.cog.qualified_name != "NoPrefixCommands":
                continue
                
            if command.name == command_name or command_name in command.aliases:
                # Create a fake context with the command name prefixed
                default_prefix = self.client.command_prefix(self.client, message)[0]
                new_content = default_prefix + content
                message.content = new_content
                
                # Process this command
                ctx = await self.client.get_context(message)
                await self.client.invoke(ctx)
                
                # Restore original content
                message.content = content
                return
                
        # If we've reached here and the command is just "help", let's handle it as a special case
        # This allows help to work even if there's no NoPrefixCommands cog
        if command_name == "help":
            # Create a fake context with the help command prefixed
            default_prefix = self.client.command_prefix(self.client, message)[0]
            new_content = default_prefix + content
            message.content = new_content
            
            # Process this command
            ctx = await self.client.get_context(message)
            await self.client.invoke(ctx)
            
            # Restore original content
            message.content = content

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