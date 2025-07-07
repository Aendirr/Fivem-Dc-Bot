import discord
from discord.ext import commands
from discord import app_commands
from discord import ui
import json
import os
from typing import Optional

class MulakatModal(discord.ui.Modal):
    def __init__(self, page_index, questions, config):
        super().__init__(title=f"Hard RP Soruları - Sayfa {page_index + 1}", timeout=600)
        self.page_index = page_index
        self.questions = questions
        self.config = config
        for i, question in enumerate(questions):
            label = (question[:42] + "...") if len(question) > 45 else question
            text_input = discord.ui.TextInput(
                label=label,
                placeholder="Cevabınızı buraya yazın...",
                required=True,
                style=discord.TextStyle.paragraph,
                max_length=1000
            )
            self.add_item(text_input)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        # Kullanıcıya özel cevapları başlat
        if not hasattr(interaction.client, 'mulakat_responses'):
            interaction.client.mulakat_responses = {}
        if user_id not in interaction.client.mulakat_responses or self.page_index == 0:
            interaction.client.mulakat_responses[user_id] = []
        # Cevapları kaydet
        responses = {}
        for i, question in enumerate(self.questions):
            responses[question] = self.children[i].value
        page_data = {
            "page": self.page_index + 1,
            "responses": responses
        }
        # Aynı sayfa tekrar submit edilirse üzerine yazmasın diye kontrol
        if len(interaction.client.mulakat_responses[user_id]) == self.page_index:
            interaction.client.mulakat_responses[user_id].append(page_data)
        else:
            interaction.client.mulakat_responses[user_id][self.page_index] = page_data
        # Sonraki sayfa var mı?
        total_pages = 4
        if self.page_index < total_pages - 1:
            view = MulakatContinueView(self.page_index + 1, self.config)
            await interaction.response.send_message(
                f"Sayfa {self.page_index + 1} cevaplarınız kaydedildi. Sonraki sayfa için aşağıdaki butona tıklayın.",
                view=view,
                ephemeral=True
            )
        else:
            await self.complete_mulakat(interaction, user_id)

    async def complete_mulakat(self, interaction: discord.Interaction, user_id: str):
        final_data = {
            "discord_id": interaction.user.id,
            "discord_name": str(interaction.user),
            "responses": interaction.client.mulakat_responses[user_id]
        }
        os.makedirs('./responses', exist_ok=True)
        final_json_path = f'./responses/{user_id}_mulakat_final.json'
        with open(final_json_path, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        mulakat_channel_id = int(self.config.get('mulakat_channel_id', '1388307897099878410'))
        channel = interaction.guild.get_channel(mulakat_channel_id)
        # --- Embed ile okunabilir gönderim ---
        if channel:
            try:
                embed = discord.Embed(
                    title=f"Mülakat Cevapları - {interaction.user}",
                    description=f"Kullanıcı: <@{interaction.user.id}>\nDiscord ID: {interaction.user.id}",
                    color=0x3498db
                )
                for page in final_data["responses"]:
                    sayfa = page["page"]
                    cevaplar = page["responses"]
                    value = ""
                    for soru, cevap in cevaplar.items():
                        value += f"**{soru}**\n{cevap}\n\n"
                    embed.add_field(name=f"Sayfa {sayfa}", value=value[:1024], inline=False)
                await channel.send(embed=embed)
                # await channel.send(file=discord.File(final_json_path, f'{user_id}_mulakat_final.json'))  # Artık dosya gönderilmeyecek
            except Exception as e:
                print(f"Mülakat kanalına gönderme hatası: {e}")
        try:
            role_to_add_id = int(self.config.get('mulakat_role_to_add', '1330382259395756094'))
            role_to_remove_id = int(self.config.get('mulakat_role_to_remove', '979515873675071488'))
            role_to_add = interaction.guild.get_role(role_to_add_id)
            role_to_remove = interaction.guild.get_role(role_to_remove_id)
            if role_to_add:
                await interaction.user.add_roles(role_to_add, reason="Mülakat tamamlandı")
            if role_to_remove:
                await interaction.user.remove_roles(role_to_remove, reason="Mülakat tamamlandı")
        except Exception as e:
            print(f"Rol güncelleme hatası: {e}")
        await interaction.response.send_message(
            "✅ Tüm cevaplarınız kaydedildi ve yeni rol verildi. Mülakatınız tamamlandı!",
            ephemeral=True
        )
        if user_id in interaction.client.mulakat_responses:
            del interaction.client.mulakat_responses[user_id]

class MulakatContinueView(discord.ui.View):
    def __init__(self, next_page, config):
        super().__init__(timeout=300)
        self.next_page = next_page
        self.config = config
    @discord.ui.button(label="Sonraki Sayfa", style=discord.ButtonStyle.primary)
    async def continue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        questions = self.config['mulakat_questions']
        page_questions = [
            questions[0:5],
            questions[5:10],
            questions[10:15],
            questions[15:20]
        ]
        if self.next_page <= len(page_questions):
            modal = MulakatModal(self.next_page, page_questions[self.next_page], self.config)
            await interaction.response.send_modal(modal)
        else:
            await interaction.response.send_message("Mülakat tamamlandı!", ephemeral=True)

class MulakatStartView(discord.ui.View):
    def __init__(self, config):
        super().__init__(timeout=300)
        self.config = config
    @discord.ui.button(label="Sorulara Başla", style=discord.ButtonStyle.primary)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        questions = self.config['mulakat_questions']
        page_questions = [
            questions[0:5],
            questions[5:10],
            questions[10:15],
            questions[15:20]
        ]
        modal = MulakatModal(0, page_questions[0], self.config)
        await interaction.response.send_modal(modal)

class MulakatSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
    @app_commands.command(name="mülakat", description="Hard RP mülakat sorularını başlatır")
    async def mulakat(self, interaction: discord.Interaction):
        required_role_id = int(self.config.get('mulakat_required_role', '979515873675071488'))
        if not any(role.id == required_role_id for role in interaction.user.roles):
            await interaction.response.send_message(
                "❌ Bu komutu kullanmak için gerekli role sahip değilsiniz!",
                ephemeral=True
            )
            return
        view = MulakatStartView(self.config)
        await interaction.response.send_message(
            "Mülakat sorularına başlamak için aşağıdaki butona tıklayın.",
            view=view,
            ephemeral=True
        )

    @app_commands.command(name="mülakatonay", description="Kullanıcıya mülakat onay rolü verir ve bekleme rolünü alır")
    @app_commands.describe(user_id="Onay verilecek kullanıcının Discord ID'si")
    async def mulakatonay(self, interaction: discord.Interaction, user_id: str):
        admin_role_id = int(self.config.get('admin_role_id', '979515638542389278'))
        log_channel_id = 1391725335263051806
        log_channel = interaction.guild.get_channel(log_channel_id)
        try:
            if not any(role.id == admin_role_id for role in interaction.user.roles):
                msg = "❌ Bu komutu kullanmak için yetkiniz yok!"
                await interaction.response.send_message(msg, ephemeral=True)
                if log_channel:
                    await log_channel.send(f"[MülakatOnay] {interaction.user.mention} yetkisiz komut denemesi! Kullanıcı ID: {user_id}")
                print(f"[MülakatOnay] {interaction.user} yetkisiz komut denemesi! Kullanıcı ID: {user_id}")
                return
            try:
                member = await interaction.guild.fetch_member(int(user_id))
            except Exception:
                msg = "Kullanıcı bulunamadı!"
                await interaction.response.send_message(msg, ephemeral=True)
                if log_channel:
                    await log_channel.send(f"[MülakatOnay] Kullanıcı bulunamadı! ID: {user_id}")
                print(f"[MülakatOnay] Kullanıcı bulunamadı! ID: {user_id}")
                return
            bekleme_rol_id = int(self.config.get('mulakat_role_to_add', '1330382259395756094'))
            onay_rol_id = 1330578864396828682
            bekleme_rol = interaction.guild.get_role(bekleme_rol_id)
            onay_rol = interaction.guild.get_role(onay_rol_id)
            rol_mesaj = []
            if bekleme_rol and bekleme_rol in member.roles:
                await member.remove_roles(bekleme_rol, reason="Mülakat onaylandı")
                rol_mesaj.append(f"Bekleme rolü alındı.")
            if onay_rol and onay_rol not in member.roles:
                await member.add_roles(onay_rol, reason="Mülakat onaylandı")
                rol_mesaj.append(f"IC-ISIM rolü verildi.")
            msg = f"✅ <@{user_id}> kullanıcısına IC-ISIM rolü verildi ve bekleme rolü alındı!\n" + " ".join(rol_mesaj)
            await interaction.response.send_message(msg, ephemeral=True)
            log_text = f"[MülakatOnay] <@{user_id}> kullanıcısına IC-ISIM rolü verildi ve bekleme rolü alındı. Onaylayan: {interaction.user.mention}"
            if log_channel:
                await log_channel.send(log_text)
            print(log_text)
        except Exception as e:
            err_msg = f"Rol güncellenirken hata oluştu: {e}"
            try:
                await interaction.response.send_message(err_msg, ephemeral=True)
            except:
                pass
            if log_channel:
                await log_channel.send(f"[MülakatOnay] Hata: {e}")
            print(f"[MülakatOnay] Hata: {e}")

async def setup(bot):
    await bot.add_cog(MulakatSystem(bot)) 