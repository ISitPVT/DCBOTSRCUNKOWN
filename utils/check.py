from utils import database as db
from discord.ext import commands

# Is the user a owner
def is_owner(user_id):
    """Check if user is the bot owner"""
    return db.is_owner(user_id)

# Is the user a dev
def is_dev(user_id):
    """Check if user is a developer or owner"""
    return db.is_dev(user_id)

# Command checks
def owner_only():
    """Command check for owner only"""
    def predicate(ctx):
        return is_owner(ctx.author.id)
    return commands.check(predicate)

def dev_only():
    """Command check for devs only"""
    def predicate(ctx):
        return is_dev(ctx.author.id)
    return commands.check(predicate)

def has_noprefix():
    """Command check for users with no-prefix permission"""
    def predicate(ctx):
        return db.has_noprefix(ctx.author.id)
    return commands.check(predicate)