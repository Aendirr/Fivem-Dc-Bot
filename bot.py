import discord
from discord.ext import commands
import json
import asyncio
import os
from utils.helpers import load_config

config = load_config()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=config['prefix'], intents=intents)

bot.config = config

bot.ticket_data = {}

async def load_extensions():
    for filename in os.listdir('./events'):
        if filename.endswith('.py') and not filename.startswith('__'):
            try:
                await bot.load_extension(f'events.{filename[:-3]}')
                print(f'✅ Event yüklendi: {filename}')
            except Exception as e:
                print(f'❌ Event yüklenemedi {filename}: {e}')
    
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and not filename.startswith('__'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'✅ Cog yüklendi: {filename}')
            except Exception as e:
                print(f'❌ Cog yüklenemedi {filename}: {e}')

@bot.event
async def on_ready():
    print(f'{bot.user} olarak giriş yapıldı!')
    print(f'Bot ID: {bot.user.id}')
    print(f'Guild sayısı: {len(bot.guilds)}')

    try:
        guild = discord.Object(id=config['guild_id'])
        synced = await bot.tree.sync(guild=guild)
        print(f"{len(synced)} komut {config['guild_id']} sunucusunda senkronize edildi.")
    except Exception as e:
        print(f"Komut senkronizasyon hatası: {e}")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(config['token'])

if __name__ == "__main__":
    asyncio.run(main()) 