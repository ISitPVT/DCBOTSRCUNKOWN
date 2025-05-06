
import discord
import discord.ui
import os, sys
import math
from utils import database as db, emoji
from utils import check
from discord.ext import commands

class GuildListView(discord.ui.View):
    def __init__(self, client: discord.Client, ctx: commands.Context, page: int, timeout: int):
        super().__init__(timeout=timeout, disable_on_timeout=True)
        self.client = client
        self.ctx = ctx
        self.page = page
        self.items_per_page = 10

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            help_check_em = discord.Embed(description=f"{emoji.error} You are not the author of this message", color=db.error_color)
            await interaction.response.send_message(embed=help_check_em, ephemeral=True)
            return False
        else:
            return True

    # Start
    @discord.ui.button(emoji=f"{emoji.start}", custom_id="start", style=discord.ButtonStyle.grey)
    async def start_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.page = 1
        em = GuildListEmbed(self.client, self.page).get_embed()
        await interaction.response.edit_message(embed=em, view=self)

    # Previous
    @discord.ui.button(emoji=f"{emoji.previous}", custom_id="previous", style=discord.ButtonStyle.grey)
    async def previous_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        pages = math.ceil(len(self.client.guilds) / self.items_per_page)
        if self.page <= 1:
            self.page = pages
        else:
            self.page -= 1
        em = GuildListEmbed(self.client, self.page).get_embed()
        await interaction.response.edit_message(embed=em, view=self)

    # Next
    @discord.ui.button(emoji=f"{emoji.next}", custom_id="next", style=discord.ButtonStyle.grey)
    async def next_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        pages = math.ceil(len(self.client.guilds) / self.items_per_page)
        if self.page >= pages:
            self.page = 1
        else:
            self.page += 1
        em = GuildListEmbed(self.client, self.page).get_embed()
        await interaction.response.edit_message(embed=em, view=self)

    # End
    @discord.ui.button(emoji=f"{emoji.end}", custom_id="end", style=discord.ButtonStyle.grey)
    async def end_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.page = math.ceil(len(self.client.guilds) / self.items_per_page)
        em = GuildListEmbed(self.client, self.page).get_embed()
        await interaction.response.edit_message(embed=em, view=self)

class GuildListEmbed(discord.Embed):
    def __init__(self, client: discord.Client, page: int):
        super().__init__(title=f"{emoji.embed} Guilds List", color=db.theme_color)
        self.client = client
        self.page = page
        self.items_per_page = 10

    def get_guilds(self):
        guilds = self.client.guilds
        start = (self.page - 1) * self.items_per_page
        end = start + self.items_per_page
        return guilds[start:end]

    def get_guilds_list(self):
        guilds_list = ""
        for num, guild in enumerate(self.get_guilds(), start=self.items_per_page * (self.page - 1) + 1):
            guilds_list += f"`{num}.` **{guild.name}** - `{guild.id}`\n"
        return guilds_list

    def get_footer(self):
        total_pages = math.ceil(len(self.client.guilds) / self.items_per_page)
        return f"Viewing Page {self.page}/{total_pages}"

    def get_embed(self):
        self.description = self.get_guilds_list()
        self.set_footer(text=self.get_footer())
        return self

