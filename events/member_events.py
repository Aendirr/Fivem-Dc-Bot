import discord
from discord.ext import commands
import datetime
from utils.helpers import save_ticket_event

class MemberEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Üye sunucuya katıldığında çalışır"""
        date_format = "%x, %X"
        
        # Oto rol ver
        rol_id = int(self.config['ticket_user_role_id'])
        rol = member.guild.get_role(rol_id)
        new_name = "IC/OOC ISIM"
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        
        # Giriş embed'i oluştur
        girisembed = discord.Embed(title=f"discord id : {member.id}")
        girisembed.set_thumbnail(url=avatar_url)
        girisembed.set_author(name=member.name, icon_url=avatar_url)
        girisembed.add_field(name="Hesap Kuruluş Tarihi: ", value=member.created_at.strftime(date_format))
        girisembed.set_footer(text=f"{member.guild.name}", icon_url=avatar_url)
        
        # Giriş kanalına gönder
        giriskanal = self.bot.get_channel(int(self.config['giris_channel_id']))
        if giriskanal:
            await giriskanal.send(member.mention, embed=girisembed)
        
        # Rol ver ve isim değiştir
        if rol:
            await member.add_roles(rol)
        await member.edit(nick=new_name)
        
        print(f'{member.name} Sunucuya Katıldı.')
        print(f'{member.name} kullanıcısına {rol.name if rol else "rol"} rolü verildi.')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Üye sunucudan çıktığında çalışır"""
        membercikis = datetime.datetime.now()
        membercikistarihi = membercikis.strftime("%x, %X")
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        
        # Çıkış embed'i oluştur
        cikisembed = discord.Embed(title=f"Bir Kullanıcı Sunucudan Çıktı")
        cikisembed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=avatar_url)
        cikisembed.set_thumbnail(url=avatar_url)
        cikisembed.add_field(name="Sunucudan Ayrılma Tarihi", value=f"{membercikistarihi}", inline=False)
        cikisembed.add_field(name="Kullanıcı Bilgileri:", value=f"{member.name}#{member.discriminator}  -  {member.id}", inline=False)
        cikisembed.set_footer(text=f"{member.guild.name}", icon_url=f"{member.guild.icon.url}")
        
        # Çıkış kanalına gönder
        cikiskanal = self.bot.get_channel(int(self.config['cikis_channel_id']))
        if cikiskanal:
            await cikiskanal.send(member.mention, embed=cikisembed)
        
        print(f'{member.name} Sunucudan Ayrıldı.')

    @commands.Cog.listener()
    async def on_message(self, message):
        """Mesaj gönderildiğinde çalışır"""
        if message.author.bot:
            return
        
        # Ticket kanalı ise ve data varsa kaydet
        if message.channel.name.startswith(self.config['ticket_channel_prefix']):
            user_id = None
            ticket_id = message.channel.id
            
            # Ticket sahibini bul
            for uid, data in self.bot.ticket_data.items():
                if 'interaction' in data and data['interaction'].channel.id == ticket_id:
                    user_id = uid
                    break
            
            if user_id:
                save_ticket_event(user_id, ticket_id, {
                    "type": "message",
                    "author": message.author.id,
                    "content": message.content,
                    "timestamp": str(message.created_at)
                })
        
        # Kayıt kanalı kontrolü
        if message.channel.id == int(self.config['kayit_channel_id']) and not message.author.bot:
            await self.handle_registration(message)
        
        await self.bot.process_commands(message)

    async def handle_registration(self, message):
        """Kayıt kanalında mesaj gönderildiğinde çalışır"""
        isim_soyisim = message.content.strip()
        
        if len(isim_soyisim.split()) < 2:
            await message.channel.send(f"{message.author.mention}, lütfen ad ve soyad yazınız.")
            return

        try:
            # Kullanıcı adını güncelle
            await message.author.edit(nick=isim_soyisim)
            
            guild = message.guild
            rol_yeni = discord.utils.get(guild.roles, name=self.config['whitelist_role'])
            rol_eski = discord.utils.get(guild.roles, name=self.config['isim_role'])
            
            if rol_yeni:
                await message.author.add_roles(rol_yeni)
            if rol_eski:
                await message.author.remove_roles(rol_eski)
            
            await message.channel.send(f"{message.author.mention}, başarıyla kayıt oldunuz!")
        
        except discord.Forbidden:
            await message.channel.send(f"{message.author.mention}, isim değişikliği veya rol ayarlamak için yetkim yok.")
        except discord.HTTPException as e:
            await message.channel.send(f"Bir hata oluştu: {e}")

async def setup(bot):
    await bot.add_cog(MemberEvents(bot)) 