import discord
import os
import asyncio
from utils import database as db
from handlers.slash_handler import setup_slash_commands
from handlers.prefix_handler import setup_prefix_commands
from handlers.noprefix_handler import setup_noprefix_commands
from rich import print
from rich.progress import Progress, SpinnerColumn
from pyfiglet import Figlet
from discord.ext import commands

# Discord vars
status = discord.Status.idle if not db.lockdown(status_only=True) else discord.Status.dnd
activity = discord.Activity(type=discord.ActivityType.listening, name="Managing Your Cute Servers") if not db.lockdown(status_only=True) else discord.Activity(type=discord.ActivityType.playing, name="Maintenance")
intents = discord.Intents.all()

# Create the bot client with default prefix (will be overridden per server)
DEFAULT_PREFIX = "!"
client = commands.Bot(
    command_prefix=lambda bot, message: db.get_prefix(message.guild.id) if message.guild else DEFAULT_PREFIX,
    status=status, 
    activity=activity, 
    intents=intents, 
    help_command=None
)

# Startup printing
figlted_txt = Figlet(font="standard", justify="center").renderText("Discord Bot")
print(f"[cyan]{figlted_txt}[/]")

# Loading all command handlers
def load_handlers():
    setup_slash_commands(client)
    setup_prefix_commands(client)
    setup_noprefix_commands(client)

# Loading all cog files
cogs_progress_bar = Progress(
    SpinnerColumn(style="yellow", finished_text="[green bold]✓[/]"),
    "[progress.description]{task.description} [progress.percentage]{task.percentage:>3.1f}%"
)
with cogs_progress_bar as progress:
    # Load cogs from both slash and prefix directories
    cog_directories = ["./cogs/slash", "./cogs/prefix"]
    file_count = sum(len([file for file in os.listdir(directory) if file.endswith(".py")]) 
                     for directory in cog_directories if os.path.exists(directory))
    
    task = cogs_progress_bar.add_task("Loading Cogs", total=file_count)
    
    # Load all handlers
    load_handlers()
    
    # Load all cogs
    for directory in cog_directories:
        if not os.path.exists(directory):
            continue
            
        for filename in os.listdir(directory):
            if filename.endswith(".py") and filename != "__init__.py":
                progress.update(task, advance=1)
                client.load_extension(f"{directory[2:].replace('/', '.')}.{filename[:-3]}")
    
    progress.update(task, description="[green]Loaded Cogs[/]")

# On connect event
@client.event
async def on_connect():
    
    if client.auto_sync_commands:
        try:
            await client.sync_commands()
            print("[green][bold]✓[/] Commands synced successfully")
        except discord.errors.Forbidden:
            print("[yellow][bold]![/] Unable to sync commands: Missing permissions")
        except Exception as e:
            print(f"[red][bold]✗[/] commands sync failed: {e}")
        
        await client.sync_commands()

# On ready event
@client.event
async def on_ready():
    print(f"[green][bold]✓[/] Logged in as {client.user} [ID: {client.user.id}][/]")
    print(f"[green][bold]✓[/] Connected to {len(client.guilds)} guild{'' if len(client.guilds) <= 1 else 's'}[/]")
    print(f"[green][bold]✓[/] Default prefix: {DEFAULT_PREFIX}[/]")

# Handle messages - for no prefix commands
@client.event
async def on_message(message):
    # Ignore messages from bots
    if message.author.bot:
        return
    
    # Check if user has noprefix permission
    has_noprefix = db.has_noprefix(message.author.id)
    
    # Process commands with prefixes first
    await client.process_commands(message)
    
    # Then check for no-prefix commands if user has permission
    if has_noprefix:
        # Let the noprefix handler handle this
        ctx = await client.get_context(message)
        await client.get_cog("NoPrefixHandler").process_noprefix_commands(ctx)

# Starting bot
try:
    client.run(db.discord_api_token())
except Exception as e:
    print(f"[red][bold]✗[/] Unable to login due to {e}[/]")