import json
import os
import discord
from typing import Optional

def load_config():
    """Config dosyasını yükler"""
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_ticket_event(user_id, ticket_id, event):
    """Ticket olaylarını kaydeder"""
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
    """Kullanıcının staff olup olmadığını kontrol eder"""
    admin_role_id = int(config['admin_role_id'])
    moderator_role_id = int(config['moderator_role_id'])
    # Belirtilen rol ID'sine sahip kullanıcılar staff olarak kabul edilir
    return any(role.id == admin_role_id or role.id == moderator_role_id for role in member.roles)

def has_staff_role(member, config):
    """Kullanıcının belirtilen staff rolüne sahip olup olmadığını kontrol eder"""
    staff_role_id = int(config['admin_role_id'])  # Aynı rol ID'si kullanılıyor
    return any(role.id == staff_role_id for role in member.roles)

def has_permission(member, permission_name, config):
    """Kullanıcının belirli bir yetkiye sahip olup olmadığını kontrol eder"""
    if permission_name == "manage_guild":
        return member.guild_permissions.manage_guild
    elif permission_name == "manage_nicknames":
        return member.guild_permissions.manage_nicknames
    elif permission_name == "kick_members":
        return member.guild_permissions.kick_members
    return False

def get_role_by_name(guild, role_name):
    """Rol adına göre rol döndürür"""
    return discord.utils.get(guild.roles, name=role_name)

def create_embed(title, description, color, thumbnail_url=None, footer_text=None):
    """Embed oluşturur"""
    embed = discord.Embed(title=title, description=description, color=color)
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    if footer_text:
        embed.set_footer(text=footer_text)
    return embed 