import discord
import discord.errors
from discord import app_commands, ui
from discord.ext import commands
from discord.app_commands import Choice
from Utils.formatting import *
Nein = discord.AllowedMentions(everyone=False, roles=False, users=False)

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    role = app_commands.Group(name="role", description="Rollenverwaltung")

    @role.command(name="add", description="Vergebe einem Nutzer eine Rolle")
    @app_commands.describe(rolle="Welche Rolle willst du hinzufügen oder entfernen?",
                           nutzer="Welchen Nutzer soll es betreffen?")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True, send_messages=True)
    async def role(self, interaction: discord.Interaction, rolle: discord.Role, *, nutzer: discord.Member = None):
        nutzer = nutzer or interaction.user
        logreason = f"Vergeben von {interaction.user}"
        await interaction.response.defer(ephemeral=False)
        nachricht = f"{icon_accept} Die Rolle {rolle.mention} wurde dem Nutzer {nutzer.mention} vergeben!"
        await nutzer.add_roles(rolle, reason=logreason)
        await interaction.edit_original_response(content=nachricht, allowed_mentions=Nein)

    @role.command(name="role", description="Entferne einem Nutzer eine Rolle")
    @app_commands.describe(rolle="Welche Rolle willst du hinzufügen oder entfernen?",
                           nutzer="Welchen Nutzer soll es betreffen?")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True, send_messages=True)
    async def role(self, interaction: discord.Interaction, rolle: discord.Role, *, nutzer: discord.Member = None):
        nutzer = nutzer or interaction.user
        logreason = f"Entfernt von {interaction.user}"
        await interaction.response.defer(ephemeral=False)
        nachricht = f"{icon_accept} Die Rolle {rolle.mention} wurde dem Nutzer {nutzer.mention} entzogen!"
        await nutzer.remove_roles(rolle, reason=logreason)
        await interaction.edit_original_response(content=nachricht, allowed_mentions=Nein)

    @app_commands.command(name="say", description="Schreibe im Namen des Bots eine Nachricht")
    @app_commands.describe(format="Soll die Nachricht normal oder als Embed verschickt werden?",
                           kanal="In welchen Kanal soll die Nachricht kommen?")
    @app_commands.choices(format=[Choice(name="nachricht", value=1),
                                  Choice(name="embed", value=2)])
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(send_messages=True, embed_links=True, use_external_emojis=True)
    async def say(self, interaction: discord.Interaction, format: Choice[int], kanal: discord.TextChannel = None):
        if kanal is None:
            kanal = interaction.channel
        erfolgreich = f"{icon_accept} Die Nachricht wurde in den Kanal {kanal.mention} gesendet!"
        class Fragen(ui.Modal, title=f"{interaction.guild.name}"):
            answer = ui.TextInput(label="Nachricht", style=discord.TextStyle.paragraph, required=True,
                                  placeholder=f"Gebe deine Nachricht ein . . .")
            async def on_submit(self, interaction: discord.Interaction):
                if format.value == 1:
                    await kanal.send(content=self.answer.value)
                if format.value == 2:
                    embed = discord.Embed(description=self.answer.value, color=interaction.user.color)
                    embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url)
                    await kanal.send(embed=embed)
                await interaction.response.send_message(content=erfolgreich, ephemeral=True)
        await interaction.response.send_modal(Fragen())

async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))#, guilds=[discord.Object(id=756526359521656951)])