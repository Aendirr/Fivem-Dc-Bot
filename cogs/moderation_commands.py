import discord
from discord.ext import commands
from discord import app_commands
from utils.helpers import is_staff, has_staff_role, create_embed

class ModerationCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config

    @app_commands.command(name="kayital", description="Kullanıcıyı kayıt eder")
    @app_commands.describe(user="Kayıt edilecek kullanıcı")
    async def kayital(self, interaction: discord.Interaction, user: discord.Member):
        if not has_staff_role(interaction.user, self.config):
            await interaction.response.send_message("Bu komutu kullanma yetkiniz yok!", ephemeral=True)
            return
        
        try:
            rol = discord.utils.get(interaction.guild.roles, name=self.config['isim_role'])
            rol2 = discord.utils.get(interaction.guild.roles, name=self.config['kayitsiz_role'])
            
            if rol:
                await user.add_roles(rol)
            if rol2:
                await user.remove_roles(rol2)
            
            await interaction.response.send_message(f"✅ {user.mention} başarıyla kayıt edildi!", ephemeral=True)
            
            log_channel = self.bot.get_channel(int(self.config['log_channel_id']))
            if log_channel:
                await log_channel.send(f"<@!{interaction.user.id}> isimli yetkili , {user.mention} isimli Oyuncuya {rol.name if rol else 'rol'} permi verdi!")
        
        except Exception as e:
            await interaction.response.send_message(f"Kayıt işlemi sırasında hata oluştu: {e}", ephemeral=True)

    @app_commands.command(name="bayan", description="Kullanıcıya bayan rolü verir")
    @app_commands.describe(user="Rol verilecek kullanıcı")
    async def bayan(self, interaction: discord.Interaction, user: discord.Member):
        if not has_staff_role(interaction.user, self.config):
            await interaction.response.send_message("Bu komutu kullanma yetkiniz yok!", ephemeral=True)
            return
        
        try:
            rol = discord.utils.get(interaction.guild.roles, name=self.config['lady_role'])
            if rol:
                await user.add_roles(rol)
                await interaction.response.send_message(f"✅ {user.mention} kullanıcısına {rol.name} rolü verildi!", ephemeral=True)
                
                log_channel = self.bot.get_channel(int(self.config['log_channel_id']))
                if log_channel:
                    await log_channel.send(f"<@!{interaction.user.id}> isimli yetkili , {user.mention} isimli Oyuncuya {rol.name} permi verdi!")
            else:
                await interaction.response.send_message("Bayan rolü bulunamadı!", ephemeral=True)
        
        except Exception as e:
            await interaction.response.send_message(f"Rol verme işlemi sırasında hata oluştu: {e}", ephemeral=True)

    @app_commands.command(name="erkek", description="Kullanıcıya erkek rolü verir")
    @app_commands.describe(user="Rol verilecek kullanıcı")
    async def erkek(self, interaction: discord.Interaction, user: discord.Member):
        if not has_staff_role(interaction.user, self.config):
            await interaction.response.send_message("Bu komutu kullanma yetkiniz yok!", ephemeral=True)
            return
        
        try:
            erkek_role_name = "Erkek"
            rol = discord.utils.get(interaction.guild.roles, name=erkek_role_name)
            if rol:
                await user.add_roles(rol)
                await interaction.response.send_message(f"✅ {user.mention} kullanıcısına {rol.name} rolü verildi!", ephemeral=True)
                
                log_channel = self.bot.get_channel(int(self.config['log_channel_id']))
                if log_channel:
                    await log_channel.send(f"<@!{interaction.user.id}> isimli yetkili , {user.mention} isimli Oyuncuya {rol.name} permi verdi!")
            else:
                await interaction.response.send_message("Erkek rolü bulunamadı!", ephemeral=True)
        
        except Exception as e:
            await interaction.response.send_message(f"Rol verme işlemi sırasında hata oluştu: {e}", ephemeral=True)

    @app_commands.command(name="isim", description="Kullanıcının ismini değiştirir")
    @app_commands.describe(user="İsmi değiştirilecek kullanıcı", new_name="Yeni isim")
    async def isim(self, interaction: discord.Interaction, user: discord.Member, new_name: str):
        if not has_staff_role(interaction.user, self.config):
            await interaction.response.send_message("Bu komutu kullanma yetkiniz yok!", ephemeral=True)
            return
        
        try:
            rol_id = int(self.config['admin_role_id'])
            rol2 = discord.utils.get(interaction.guild.roles, name=self.config['kayitsiz_role'])
            rol = user.guild.get_role(rol_id)
            
            new_name_parts = new_name.split()
            if len(new_name_parts) >= 2:
                new_nickname = f"{new_name_parts[0]} {new_name_parts[1]}"
                await user.edit(nick=new_nickname)
                
                if rol:
                    await user.add_roles(rol)
                if rol2:
                    await user.remove_roles(rol2)
                
                await interaction.response.send_message(f"✅ {user.mention} kullanıcısının ismi '{new_nickname}' olarak değiştirildi!", ephemeral=True)
                
                log_channel = self.bot.get_channel(int(self.config['log_channel_id']))
                if log_channel:
                    await log_channel.send(f"<@!{interaction.user.id}> isimli yetkili , bu discord idye sahip kullanıcının: {user.id} ismini {user.mention} verdi! Ve {rol.name if rol else 'rol'} verildi..")
            else:
                await interaction.response.send_message("İsim Soyisim Giriniz...", ephemeral=True)
        
        except Exception as e:
            await interaction.response.send_message(f"İsim değiştirme işlemi sırasında hata oluştu: {e}", ephemeral=True)

    @app_commands.command(name="avatar", description="Kullanıcının avatarını gösterir")
    @app_commands.describe(user="Avatarı gösterilecek kullanıcı")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member):
        try:
            user_avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
            await interaction.response.send_message(user_avatar_url, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Avatar gösterilirken hata oluştu: {e}", ephemeral=True)

    @app_commands.command(name="clear", description="Belirtilen sayıda mesaj siler")
    @app_commands.describe(amount="Silinecek mesaj sayısı")
    async def clear(self, interaction: discord.Interaction, amount: int):
        if not has_staff_role(interaction.user, self.config):
            await interaction.response.send_message("Bu komutu kullanma yetkiniz yok!", ephemeral=True)
            return
        
        try:
            await interaction.channel.purge(limit=amount)
            await interaction.response.send_message(f"✅ Başarıyla {amount} tane mesaj silindi", ephemeral=True, delete_after=2)
        except Exception as e:
            await interaction.response.send_message(f"Mesaj silme işlemi sırasında hata oluştu: {e}", ephemeral=True)

    @app_commands.command(name="kanalsil", description="Belirtilen isimdeki kanalı siler")
    @app_commands.describe(channel_name="Silinecek kanalın adı")
    async def kanalsil(self, interaction: discord.Interaction, channel_name: str):
        if not has_staff_role(interaction.user, self.config):
            await interaction.response.send_message("Bu komutu kullanma yetkiniz yok!", ephemeral=True)
            return
        
        try:
            channel = discord.utils.get(interaction.guild.channels, name=channel_name)
            
            if channel is not None:
                await channel.delete()
                await interaction.response.send_message(f"✅ {channel_name} kanalı başarıyla silindi.", ephemeral=True)
            else:
                await interaction.response.send_message("Belirtilen isimde bir kanal bulunamadı.", ephemeral=True)
        
        except discord.Forbidden:
            await interaction.response.send_message("Bu işlem için yeterli iznim yok.", ephemeral=True)
        except discord.NotFound:
            await interaction.response.send_message("Belirtilen kanal bulunamadı.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("Kanal silinirken bir hata oluştu.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Kanal silme işlemi sırasında hata oluştu: {e}", ephemeral=True)

    @app_commands.command(name="join", description="Ses kanalına katılır")
    async def join(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message("Bir ses kanalında olmalısınız!", ephemeral=True)
            return
        
        try:
            channel = interaction.user.voice.channel
            await channel.connect()
            await interaction.response.send_message(f"✅ {channel.name} kanalına katıldım!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Ses kanalına katılırken hata oluştu: {e}", ephemeral=True)

    @app_commands.command(name="leave", description="Ses kanalından ayrılır")
    async def leave(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client:
            await interaction.response.send_message("Zaten bir ses kanalında değilim!", ephemeral=True)
            return
        
        try:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("✅ Ses kanalından ayrıldım!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Ses kanalından ayrılırken hata oluştu: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ModerationCommands(bot)) 