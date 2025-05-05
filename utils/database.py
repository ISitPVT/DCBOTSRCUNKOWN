import os
import json

config_file_path = "./configs/config.json"
temp_file_path = {}

theme_color = int("22CEEC", 16)
error_color = None  # Will be set to discord.Color.red() in main.py

# -------------------- CONFIG FILE --------------------

def _load_config():
    """Load config data from file"""
    with open(f"{config_file_path}", "r") as config_file:
        return json.load(config_file)

def _save_config(config_data):
    """Save config data to file"""
    with open(f"{config_file_path}", "w") as config_file:
        json.dump(config_data, config_file, indent=4)

# Owner IDs
def owner_id():
    """Get owner ID from config"""
    config_data = _load_config()
    return config_data["owner_id"]

# Add dev ID
def add_dev_ids(user_id: int):
    """Add a developer ID to config"""
    config_data = _load_config()
    if user_id not in list(config_data["dev_ids"]):
        config_data["dev_ids"].append(user_id)
        _save_config(config_data)
        return True
    return False

# Remove dev
def remove_dev_ids(user_id: int):
    """Remove a developer ID from config"""
    config_data = _load_config()
    if user_id in list(config_data["dev_ids"]):
        config_data["dev_ids"].remove(user_id)
        _save_config(config_data)
        return True
    return False

# Dev IDs
def dev_ids():
    """Get list of developer IDs"""
    config_data = _load_config()
    dev_ids = []
    for ids in config_data["dev_ids"]:
        dev_ids.append(ids)
    return list(dev_ids)

# Check if user is dev
def is_dev(user_id):
    """Check if user is a developer"""
    return user_id in dev_ids() or user_id == owner_id()

# Check if user is owner
def is_owner(user_id):
    """Check if user is the owner"""
    return user_id == owner_id()

# Lockdown
def lockdown(status: bool = True, status_only: bool = False):
    """Get or set lockdown status"""
    config_data = _load_config()
    if status_only:
        return config_data["lockdown"]
    else:
        config_data["lockdown"] = status
        _save_config(config_data)
        return status

# Return owner guild ids if lockdown is enabled
def guild_ids():
    """Get guild IDs based on lockdown status"""
    return owner_guild_ids() if lockdown(status_only=True) else None

# Owner guild IDs
def owner_guild_ids():
    """Get owner guild IDs"""
    config_data = _load_config()
    return config_data["owner_guild_ids"]

# System channel
def system_ch_id():
    """Get system channel ID"""
    config_data = _load_config()
    return config_data["system_ch_id"]

# Support server
def support_server_url():
    """Get support server URL"""
    config_data = _load_config()
    return config_data["support_server_url"]

# Discord API token
def discord_api_token():
    """Get Discord API token"""
    config_data = _load_config()
    try:
        return os.environ["discord_api_token"]
    except Exception:
        return config_data["discord_api_token"]

# Lavalink
def lavalink(key: str = None, mode: str = "get", data: str = None):
    """Get or set Lavalink configuration"""
    config_data = _load_config()
    if mode == "get":
        return config_data["lavalink"][key]
    elif mode == "set":
        config_data["lavalink"][key] = data
        _save_config(config_data)
        return data

# -------------------- PREFIX MANAGEMENT --------------------

