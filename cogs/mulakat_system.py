import discord
from discord.ext import commands
from discord import app_commands
from discord import ui
import json
import os
from typing import Optional

class InterviewModal(discord.ui.Modal):
    def __init__(self, page_index, questions, config):
        super().__init__(title=f"Hard RP Questions - Page {page_index + 1}", timeout=600)
        self.page_index = page_index
        self.questions = questions
        self.config = config
        for i, question in enumerate(questions):
            label = (question[:42] + "...") if len(question) > 45 else question
            text_input = discord.ui.TextInput(
                label=label,
                placeholder="Write your answer here...",
                required=True,
                style=discord.TextStyle.paragraph,
                max_length=1000
            )
            self.add_item(text_input)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        if not hasattr(interaction.client, 'interview_responses'):
            interaction.client.interview_responses = {}
        if user_id not in interaction.client.interview_responses or self.page_index == 0:
            interaction.client.interview_responses[user_id] = []
        responses = {}
        for i, question in enumerate(self.questions):
            responses[question] = self.children[i].value
        page_data = {
            "page": self.page_index + 1,
            "responses": responses
        }
        if len(interaction.client.interview_responses[user_id]) == self.page_index:
            interaction.client.interview_responses[user_id].append(page_data)
        else:
            interaction.client.interview_responses[user_id][self.page_index] = page_data
        total_pages = 4
        if self.page_index < total_pages - 1:
            view = InterviewContinueView(self.page_index + 1, self.config)
            await interaction.response.send_message(
                f"Your answers for page {self.page_index + 1} have been saved. Click the button below for the next page.",
                view=view,
                ephemeral=True
            )
        else:
            await self.complete_interview(interaction, user_id)

    async def complete_interview(self, interaction: discord.Interaction, user_id: str):
        final_data = {
            "discord_id": interaction.user.id,
            "discord_name": str(interaction.user),
            "responses": interaction.client.interview_responses[user_id]
        }
        os.makedirs('./responses', exist_ok=True)
        final_json_path = f'./responses/{user_id}_interview_final.json'
        with open(final_json_path, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        interview_channel_id = int(self.config.get('interview_channel_id', '1388307897099878410'))
        channel = interaction.guild.get_channel(interview_channel_id)
        if channel:
            try:
                embed = discord.Embed(
                    title=f"Interview Answers - {interaction.user}",
                    description=f"User: <@{interaction.user.id}>\nDiscord ID: {interaction.user.id}",
                    color=0x3498db
                )
                for page in final_data["responses"]:
                    page_num = page["page"]
                    answers = page["responses"]
                    value = ""
                    for question, answer in answers.items():
                        value += f"**{question}**\n{answer}\n\n"
                    embed.add_field(name=f"Page {page_num}", value=value[:1024], inline=False)
                await channel.send(embed=embed)
            except Exception as e:
                print(f"Error sending to interview channel: {e}")
        try:
            role_to_add_id = int(self.config.get('interview_role_to_add', '1330382259395756094'))
            role_to_remove_id = int(self.config.get('interview_role_to_remove', '979515873675071488'))
            role_to_add = interaction.guild.get_role(role_to_add_id)
            role_to_remove = interaction.guild.get_role(role_to_remove_id)
            if role_to_add:
                await interaction.user.add_roles(role_to_add, reason="Interview completed")
            if role_to_remove:
                await interaction.user.remove_roles(role_to_remove, reason="Interview completed")
        except Exception as e:
            print(f"Role update error: {e}")
        await interaction.response.send_message(
            "✅ All your answers have been saved and your new role has been assigned. Your interview is complete!",
            ephemeral=True
        )
        if user_id in interaction.client.interview_responses:
            del interaction.client.interview_responses[user_id]

class InterviewContinueView(discord.ui.View):
    def __init__(self, next_page, config):
        super().__init__(timeout=300)
        self.next_page = next_page
        self.config = config
    @discord.ui.button(label="Next Page", style=discord.ButtonStyle.primary)
    async def continue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        questions = self.config['interview_questions']
        page_questions = [
            questions[0:5],
            questions[5:10],
            questions[10:15],
            questions[15:20]
        ]
        if self.next_page <= len(page_questions):
            modal = InterviewModal(self.next_page, page_questions[self.next_page], self.config)
            await interaction.response.send_modal(modal)
        else:
            await interaction.response.send_message("Interview completed!", ephemeral=True)

class InterviewStartView(discord.ui.View):
    def __init__(self, config):
        super().__init__(timeout=300)
        self.config = config
    @discord.ui.button(label="Start Questions", style=discord.ButtonStyle.primary)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        questions = self.config['interview_questions']
        page_questions = [
            questions[0:5],
            questions[5:10],
            questions[10:15],
            questions[15:20]
        ]
        modal = InterviewModal(0, page_questions[0], self.config)
        await interaction.response.send_modal(modal)

class InterviewSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
    @app_commands.command(name="interview", description="Starts the Hard RP interview questions")
    async def interview(self, interaction: discord.Interaction):
        required_role_id = int(self.config.get('interview_required_role', '979515873675071488'))
        if not any(role.id == required_role_id for role in interaction.user.roles):
            await interaction.response.send_message(
                "❌ You do not have the required role to use this command!",
                ephemeral=True
            )
            return
        view = InterviewStartView(self.config)
        await interaction.response.send_message(
            "Click the button below to start the interview questions.",
            view=view,
            ephemeral=True
        )

    @app_commands.command(name="interviewapprove", description="Gives the interview approval role to the user and removes the waiting role")
    @app_commands.describe(user_id="Discord ID of the user to approve")
    async def interviewapprove(self, interaction: discord.Interaction, user_id: str):
        admin_role_id = int(self.config.get('admin_role_id', '979515638542389278'))
        log_channel_id = 1391725335263051806
        log_channel = interaction.guild.get_channel(log_channel_id)
        try:
            if not any(role.id == admin_role_id for role in interaction.user.roles):
                msg = "❌ You do not have permission to use this command!"
                await interaction.response.send_message(msg, ephemeral=True)
                if log_channel:
                    await log_channel.send(f"[InterviewApprove] {interaction.user.mention} tried to use the command without permission! User ID: {user_id}")
                print(f"[InterviewApprove] {interaction.user} tried to use the command without permission! User ID: {user_id}")
                return
            try:
                member = await interaction.guild.fetch_member(int(user_id))
            except Exception:
                msg = "User not found!"
                await interaction.response.send_message(msg, ephemeral=True)
                if log_channel:
                    await log_channel.send(f"[InterviewApprove] User not found! ID: {user_id}")
                print(f"[InterviewApprove] User not found! ID: {user_id}")
                return
            waiting_role_id = int(self.config.get('interview_role_to_add', '1330382259395756094'))
            approval_role_id = 1330578864396828682
            waiting_role = interaction.guild.get_role(waiting_role_id)
            approval_role = interaction.guild.get_role(approval_role_id)
            role_message = []
            if waiting_role and waiting_role in member.roles:
                await member.remove_roles(waiting_role, reason="Interview approved")
                role_message.append("Waiting role removed.")
            if approval_role and approval_role not in member.roles:
                await member.add_roles(approval_role, reason="Interview approved")
                role_message.append("IC-NAME role assigned.")
            msg = f"✅ <@{user_id}> has been given the IC-NAME role and the waiting role has been removed!\n" + " ".join(role_message)
            await interaction.response.send_message(msg, ephemeral=True)
            log_text = f"[InterviewApprove] <@{user_id}> has been given the IC-NAME role and the waiting role has been removed. Approved by: {interaction.user.mention}"
            if log_channel:
                await log_channel.send(log_text)
            print(log_text)
        except Exception as e:
            err_msg = f"Error updating roles: {e}"
            try:
                await interaction.response.send_message(err_msg, ephemeral=True)
                if log_channel:
                    await log_channel.send(f"[InterviewApprove] {err_msg}")
                print(f"[InterviewApprove] {err_msg}")
            except Exception:
                pass

async def setup(bot):
    await bot.add_cog(InterviewSystem(bot)) 