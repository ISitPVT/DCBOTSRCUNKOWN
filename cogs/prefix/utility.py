import discord
from discord.ext import commands
from utils import database as db, emoji
import datetime, time
import platform

# Import the start_time from your original Info cog
start_time = time.time()

class Utility(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command(name="ping")
    async def ping(self, ctx):
        """Shows bot latency."""
        ping_em = discord.Embed(
            description=f"{emoji.bullet} **Ping**: `{round(self.client.latency * 1000)} ms`",
            color=db.theme_color
        )
        await ctx.send(embed=ping_em)
    
    @commands.command(name="uptime")
    async def uptime(self, ctx):
        """Shows bot's uptime."""
        uptime_em = discord.Embed(
            description=f"{emoji.bullet} **Bot's Uptime**: `{str(datetime.timedelta(seconds=int(round(time.time() - start_time))))}`",
            color=db.theme_color
        )
        await ctx.send(embed=uptime_em)
    
    @commands.command(name="stats")
    async def stats(self, ctx):
        """Shows bot stats."""
        owner = self.client.get_user(db.owner_id()) or await self.client.fetch_user(db.owner_id())
        stats_em = discord.Embed(
            title=f"{self.client.user.name} Stats",
            description=(
                f"{emoji.bullet} **Bot's Latency**: `{round(self.client.latency * 1000)} ms`\n"
                f"{emoji.bullet} **Bot's Uptime**: `{str(datetime.timedelta(seconds=int(round(time.time() - start_time))))}`\n"
                f"{emoji.bullet} **Total Servers**: `{str(len(self.client.guilds))}`\n"
                f"{emoji.bullet} **Total Members**: `{len(set(self.client.get_all_members()))}`\n"
                f"{emoji.bullet} **Total Channels**: `{len(set(self.client.get_all_channels()))}`\n"
                f"{emoji.bullet} **Python Version**: `v{platform.python_version()}`\n"
                f"{emoji.bullet} **Pycord Version**: `v{discord.__version__}`"
            ),
            color=db.theme_color
        )
        if owner and owner.avatar:
            stats_em.set_footer(text=f"Designed & Built by {owner}", icon_url=owner.avatar.url)
        else:
            stats_em.set_footer(text=f"Designed & Built by Owner (ID: {db.owner_id()})")
        await ctx.send(embed=stats_em)
    
    @commands.command(name="avatar")
    async def avatar(self, ctx, user: discord.Member = None):
        """Shows the avatar of the mentioned user."""
        user = user or ctx.author
        if not user.avatar:
            await ctx.send(f"{emoji.error} User has no avatar.")
            return
            
        avatar_em = discord.Embed(
            title=f"{user.name}'s Avatar",
            description=f"[Avatar URL]({user.avatar.url})",
            color=db.theme_color
        )
        avatar_em.set_image(url=user.avatar.url)
        await ctx.send(embed=avatar_em)
    
    @commands.command(name="userinfo")
    async def user_info(self, ctx, user: discord.Member = None):
        """Shows info of the mentioned user."""
        user = user or ctx.author
        user_info_em = discord.Embed(
            title=f"{user.name}'s Info",
            description=(
                f"{emoji.bullet} **Name**: `{user}`\n"
                f"{emoji.bullet} **ID**: `{user.id}`\n"
                f"{emoji.bullet} **Bot?**: {user.bot}\n"
                f"{emoji.bullet} **Avatar URL**: {f'[Click Here]({user.avatar.url})' if user.avatar else 'None'}\n"
                f"{emoji.bullet} **Status**: {user.status}\n"
                f"{emoji.bullet} **Nickname**: {user.nick or 'None'}\n"
                f"{emoji.bullet} **Highest Role**: {user.top_role.mention}\n"
                f"{emoji.bullet} **Account Created**: {discord.utils.format_dt(user.created_at, 'R')}\n"
                f"{emoji.bullet} **Server Joined**: {discord.utils.format_dt(user.joined_at, 'R')}"
            ),
            color=db.theme_color
        )
        if user.avatar:
            user_info_em.set_thumbnail(url=user.avatar.url)
        await ctx.send(embed=user_info_em)
    
    @commands.command(name="serverinfo")
    async def server_info(self, ctx):
        """Shows info of the current server."""
        server_info_em = discord.Embed(
            title=f"{ctx.guild.name}'s Info",
            description=(
                f"{emoji.bullet} **Name**: {ctx.guild.name}\n"
                f"{emoji.bullet} **ID**: `{ctx.guild.id}`\n"
                f"{emoji.bullet} **Icon URL**: {f'[Click Here]({ctx.guild.icon})' if ctx.guild.icon else 'None'}\n"
                f"{emoji.bullet} **Owner**: {ctx.guild.owner.mention}\n"
                f"{emoji.bullet} **Verification Level**: `{ctx.guild.verification_level}`\n"
                f"{emoji.bullet} **Total Categorie(s)**: `{len(ctx.guild.categories)}`\n"
                f"{emoji.bullet} **Total Channel(s)**: `{len(ctx.guild.text_channels) + len(ctx.guild.voice_channels)}`\n"
                f"{emoji.bullet} **Text Channel(s)**: `{len(ctx.guild.text_channels)}`\n"
                f"{emoji.bullet} **Voice Channel(s)**: `{len(ctx.guild.voice_channels)}`\n"
                f"{emoji.bullet} **Stage Channel(s)**: `{len(ctx.guild.stage_channels)}`\n"
                f"{emoji.bullet} **Total Member(s)**: `{len(ctx.guild.members)}`\n"
                f"{emoji.bullet} **Human(s)**: `{len([m for m in ctx.guild.members if not m.bot])}`\n"
                f"{emoji.bullet} **Bot(s)**: `{len([m for m in ctx.guild.members if m.bot])}`\n"
                f"{emoji.bullet} **Role(s)**: `{len(ctx.guild.roles)}`\n"
                f"{emoji.bullet} **Server Created**: {discord.utils.format_dt(ctx.guild.created_at, 'R')}"
            ),
            color=db.theme_color
        )
        if ctx.guild.icon:
            server_info_em.set_thumbnail(url=ctx.guild.icon)
        await ctx.send(embed=server_info_em)
    
    @commands.command(name="emojiinfo")
    async def emoji_info(self, ctx, icon: discord.Emoji = None):
        """Shows info of the given emoji."""
        if icon is None:
            await ctx.send(f"{emoji.error} Please provide an emoji to get information about.")
            return
            
        emoji_info_em = discord.Embed(
            description=(
                f"{emoji.bullet} **Name**: {icon.name}\n"
                f"{emoji.bullet} **ID**: `{icon.id}`\n"
                f"{emoji.bullet} **Emoji URL**: [Click Here]({icon.url})\n"
                f"{emoji.bullet} **Is Animated?**: {icon.animated}\n"
                f"{emoji.bullet} **Usage**: `{icon}`\n"
                f"{emoji.bullet} **Emoji Created**: {discord.utils.format_dt(icon.created_at, 'R')}"
            ),
            color=db.theme_color
        )
        emoji_info_em.set_thumbnail(url=icon.url)
        await ctx.send(embed=emoji_info_em)

def setup(client):
    client.add_cog(Utility(client))