def _load_prefixes():
    """Load server prefixes from file"""
    try:
        if not os.path.exists('./data'):
            os.makedirs('./data')
        
        if not os.path.exists('./data/prefixes.json'):
            with open('./data/prefixes.json', 'w') as f:
                json.dump({}, f, indent=4)
                return {}
        
        with open('./data/prefixes.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Create the file if it doesn't exist
        if not os.path.exists('./data'):
            os.makedirs('./data')
        
        with open('./data/prefixes.json', 'w') as f:
            json.dump({}, f, indent=4)
        return {}

def _save_prefixes(prefixes):
    """Save server prefixes to file"""
    with open('./data/prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

def get_prefix(guild_id):
    """Get prefix for a specific guild"""
    guild_id = str(guild_id)  # Convert to string for JSON keys
    prefixes = _load_prefixes()
    return prefixes.get(guild_id, "!")  # Default to "!" if not found

def set_prefix(guild_id, prefix):
    """Set prefix for a specific guild"""
    guild_id = str(guild_id)  # Convert to string for JSON keys
    prefixes = _load_prefixes()
    prefixes[guild_id] = prefix
    _save_prefixes(prefixes)
    return True

def remove_prefix(guild_id):
    """Remove prefix for a specific guild"""
    guild_id = str(guild_id)  # Convert to string for JSON keys
    prefixes = _load_prefixes()
    if guild_id in prefixes:
        del prefixes[guild_id]
        _save_prefixes(prefixes)
        return True
    return False

# -------------------- NO-PREFIX MANAGEMENT --------------------

def _load_noprefix():
    """Load no-prefix users from file"""
    try:
        if not os.path.exists('./data'):
            os.makedirs('./data')
        
        if not os.path.exists('./data/noprefix.json'):
            with open('./data/noprefix.json', 'w') as f:
                json.dump({"users": []}, f, indent=4)
                return {"users": []}
        
        with open('./data/noprefix.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Create the file if it doesn't exist
        if not os.path.exists('./data'):
            os.makedirs('./data')
        
        with open('./data/noprefix.json', 'w') as f:
            json.dump({"users": []}, f, indent=4)
        return {"users": []}

def _save_noprefix(data):
    """Save no-prefix users to file"""
    with open('./data/noprefix.json', 'w') as f:
        json.dump(data, f, indent=4)

def has_noprefix(user_id):
    """Check if user has no-prefix permission"""
    user_id = int(user_id)  # Ensure it's an integer
    data = _load_noprefix()
    
    # Always allow owner and devs to use no-prefix
    if is_owner(user_id) or is_dev(user_id):
        return True
        
    return user_id in data.get("users", [])

def add_noprefix(user_id):
    """Add no-prefix permission for a user"""
    user_id = int(user_id)  # Ensure it's an integer
    data = _load_noprefix()
    
    if user_id in data.get("users", []):
        return False  # User already has no-prefix
        
    data["users"].append(user_id)
    _save_noprefix(data)
    return True

def remove_noprefix(user_id):
    """Remove no-prefix permission from a user"""
    user_id = int(user_id)  # Ensure it's an integer
    data = _load_noprefix()
    
    if user_id not in data.get("users", []):
        return False  # User doesn't have no-prefix
        
    data["users"].remove(user_id)
    _save_noprefix(data)
    return True

# -------------------- GUILD CONFIGURATION --------------------

def guild_config(guild_id: int, key: str = "", value: any = None, mode: str = "get"):
    """
    Handles guild configuration settings

    Args:
        guild_id (int): The guild ID.
        key (str): The configuration key.
        value (any, optional): The new value for the key. Defaults to None.
        mode (str, optional): The operation mode ("get" or "set"). Defaults to "get".

    Returns:
        The current or updated value for the key
    """
    file_path = f"database/{str(guild_id)}.json"
    os.makedirs("database", exist_ok=True)
    data = {}

    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        with open(file_path, "w") as f:
            data = {
                "mod_log_ch": None,
                "mod_cmd_log_ch": None,
                "msg_log_ch": None,
                "ticket_cmds": True,
                "ticket_log_ch": None,
                "autorole": None,
            }
            json.dump(data, f, indent=4)

    if mode == "get":
        return data.get(key)
    elif mode == "set":
        data[key] = value
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
        return value

# Create new db
def create(guild_id: int):
    """Create new guild database"""
    guild_config(guild_id=guild_id, mode="get")

# Delete db
def delete(guild_id: int):
    """Delete guild database"""
    os.remove(f"database/{str(guild_id)}.json")

# Mod log channel
def mod_log_ch(guild_id: int, channel_id: int = None, mode: str = "get"):
    """Get or set mod log channel"""
    return guild_config(guild_id, "mod_log_ch", channel_id, mode)

# Mod cmd log channel
def mod_cmd_log_ch(guild_id: int, channel_id: int = None, mode: str = "get"):
    """Get or set mod command log channel"""
    return guild_config(guild_id, "mod_cmd_log_ch", channel_id, mode)

# Message log channel
def msg_log_ch(guild_id: int, channel_id: int = None, mode: str = "get"):
    """Get or set message log channel"""
    return guild_config(guild_id, "msg_log_ch", channel_id, mode)

# Ticket cmds
def ticket_cmds(guild_id: int, status: bool = True, mode: str = "get"):
    """Get or set ticket commands status"""
    return guild_config(guild_id, "ticket_cmds", status, mode)

# Ticket log channel
def ticket_log_ch(guild_id: int, channel_id: int = None, mode: str = "get"):
    """Get or set ticket log channel"""
    return guild_config(guild_id, "ticket_log_ch", channel_id, mode)

# Autorole
def autorole(guild_id: int, role_id: int = None, mode: str = "get"):
    """Get or set autorole"""
    return guild_config(guild_id, "autorole", role_id, mode)

# -------------------- TEMP FILE --------------------

# Play channel ID
def play_ch_id(guild_id: int, channel_id: any = None, mode: str = "get"):
    """Get or set play channel ID"""
    if mode == "get":
        return temp_file_path.get(f"{str(guild_id)}-play_ch_id", None)
    elif mode == "set":
        temp_file_path.update({f"{str(guild_id)}-play_ch_id": channel_id})

# Play msg ID
def play_msg(guild_id: int, msg: any = None, mode: str = "get"):
    """Get or set play message"""
    match mode:
        case "get":
            return temp_file_path.get(f"{str(guild_id)}-play_msg", None)
        case "set":
            temp_file_path.update({f"{str(guild_id)}-play_msg": msg})

# Queue msg ID
def queue_msg(guild_id: int, msg: any = None, mode: str = "get"):
    """Get or set queue message"""
    match mode:
        case "get":
            if temp_file_path.__contains__(f"{str(guild_id)}-queue_msgs"):
                return temp_file_path.get(f"{str(guild_id)}-queue_msgs", None)
            else:
                return list()
        case "set":
            if temp_file_path.__contains__(f"{str(guild_id)}-queue_msgs"):
                temp_file_path[f"{str(guild_id)}-queue_msgs"].append(msg)
            else:
                temp_file_path.update({f"{str(guild_id)}-queue_msgs": [msg]})
        case "clear":
            temp_file_path.update({f"{str(guild_id)}-queue_msgs": []})

# Equalizer
def equalizer(guild_id: int, name: str = None, mode: str = "get"):
    """Get or set equalizer"""
    match mode:
        case "get":
            return temp_file_path.get(f"{str(guild_id)}-equalizer", None)
        case "set":
            temp_file_path.update({f"{str(guild_id)}-equalizer": name})