import discord
from discord.ext import commands
import asyncio
import random

class ReadyEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} olarak giriş yapıldı!')
        
        try:
            synced = await self.bot.tree.sync()
            print(f"{len(synced)} komut global olarak senkronize edildi.")
        except Exception as e:
            print(f"Komut senkronizasyon hatası: {e}")
        
        channel_id = int(self.config['ses_channel_id'])
        channel = self.bot.get_channel(channel_id)
        if channel:
            try:
                await channel.connect()
                print(f"Ses kanalına bağlanıldı: {channel.name}")
            except Exception as e:
                print(f"Ses kanalına bağlanma hatası: {e}")
        
        self.bot.loop.create_task(self.change_presence())

    async def change_presence(self):
        await self.bot.wait_until_ready()
        
        statuses = [
            "👨‍💻 Made by Aendir",
            "👨‍💻 Workin For QBCore"
        ]
        
        while not self.bot.is_closed():
            status = random.choice(statuses)
            await self.bot.change_presence(activity=discord.Game(name=status))
            await asyncio.sleep(5)

async def setup(bot):
    await bot.add_cog(ReadyEvent(bot)) 