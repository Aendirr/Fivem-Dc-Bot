import json
import os
import discord
from typing import Optional

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_ticket_event(user_id, ticket_id, event):
    os.makedirs('data', exist_ok=True)
    path = f'data/{user_id}_{ticket_id}.json'
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {"events": []}
    data["events"].append(event)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_staff(member, config):
    admin_role_id = int(config['admin_role_id'])
    moderator_role_id = int(config['moderator_role_id'])
    return any(role.id == admin_role_id or role.id == moderator_role_id for role in member.roles)

def has_staff_role(member, config):
    staff_role_id = int(config['admin_role_id'])
    return any(role.id == staff_role_id for role in member.roles)

def has_permission(member, permission_name, config):
    if permission_name == "manage_guild":
        return member.guild_permissions.manage_guild
    elif permission_name == "manage_nicknames":
        return member.guild_permissions.manage_nicknames
    elif permission_name == "kick_members":
        return member.guild_permissions.kick_members
    return False

def get_role_by_name(guild, role_name):
    return discord.utils.get(guild.roles, name=role_name)

def create_embed(title, description, color, thumbnail_url=None, footer_text=None):
    embed = discord.Embed(title=title, description=description, color=color)
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    if footer_text:
        embed.set_footer(text=footer_text)
    return embed 