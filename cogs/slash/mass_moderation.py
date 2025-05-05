import discord
import datetime
from utils import database as db, emoji
from discord.ext import commands
from discord.commands import option, SlashCommandGroup
from utils.utils import parse_duration
from babel.dates import format_timedelta

class MassModeration(commands.Cog):
    def __init__(self, client):
        self.client = client

# Mass slash cmd group
    mass = SlashCommandGroup(guild_ids=db.guild_ids(), name="mass", description="Mass moderation commands.")

    def _build_log_embed(self, title, reason, users, moderator, extra=""):
        desc = (
            f"{emoji.bullet2} **Reason**: {reason or 'No reason provided'}\n"
            f"{emoji.bullet2} **Users**: {', '.join(users)}\n"
            f"{emoji.bullet2} **Moderator**: {moderator.mention}"
        )
        if extra:
            desc += f"\n{extra}"
        return discord.Embed(title=title, description=desc, color=db.error_color)

    async def _log_action(self, guild, embed):
        log_channel_id = db.mod_cmd_log_ch(guild.id)
        if log_channel_id:
            log_ch = await self.client.fetch_channel(log_channel_id)
            await log_ch.send(embed=embed)

    async def _convert_user(self, ctx, user_str):
        try:
            return await commands.MemberConverter().convert(ctx, user_str.strip())
        except:
            return None

    @mass.command(name="kick")
    @discord.default_permissions(kick_members=True)
    @option("users", description="Mention the users to kick. Use ',' to separate users.", required=True)
    @option("reason", description="Reason for kicking the users", required=False)
    async def mass_kick_users(self, ctx, users: str, reason: str = None):
        await ctx.defer()
        user_list = users.split(",")
        kicked, errors = [], []

        if len(user_list) > 10:
            await ctx.respond(embed=discord.Embed(description=f"{emoji.error} You can only mass kick up to 10 users.", color=db.error_color), ephemeral=True)
            return

        for u in user_list:
            member = await self._convert_user(ctx, u)
            if not member:
                errors.append((u.strip(), "User not found."))
                continue
            if member == ctx.author:
                errors.append((member.mention, "You cannot use this on yourself."))
            elif member.top_role >= ctx.author.top_role:
                errors.append((member.mention, "User has same or higher role than you."))
            else:
                try:
                    await member.kick(reason=reason)
                    kicked.append(member.mention)
                except Exception as e:
                    errors.append((member.mention, str(e)))

        if kicked:
            embed = self._build_log_embed(f"{emoji.kick} Mass Kicked Users", reason, kicked, ctx.author)
            await ctx.respond(embed=embed)
            await self._log_action(ctx.guild, embed)

        if errors:
            msg = "\n".join([f"{emoji.bullet2} **{u}**: {r}" for u, r in errors])
            await ctx.respond(embed=discord.Embed(title=f"{emoji.error} Couldn't kick some users", description=msg, color=db.error_color), ephemeral=True)

    @mass.command(name="ban")
    @discord.default_permissions(ban_members=True)
    @option("users", description="Mention the users to ban. Use ',' to separate users.", required=True)
    @option("reason", description="Reason for banning the users", required=False)
    async def mass_ban_users(self, ctx, users: str, reason: str = None):
        await ctx.defer()
        user_list = users.split(",")
        banned, errors = [], []

        if len(user_list) > 10:
            await ctx.respond(embed=discord.Embed(description=f"{emoji.error} You can only mass ban up to 10 users.", color=db.error_color), ephemeral=True)
            return

        for u in user_list:
            member = await self._convert_user(ctx, u)
            if not member:
                errors.append((u.strip(), "User not found."))
                continue
            if member == ctx.author:
                errors.append((member.mention, "You cannot use this on yourself."))
            elif member.top_role >= ctx.author.top_role:
                errors.append((member.mention, "User has same or higher role than you."))
            else:
                try:
                    await member.ban(reason=reason)
                    banned.append(member.mention)
                except Exception as e:
                    errors.append((member.mention, str(e)))

        if banned:
            embed = self._build_log_embed(f"{emoji.mod2} Mass Banned Users", reason, banned, ctx.author)
            await ctx.respond(embed=embed)
            await self._log_action(ctx.guild, embed)

        if errors:
            msg = "\n".join([f"{emoji.bullet2} **{u}**: {r}" for u, r in errors])
            await ctx.respond(embed=discord.Embed(title=f"{emoji.error} Couldn't ban some users", description=msg, color=db.error_color), ephemeral=True)

    @mass.command(name="timeout")
    @discord.default_permissions(moderate_members=True)
    @option("users", description="Mention users separated by ','", required=True)
    @option("duration", description="Timeout duration (e.g. 10m, 1h, 1d)", required=True)
    @option("reason", description="Reason for timeout", required=False)
    async def mass_timeout_users(self, ctx, users: str, duration: str, reason: str = None):
        await ctx.defer()
        duration_seconds = parse_duration(duration)
        if duration_seconds is None:
            await ctx.respond(embed=discord.Embed(description=f"{emoji.error} Invalid duration.", color=db.error_color), ephemeral=True)
            return

        until = datetime.datetime.utcnow() + datetime.timedelta(seconds=duration_seconds)
        readable = format_timedelta(datetime.timedelta(seconds=duration_seconds), locale="en_US")
        user_list = users.split(",")
        timed_out, errors = [], []

        if len(user_list) > 10:
            await ctx.respond(embed=discord.Embed(description=f"{emoji.error} Max 10 users allowed.", color=db.error_color), ephemeral=True)
            return

        for u in user_list:
            member = await self._convert_user(ctx, u)
            if not member:
                errors.append((u.strip(), "User not found."))
                continue
            if member == ctx.author:
                errors.append((member.mention, "You can't timeout yourself."))
            elif member.top_role >= ctx.author.top_role:
                errors.append((member.mention, "User has same or higher role than you."))
            else:
                try:
                    await member.timeout(until, reason=reason)
                    timed_out.append(member.mention)
                except Exception as e:
                    errors.append((member.mention, str(e)))

        if timed_out:
            extra = f"{emoji.bullet2} **Duration**: {readable}"
            embed = self._build_log_embed(f"{emoji.time} Mass Timed Out Users", reason, timed_out, ctx.author, extra=extra)
            await ctx.respond(embed=embed)
            await self._log_action(ctx.guild, embed)

        if errors:
            msg = "\n".join([f"{emoji.bullet2} **{u}**: {r}" for u, r in errors])
            await ctx.respond(embed=discord.Embed(title=f"{emoji.error} Couldn't timeout some users", description=msg, color=db.error_color), ephemeral=True)

    @mass.command(name="untimeout")
    @discord.default_permissions(moderate_members=True)
    @option("users", description="Mention users to untimeout", required=True)
    @option("reason", description="Reason for untimeout", required=False)
    async def mass_untimeout_users(self, ctx, users: str, reason: str = None):
        await ctx.defer()
        user_list = users.split(",")
        untimeouts, errors = [], []

        if len(user_list) > 10:
            await ctx.respond(embed=discord.Embed(description=f"{emoji.error} Max 10 users allowed.", color=db.error_color), ephemeral=True)
            return

        for u in user_list:
            member = await self._convert_user(ctx, u)
            if not member:
                errors.append((u.strip(), "User not found."))
                continue
            try:
                await member.timeout(None, reason=reason)
                untimeouts.append(member.mention)
            except Exception as e:
                errors.append((member.mention, str(e)))

        if untimeouts:
            embed = self._build_log_embed(f"{emoji.success} Mass Untimeout Users", reason, untimeouts, ctx.author)
            await ctx.respond(embed=embed)
            await self._log_action(ctx.guild, embed)

        if errors:
            msg = "\n".join([f"{emoji.bullet2} **{u}**: {r}" for u, r in errors])
            await ctx.respond(embed=discord.Embed(title=f"{emoji.error} Couldn't untimeout some users", description=msg, color=db.error_color), ephemeral=True)

    @mass.command(name="role-add")
    @discord.default_permissions(manage_roles=True)
    @option("users", description="Mention users to add role to", required=True)
    @option("role", discord.Role, description="Role to add", required=True)
    async def mass_add_role(self, ctx, users: str, role: discord.Role):
        await ctx.defer()
        user_list = users.split(",")
        added, errors = [], []

        if len(user_list) > 10:
            await ctx.respond(embed=discord.Embed(description=f"{emoji.error} Max 10 users allowed.", color=db.error_color), ephemeral=True)
            return

        for u in user_list:
            member = await self._convert_user(ctx, u)
            if not member:
                errors.append((u.strip(), "User not found."))
                continue
            try:
                await member.add_roles(role)
                added.append(member.mention)
            except Exception as e:
                errors.append((member.mention, str(e)))

        if added:
            embed = self._build_log_embed(f"{emoji.plus} Mass Role Add", f"Added {role.mention}", added, ctx.author)
            await ctx.respond(embed=embed)
            await self._log_action(ctx.guild, embed)

        if errors:
            msg = "\n".join([f"{emoji.bullet2} **{u}**: {r}" for u, r in errors])
            await ctx.respond(embed=discord.Embed(title=f"{emoji.error} Couldn't add role to some users", description=msg, color=db.error_color), ephemeral=True)

    @mass.command(name="role-remove")
    @discord.default_permissions(manage_roles=True)
    @option("users", description="Mention users to remove role from", required=True)
    @option("role", discord.Role, description="Role to remove", required=True)
    async def mass_remove_role(self, ctx, users: str, role: discord.Role):
        await ctx.defer()
        user_list = users.split(",")
        removed, errors = [], []

        if len(user_list) > 10:
            await ctx.respond(embed=discord.Embed(description=f"{emoji.error} Max 10 users allowed.", color=db.error_color), ephemeral=True)
            return

        for u in user_list:
            member = await self._convert_user(ctx, u)
            if not member:
                errors.append((u.strip(), "User not found."))
                continue
            try:
                await member.remove_roles(role)
                removed.append(member.mention)
            except Exception as e:
                errors.append((member.mention, str(e)))

        if removed:
            embed = self._build_log_embed(f"{emoji.minus} Mass Role Remove", f"Removed {role.mention}", removed, ctx.author)
            await ctx.respond(embed=embed)
            await self._log_action(ctx.guild, embed)

        if errors:
            msg = "\n".join([f"{emoji.bullet2} **{u}**: {r}" for u, r in errors])
            await ctx.respond(embed=discord.Embed(title=f"{emoji.error} Couldn't remove role from some users", description=msg, color=db.error_color), ephemeral=True)
def setup(client):
    client.add_cog(MassModeration(client))