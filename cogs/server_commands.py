import discord
from discord.ext import commands
from discord import app_commands
from utils.helpers import is_staff, has_staff_role, create_embed

class ServerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config

    @app_commands.command(name="aktif", description="Sunucu aktif durumunu bildirir")
    async def aktif(self, interaction: discord.Interaction):
        if not has_staff_role(interaction.user, self.config):
            await interaction.response.send_message("Bu komutu kullanma yetkiniz yok!", ephemeral=True)
            return
        
        aktifembed = discord.Embed(description="Sunucu Aktiftir! ✅")
        aktifembed.set_author(name="Discord Adresimiz", url=f"{self.config['discord_url']}", icon_url=self.config['server_icon'])
        aktifembed.set_thumbnail(url=self.config['aktif_image'])
        aktifembed.set_image(url=self.config['aktif_image'])
        aktifembed.add_field(name=f'Sunucu Bağlantı URL\'si : {self.config["server_ip"]} ', value='🎬') 
        aktifembed.add_field(name=f'{interaction.guild.name} Herkese iyi seyirler diler.', value='🎉', inline=False)
        
        await interaction.response.send_message(embed=aktifembed)

    @app_commands.command(name="restart", description="Sunucu restart durumunu bildirir")
    async def restart(self, interaction: discord.Interaction):
        if not has_staff_role(interaction.user, self.config):
            await interaction.response.send_message("Bu komutu kullanma yetkiniz yok!", ephemeral=True)
            return
        
        restartembed = discord.Embed(description="Sunucumuza Restart Atılıyor ❗️❗️") 
        restartembed.set_thumbnail(url=self.config['restart_image'])
        restartembed.set_image(url=self.config['restart_image'])
        restartembed.set_author(name="Discord Adresimiz", url=f"{self.config['discord_url']}", icon_url=self.config['server_icon'])
        restartembed.add_field(name=f'Datalarınızın Zarar Görmemesi İçin Lütfen Oyundan Çıkış Yapalım', value="Bizi Tercih Ettiğiniz İçin Teşekkür Ederiz", inline=False) 
        restartembed.add_field(name=f'{interaction.guild.name} Ailesi', value='💖', inline=False)
        
        await interaction.response.send_message(embed=restartembed)

    @app_commands.command(name="bakim", description="Sunucu bakım durumunu bildirir")
    async def bakim(self, interaction: discord.Interaction):
        if not has_staff_role(interaction.user, self.config):
            await interaction.response.send_message("Bu komutu kullanma yetkiniz yok!", ephemeral=True)
            return
        
        bakımembed = discord.Embed(description="Sunucumuz Kısa Süreliğine Bakıma Alınmıştır ❗️❗️")
        bakımembed.set_thumbnail(url=self.config['bakim_image'])
        bakımembed.set_author(name="BAKIMDAYIZ", url=f"{self.config['discord_url']}", icon_url=self.config['server_icon'])
        bakımembed.set_image(url=self.config['bakim_image'])
        bakımembed.add_field(name=f'En Kısa Sürede Tekrar Aktif Verilecektir', value="Bizi Tercih Ettiğiniz İçin Teşekkür Ederiz", inline=False) 
        bakımembed.add_field(name=f'{interaction.guild.name} Ailesi', value='💖', inline=False)
        
        await interaction.response.send_message(embed=bakımembed)

    @app_commands.command(name="ip", description="Sunucu IP adresini gösterir")
    async def ip(self, interaction: discord.Interaction):
        # Whitelist rolü kontrolü
        whitelist_role = discord.utils.get(interaction.guild.roles, name=self.config['whitelist_role'])
        if not whitelist_role or whitelist_role not in interaction.user.roles:
            await interaction.response.send_message('Rolü olmayanlar ip talebinde bulunamaz!', ephemeral=True)
            return
        
        embed = create_embed(
            title=f'{interaction.user.name} Sunucuya katılmak için linkten direkt giriş sağlayabilirsiniz.',
            description=self.config['server_ip'],
            color=0
        )
        embed.set_footer(text=f"{interaction.guild.name}")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerCommands(bot)) 