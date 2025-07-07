import discord
from discord.ext import commands
from discord import app_commands
from discord import ui
import json
import os
from typing import Optional
from utils.helpers import save_ticket_event, is_staff, create_embed

class TicketModal(discord.ui.Modal):
    def __init__(self, config):
        super().__init__(title="Ticket Oluştur", timeout=300)
        self.config = config
        
        questions = config['questions']
        
        self.user_id = discord.ui.TextInput(
            label=questions[0],
            placeholder="Örnek: 12345 - KarakterAdı",
            required=True,
            max_length=100
        )
        
        self.event_date = discord.ui.TextInput(
            label=questions[1],
            placeholder="Örnek: 15.12.2024 - Şehir Adı",
            required=True,
            max_length=100
        )
        
        self.other_players = discord.ui.TextInput(
            label=questions[2],
            placeholder="Örnek: 67890, 11111 (yoksa 'Yok' yazın)",
            required=True,
            max_length=200
        )
        
        self.event_summary = discord.ui.TextInput(
            label=questions[3],
            placeholder="Olayı detaylı bir şekilde açıklayın...",
            required=True,
            style=discord.TextStyle.paragraph,
            max_length=1000
        )
        
        self.streamable_video = discord.ui.TextInput(
            label=questions[4],
            placeholder="https://streamable.com/...",
            required=True,
            max_length=200
        )
        
        self.add_item(self.user_id)
        self.add_item(self.event_date)
        self.add_item(self.other_players)
        self.add_item(self.event_summary)
        self.add_item(self.streamable_video)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        
        existing_channel = discord.utils.get(guild.channels, name=f"{self.config['ticket_channel_prefix']}{user.name.lower()}")
        
        if existing_channel:
            await interaction.response.send_message(
                "❌ Zaten açık bir ticket'ınız bulunmaktadır!",
                ephemeral=True
            )
            return
        
        streamable_url = self.streamable_video.value.strip()
        if self.config['required_streamable'] and not streamable_url.startswith(self.config['streamable_url']):
            await interaction.response.send_message(
                self.config['missing_streamable_message'],
                ephemeral=True
            )
            return

        interaction.client.ticket_data[interaction.user.id] = {
            'user_id': self.user_id.value,
            'event_date': self.event_date.value,
            'other_players': self.other_players.value,
            'event_summary': self.event_summary.value,
            'streamable_video': streamable_url,
            'interaction': interaction
        }

        await self.create_ticket_channel(interaction)

    async def create_ticket_channel(self, interaction: discord.Interaction):
        try:
            guild = interaction.guild
            user = interaction.user
            
            category_id = int(self.config['ticket_category_id'])
            category = guild.get_channel(category_id)
            if not category:
                await interaction.response.send_message(
                    "Ticket kategorisi bulunamadı!",
                    ephemeral=True
                )
                return
            
            channel_name = f"{self.config['ticket_channel_prefix']}{user.name.lower()}"
            
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
            }
            
            admin_role_id = int(self.config['admin_role_id'])
            moderator_role_id = int(self.config['moderator_role_id'])
            admin_role = guild.get_role(admin_role_id)
            moderator_role = guild.get_role(moderator_role_id)
            
            if admin_role:
                overwrites[admin_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
            if moderator_role:
                overwrites[moderator_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
            
            channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites
            )
            
            ticket_role = guild.get_role(int(self.config['ticket_user_role_id']))
            if ticket_role and ticket_role not in user.roles:
                await user.add_roles(ticket_role, reason="Ticket açıldı")
            
            fields = interaction.client.ticket_data[user.id].copy()
            fields.pop("interaction", None)
            save_ticket_event(user.id, channel.id, {
                "type": "ticket_create",
                "user": user.id,
                "channel": channel.id,
                "fields": fields,
                "timestamp": str(interaction.created_at)
            })
            
            embed = create_embed(
                title="🎫 Yeni Ticket",
                description=f"**Kullanıcı:** {user.mention}",
                color=self.config['embed_color']
            )
            
            data = interaction.client.ticket_data[user.id]
            embed.add_field(name="Oyun ID - Karakter", value=data['user_id'], inline=False)
            embed.add_field(name="Olay Tarihi ve Yeri", value=data['event_date'], inline=False)
            embed.add_field(name="Diğer Oyuncular", value=data['other_players'], inline=False)
            embed.add_field(name="Olay Özeti", value=data['event_summary'], inline=False)
            embed.add_field(name="Streamable Video", value=data['streamable_video'], inline=False)
            embed.set_footer(text=f"Ticket ID: {channel.id}")
            
            view = TicketPunishView(user.id, data['other_players'], ticket_id=channel.id, config=self.config)
            await channel.send(embed=embed, view=view)
            
            await interaction.response.send_message(
                f"{self.config['ticket_created_message']}\n\n🎫 Ticket kanalınız: {channel.mention}",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Ticket oluşturulurken hata oluştu: {str(e)}",
                ephemeral=True
            )

class TicketView(discord.ui.View):
    def __init__(self, config):
        super().__init__(timeout=None)
        self.config = config

    @discord.ui.button(
        label="Ticket Aç",
        style=discord.ButtonStyle.danger,
        custom_id="create_ticket"
    )
    async def create_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = TicketModal(self.config)
        await interaction.response.send_modal(modal)

class TicketPunishView(discord.ui.View):
    def __init__(self, ticket_owner_id, other_players, ticket_id=None, staff_only=True, config=None):
        super().__init__(timeout=None)
        self.ticket_owner_id = ticket_owner_id
        self.other_players = other_players
        self.staff_only = staff_only
        self.ticket_id = ticket_id
        self.config = config
        self.add_item(PunishmentSelect(ticket_owner_id, ticket_id=ticket_id, config=config))
        self.add_item(TicketRelatedButton(other_players, config=config))
        self.add_item(CloseTicketButton(config=config))

class PunishmentSelect(discord.ui.Select):
    def __init__(self, user_id, ticket_id=None, config=None):
        options = []
        for key, role_id in config['punishment_roles'].items():
            label = key.upper()
            if key.startswith('uyari'):
                label = f"⚠️ {key[-1]} UYARI"
            elif key.startswith('ckpoint'):
                label = f"💀 -{key[-1]} CK Point"
            elif key == 'blacklist':
                label = "❌ Blacklist"
            elif key.endswith('gunwl'):
                label = f"= {key[0]} GÜN WHITELIST"
            options.append(discord.SelectOption(label=label, value=key))
        super().__init__(placeholder="Ceza seçin...", min_values=1, max_values=1, options=options)
        self.user_id = int(user_id)
        self.ticket_id = ticket_id
        self.config = config

    async def callback(self, interaction: discord.Interaction):
        if not is_staff(interaction.user, self.config):
            await interaction.response.send_message("Bu menüyü kullanma yetkiniz yok!", ephemeral=True)
            return
        
        punishment_key = self.values[0]
        role_id = int(self.config['punishment_roles'][punishment_key])
        member = interaction.guild.get_member(self.user_id)
        
        if not member:
            try:
                member = await interaction.guild.fetch_member(self.user_id)
            except Exception as e:
                member = None
        
        role = interaction.guild.get_role(role_id)
        
        if not member:
            await interaction.response.send_message(f"Kullanıcı bulunamadı! (ID: {self.user_id})", ephemeral=True)
            return
        
        if not role:
            await interaction.response.send_message(f"Rol bulunamadı! (ID: {role_id})", ephemeral=True)
            return
        
        try:
            if role in member.roles:
                await member.remove_roles(role, reason="Ticket ceza menüsü ile kaldırıldı")
                await interaction.response.send_message(f"{member.mention} kullanıcısından {role.name} rolü kaldırıldı.", ephemeral=True)
                save_ticket_event(self.user_id, self.ticket_id, {
                    "type": "punishment_remove",
                    "role": role_id,
                    "by": interaction.user.id,
                    "timestamp": str(interaction.created_at)
                })
            else:
                await member.add_roles(role, reason="Ticket ceza menüsü ile verildi")
                await interaction.response.send_message(f"{member.mention} kullanıcısına {role.name} rolü verildi.", ephemeral=True)
                save_ticket_event(self.user_id, self.ticket_id, {
                    "type": "punishment_add",
                    "role": role_id,
                    "by": interaction.user.id,
                    "timestamp": str(interaction.created_at)
                })
        except discord.Forbidden:
            await interaction.response.send_message("Botun bu rolü yönetme yetkisi yok!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Bilinmeyen hata: {e}", ephemeral=True)

class TicketRelatedButton(discord.ui.Button):
    def __init__(self, other_players, config=None):
        super().__init__(label="Olay ile ilgili kişiler", style=discord.ButtonStyle.primary)
        self.other_players = other_players
        self.config = config

    async def callback(self, interaction: discord.Interaction):
        if not is_staff(interaction.user, self.config):
            await interaction.response.send_message("Bu butonu kullanma yetkiniz yok!", ephemeral=True)
            return
        
        names = [name.strip().replace(" ", "").lower() for name in self.other_players.split(",") if name.strip()]
        added = []
        
        for member in interaction.guild.members:
            member_names = [member.name.replace(" ", "").lower(), member.display_name.replace(" ", "").lower()]
            if any(n in names for n in member_names):
                overwrite = interaction.channel.overwrites_for(member)
                overwrite.read_messages = True
                await interaction.channel.set_permissions(member, overwrite=overwrite)
                added.append(member.mention)
        
        if added:
            await interaction.response.send_message(f"Olay ile ilgili kişilere kanal erişimi verildi: {', '.join(added)}", ephemeral=True)
        else:
            await interaction.response.send_message("Hiçbir kullanıcı bulunamadı!", ephemeral=True)

class CloseTicketButton(discord.ui.Button):
    def __init__(self, config=None):
        super().__init__(label="Ticket'ı Kapat", style=discord.ButtonStyle.danger)
        self.config = config

    async def callback(self, interaction: discord.Interaction):
        if not is_staff(interaction.user, self.config):
            await interaction.response.send_message("Bu ticket'ı kapatma yetkiniz yok!", ephemeral=True)
            return
        
        await interaction.response.send_message("Ticket kapatıldı.", ephemeral=True)
        channel = interaction.channel
        
        ticket_owner_id = None
        for user_id, data in list(interaction.client.ticket_data.items()):
            if 'interaction' in data and data['interaction'].channel == channel:
                ticket_owner_id = user_id
                del interaction.client.ticket_data[user_id]
                break
        
        if ticket_owner_id:
            member = interaction.guild.get_member(int(ticket_owner_id))
            if not member:
                try:
                    member = await interaction.guild.fetch_member(int(ticket_owner_id))
                except Exception as e:
                    member = None
            
            role = interaction.guild.get_role(int(self.config['ticket_user_role_id']))
            if member and role and role in member.roles:
                try:
                    await member.remove_roles(role, reason="Ticket kapatıldı")
                    save_ticket_event(ticket_owner_id, channel.id, {
                        "type": "ticket_close",
                        "by": interaction.user.id,
                        "timestamp": str(interaction.created_at)
                    })
                except Exception as e:
                    print(f"[TicketBot] Rol kaldırılamadı: {e}")
            elif not member:
                print(f"[TicketBot] Ticket kapatılırken kullanıcı bulunamadı: {ticket_owner_id}")
        
        await channel.send(self.config['ticket_closed_message'])
        await channel.delete()

class TranscriptSelectView(ui.View):
    def __init__(self, user_id, files, config):
        super().__init__(timeout=60)
        self.add_item(TranscriptSelect(user_id, files, config))

class TranscriptSelect(ui.Select):
    def __init__(self, user_id, files, config):
        options = []
        for fname in files:
            ticket_id = fname.split('_')[1].split('.')[0]
            label = f"Ticket ID: {ticket_id}"
            options.append(discord.SelectOption(label=label, value=fname))
        super().__init__(placeholder="Bir ticket seçin...", min_values=1, max_values=1, options=options)
        self.user_id = user_id
        self.config = config

    async def callback(self, interaction: discord.Interaction):
        await send_transcript(interaction, self.user_id, self.values[0])

async def send_transcript(interaction, user_id, filename):
    path = os.path.join('data', filename)
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    lines = []
    for event in data["events"]:
        if event["type"] == "message":
            lines.append(f'<@{event["author"]}>: {event["content"]}')
        elif event["type"] == "punishment_add":
            lines.append(f'Rol verildi: <@&{event["role"]}> (by <@{event["by"]}>)')
        elif event["type"] == "punishment_remove":
            lines.append(f'Rol kaldırıldı: <@&{event["role"]}> (by <@{event["by"]}>)')
        elif event["type"] == "ticket_create":
            lines.append(f'Ticket açıldı: <@{event["user"]}>')
        elif event["type"] == "ticket_close":
            lines.append(f'Ticket kapatıldı (by <@{event["by"]}>)')
    
    transcript = '\n'.join(lines)
    if len(transcript) < 1900:
        await interaction.response.send_message(f'```{transcript}```', ephemeral=True)
    else:
        with open('data/temp_transcript.txt', 'w', encoding='utf-8') as f:
            f.write(transcript)
        await interaction.response.send_message(file=discord.File('data/temp_transcript.txt'), ephemeral=True)

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config

    @app_commands.command(name="ticket", description="Ticket sistemi embed'ini oluşturur")
    @app_commands.describe(channel="Ticket embed'inin gönderileceği kanal")
    async def ticket(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        user_roles = [role.id for role in interaction.user.roles]
        admin_role_id = int(self.config['admin_role_id'])
        moderator_role_id = int(self.config['moderator_role_id'])
        
        if admin_role_id not in user_roles and moderator_role_id not in user_roles:
            await interaction.response.send_message(
                "Bu komutu kullanma yetkiniz yok!",
                ephemeral=True
            )
            return

        target_channel = channel or interaction.channel
        
        embed = create_embed(
            title=self.config['embed_title'],
            description=self.config['embed_description'],
            color=self.config['embed_color'],
            thumbnail_url=self.config['embed_thumbnail_url']
        )
        
        view = TicketView(self.config)
        
        await target_channel.send(embed=embed, view=view)
        await interaction.response.send_message(
            f"Ticket sistemi {target_channel.mention} kanalında oluşturuldu!",
            ephemeral=True
        )

    @app_commands.command(name="dataticket", description="Kullanıcının ticket transkriptini getirir")
    @app_commands.describe(user_id="Kullanıcı ID")
    async def dataticket(self, interaction: discord.Interaction, user_id: str):
        if not is_staff(interaction.user, self.config):
            await interaction.response.send_message("Bu komutu kullanma yetkiniz yok!", ephemeral=True)
            return
        
        files = [f for f in os.listdir('data') if f.startswith(f'{user_id}_') and f.endswith('.json')]
        if not files:
            await interaction.response.send_message("Bu kullanıcıya ait ticket kaydı bulunamadı!", ephemeral=True)
            return
        
        if len(files) == 1:
            await send_transcript(interaction, user_id, files[0])
            return
        
        files.sort(reverse=True)
        view = TranscriptSelectView(user_id, files, self.config)
        await interaction.response.send_message("Lütfen görmek istediğiniz ticketı seçin:", view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketSystem(bot)) 