class PrefixDevCommands(commands.Cog, name="PrefixDevCommands"):
    def __init__(self, client: discord.Client):
        self.client = client

    # Add dev command with prefix
    @commands.command(name="dev-add")
    async def add_dev(self, ctx: commands.Context, user: discord.Member = None):
        """Adds a bot dev."""
        if check.is_owner(ctx.author.id):
            if user is None:
                error_em = discord.Embed(description=f"{emoji.error} Please specify a user to add as a dev", color=db.error_color)
                await ctx.send(embed=error_em)
                return
                
            db.add_dev_ids(user.id)
            done_em = discord.Embed(title=f"{emoji.plus} Added", description=f"Added {user.mention} to dev", color=db.theme_color)
            await ctx.send(embed=done_em)
        else:
            error_em = discord.Embed(description=f"{emoji.error} You are not authorized to use the command", color=db.error_color)
            await ctx.send(embed=error_em)
    
    # Process no-prefix dev-add command
    async def process_noprefix_dev_add(self, ctx: commands.Context, user: discord.Member = None):
        """Process the dev-add command when used without a prefix"""
        await self.add_dev(ctx, user)

    # Remove dev command with prefix
    @commands.command(name="dev-remove")
    async def remove_dev(self, ctx: commands.Context, user: discord.Member = None):
        """Removes a bot dev."""
        if check.is_owner(ctx.author.id):
            if user is None:
                error_em = discord.Embed(description=f"{emoji.error} Please specify a user to remove from dev", color=db.error_color)
                await ctx.send(embed=error_em)
                return
                
            db.remove_dev_ids(user.id)
            done_em = discord.Embed(title=f"{emoji.bin} Removed", description=f"Removed {user.mention} from dev", color=db.theme_color)
            await ctx.send(embed=done_em)
        else:
            error_em = discord.Embed(description=f"{emoji.error} You are not authorized to use the command", color=db.error_color)
            await ctx.send(embed=error_em)
    
    # Process no-prefix dev-remove command
    async def process_noprefix_dev_remove(self, ctx: commands.Context, user: discord.Member = None):
        """Process the dev-remove command when used without a prefix"""
        await self.remove_dev(ctx, user)

    # List devs command with prefix
    @commands.command(name="dev-list")
    async def list_devs(self, ctx: commands.Context):
        """Shows bot devs."""
        if check.is_owner(ctx.author.id):
            num = 0
            devs_list = ""
            for ids in list(db.dev_ids()):
                num += 1
                dev_mention = f"<@{ids}>"
                devs_list += f"`{num}.` {dev_mention}\n"
            dev_em = discord.Embed(title=f"{emoji.embed} Devs List", description=devs_list, color=db.theme_color)
            await ctx.send(embed=dev_em)
        else:
            error_em = discord.Embed(description=f"{emoji.error} You are not authorized to use the command", color=db.error_color)
            await ctx.send(embed=error_em)
    
    # Process no-prefix dev-list command
    async def process_noprefix_dev_list(self, ctx: commands.Context):
        """Process the dev-list command when used without a prefix"""
        await self.list_devs(ctx)
    
    # Lockdown command with prefix
    @commands.command(name="lockdown")
    async def lockdown(self, ctx: commands.Context, status: str = None):
        """Lockdowns the bot. Usage: lockdown <enable/disable>"""
        if check.is_dev(ctx.author.id):
            if status is None:
                error_em = discord.Embed(description=f"{emoji.error} Please specify the status (enable/disable)", color=db.error_color)
                await ctx.send(embed=error_em)
                return
                
            status = status.lower()
            if status not in ["enable", "disable"]:
                error_em = discord.Embed(description=f"{emoji.error} Status must be 'enable' or 'disable'", color=db.error_color)
                await ctx.send(embed=error_em)
                return
                
            db.lockdown(True) if status == "enable" else db.lockdown(False)
            lockdown_em = discord.Embed(
                title=f"{emoji.lock if db.lockdown(status_only=True) else emoji.unlock} Bot Lockdown",
                description=f"Bot is now in lockdown mode" if db.lockdown(status_only=True) else "Bot is now out of lockdown mode",
                color=db.theme_color
            )
            await ctx.send(embed=lockdown_em)
            await self.restart(ctx)
        else:
            error_em = discord.Embed(description=f"{emoji.error} You are not authorized to use the command", color=db.error_color)
            await ctx.send(embed=error_em)
    
    # Process no-prefix lockdown command
    async def process_noprefix_lockdown(self, ctx: commands.Context, status: str = None):
        """Process the lockdown command when used without a prefix"""
        await self.lockdown(ctx, status)
    
    # Restart command with prefix
    @commands.command(name="restart")
    async def restart(self, ctx: commands.Context):
        """Restarts the bot."""
        if check.is_dev(ctx.author.id):
            restart_em = discord.Embed(title=f"{emoji.restart} Restarting", color=db.theme_color)
            await ctx.send(embed=restart_em)
            os.system("clear")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            error_em = discord.Embed(description=f"{emoji.error} You are not authorized to use the command", color=db.error_color)
            await ctx.send(embed=error_em)
    
    # Process no-prefix restart command
    async def process_noprefix_restart(self, ctx: commands.Context):
        """Process the restart command when used without a prefix"""
        await self.restart(ctx)
    
    # Reload cogs command with prefix
    @commands.command(name="reload-cogs")
    async def reload_cogs(self, ctx: commands.Context):
        """Reloads bot's all files."""
        if check.is_dev(ctx.author.id):
            reload_em = discord.Embed(title=f"{emoji.restart} Reloaded Cogs", color=db.theme_color)
            await ctx.send(embed=reload_em)
            for filename in os.listdir("./cogs"):
                if filename.endswith(".py"):
                    self.client.reload_extension(f"cogs.{filename[:-3]}")
        else:
            error_em = discord.Embed(description=f"{emoji.error} You are not authorized to use the command", color=db.error_color)
            await ctx.send(embed=error_em)
    
    # Process no-prefix reload-cogs command
    async def process_noprefix_reload_cogs(self, ctx: commands.Context):
        """Process the reload-cogs command when used without a prefix"""
        await self.reload_cogs(ctx)
    
    # Shutdown command with prefix
    @commands.command(name="shutdown")
    async def shutdown(self, ctx: commands.Context):
        """Shutdowns the bot."""
        if check.is_owner(ctx.author.id):
            shutdown_em = discord.Embed(title=f"{emoji.shutdown} Shutdown", color=db.theme_color)
            await ctx.send(embed=shutdown_em)
            await self.client.wait_until_ready()
            await self.client.close()
        else:
            error_em = discord.Embed(description=f"{emoji.error} You are not authorized to use the command", color=db.error_color)
            await ctx.send(embed=error_em)
    
    # Process no-prefix shutdown command
    async def process_noprefix_shutdown(self, ctx: commands.Context):
        """Process the shutdown command when used without a prefix"""
        await self.shutdown(ctx)
    
    # Set status command with prefix
    @commands.command(name="status")
    async def set_status(self, ctx: commands.Context, type: str = None, *, status: str = None):
        """Sets custom bot status. Usage: status <game/streaming/listening/watching> <status text>"""
        if check.is_dev(ctx.author.id):
            if type is None or status is None:
                error_em = discord.Embed(description=f"{emoji.error} Please specify both type and status", color=db.error_color)
                await ctx.send(embed=error_em)
                return
                
            type = type.lower()
            valid_types = {"game": "Game", "streaming": "Streaming", "listening": "Listening", "watching": "Watching"}
            
            if type not in valid_types:
                error_em = discord.Embed(description=f"{emoji.error} Type must be 'game', 'streaming', 'listening', or 'watching'", color=db.error_color)
                await ctx.send(embed=error_em)
                return
                
            type = valid_types[type]
                
            if type == "Game":
                await self.client.change_presence(activity=discord.Game(name=status))
            elif type == "Streaming":
                await self.client.change_presence(activity=discord.Streaming(name=status, url=db.support_server_url()))
            elif type == "Listening":
                await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=status))
            elif type == "Watching":
                await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status))
            
            status_em = discord.Embed(title=f"{emoji.console} Status Changed", description=f"Status changed to **{type}** as `{status}`", color=db.theme_color)
            await ctx.send(embed=status_em)
        else:
            error_em = discord.Embed(description=f"{emoji.error} You are not authorized to use the command", color=db.error_color)
            await ctx.send(embed=error_em)
    
    # Process no-prefix status command
    async def process_noprefix_status(self, ctx: commands.Context, type: str = None, *, status: str = None):
        """Process the status command when used without a prefix"""
        await self.set_status(ctx, type, status=status)
    
    # List guilds command with prefix
    @commands.command(name="guild-list")
    async def list_guilds(self, ctx: commands.Context):
        """Shows all guilds."""
        if check.is_owner(ctx.author.id):
            guild_list_em = GuildListEmbed(self.client, 1).get_embed()
            guild_list_view = None
            if len(self.client.guilds) > 10:
                guild_list_view = GuildListView(self.client, ctx, 1, timeout=60)
            await ctx.send(embed=guild_list_em, view=guild_list_view)
        else:
            error_em = discord.Embed(description=f"{emoji.error} You are not authorized to use the command", color=db.error_color)
            await ctx.send(embed=error_em)
    
    # Process no-prefix guild-list command
    async def process_noprefix_guild_list(self, ctx: commands.Context):
        """Process the guild-list command when used without a prefix"""
        await self.list_guilds(ctx)
    
    # Leave guild command with prefix
    @commands.command(name="guild-leave")
    async def leave_guild(self, ctx: commands.Context, *, guild_name: str = None):
        """Leaves a guild by name."""
        if check.is_owner(ctx.author.id):
            if guild_name is None:
                error_em = discord.Embed(description=f"{emoji.error} Please specify a guild name", color=db.error_color)
                await ctx.send(embed=error_em)
                return
                
            # Find the guild by name
            guild = discord.utils.get(self.client.guilds, name=guild_name)
            if guild is None:
                error_em = discord.Embed(description=f"{emoji.error} Could not find a guild with that name", color=db.error_color)
                await ctx.send(embed=error_em)
                return
                
            if any(guild.id == g for g in db.owner_guild_ids()):
                error_em = discord.Embed(description=f"{emoji.error} I can't leave the owner guild", color=db.error_color)
                await ctx.send(embed=error_em)
                return
                
            await guild.leave()
            leave_em = discord.Embed(title=f"{emoji.minus} Left Guild", description=f"Left **{guild.name}**", color=db.error_color)
            await ctx.send(embed=leave_em)
        else:
            error_em = discord.Embed(description=f"{emoji.error} You are not authorized to use the command", color=db.error_color)
            await ctx.send(embed=error_em)
    
    # Process no-prefix guild-leave command
    async def process_noprefix_guild_leave(self, ctx: commands.Context, *, guild_name: str = None):
        """Process the guild-leave command when used without a prefix"""
        await self.leave_guild(ctx, guild_name=guild_name)

def setup(client: discord.Client):
    client.add_cog(PrefixDevCommands(client))
