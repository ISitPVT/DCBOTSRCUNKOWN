import discord
from discord.ext import commands
from discord import Embed, Color
import datetime

class UtilityPrefix(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command(name="ping", description="Check the bot's latency")
    async def ping(self, ctx):
        latency = round(self.client.latency * 1000)
        embed = Embed(
            title="🏓 Pong!",
            description=f"Bot latency: `{latency}ms`",
            color=Color.green()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="userinfo", description="Get information about a user")
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        
        embed = Embed(
            title=f"{member.name} User Information",
            color=member.color,
            timestamp=datetime.datetime.now()
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="User ID", value=member.id, inline=True)
        embed.add_field(name="Created At", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Joined At", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)
        
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(UtilityPrefix(client))