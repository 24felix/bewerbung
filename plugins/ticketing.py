import json
import discord
import discord.errors
from discord import ui
from Utils.formatting import *
from discord.ext import commands

def get_pingrole(client, message):
    with open("Legolas/datenbank/ticketping.json", "r") as c:
        pingrole = json.load(c)
    return pingrole[str(message.guild.id)]
mFehler = f"{icon_denied} Bitte lege mit </config team:1029785742207090758> eine Pingrolle fest!"

class Close(discord.ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Schließen", style=discord.ButtonStyle.success, emoji=icon_accept, custom_id="persistent_view:confirm")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        tEmbed = discord.Embed(description=f"{icon_accept} Ticket von {interaction.user.mention} geschlossen",
                               color=color_red)
        tEmbed.set_author(name=f"{interaction.guild.name} Tickets", icon_url=interaction.guild.icon.url)
        await interaction.message.edit(content=None, embed=tEmbed, view=None)
        await interaction.channel.edit(archived=True, locked=True)

    @discord.ui.button(label="Abbrechen", style=discord.ButtonStyle.danger, emoji=icon_denied, custom_id="persistent_view:cancel")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()

class Message(discord.ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Schließen", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="persistent_view:schließen")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        tEmbed = discord.Embed(description=f"Sollte dein Anliegen hiermit geklärt sein, klicke auf den \"`Schließen`\" Button!",
                               color=color_orange)
        tEmbed.set_author(name=f"{interaction.guild.name} Tickets", icon_url=interaction.guild.icon.url)
        await interaction.response.send_message(content=interaction.message.mentions[0].mention, embed=tEmbed, view=Close())

class Support(discord.ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Support anfordern", style=discord.ButtonStyle.success, emoji="🎫", custom_id="persistent_view:support")
    async def support(self, interaction: discord.Interaction, button: discord.ui.Button):
        tEmbed = discord.Embed(description=f"Bitte habe etwas Geduld, es wird sich gleich jemand um dich kümmern!",
                               color=color_green)
        tEmbed.set_author(name=f"{interaction.guild.name} Tickets", icon_url=interaction.guild.icon.url)
        try:
            mod = discord.utils.get(interaction.guild.roles, id=get_pingrole(self, interaction))
        except KeyError:
            return await interaction.response.send_message(content=mFehler, ephemeral=True)
        if mod in interaction.user.roles:
            class Nutzer(ui.Modal, title=f"{interaction.guild.name} Tickets"):
                answer = ui.TextInput(label="Ticket für Nutzer", style=discord.TextStyle.short, required=True, min_length=18, max_length=19,
                                      placeholder=f"Gebe die ID vom Nutzer ein . . .")
                async def on_submit(self, interaction: discord.Interaction):
                    try:
                        user = await interaction.guild.fetch_member(int(self.answer.value))
                        ticket = await interaction.channel.create_thread(name=f"Support - {user.name}", type=discord.ChannelType.private_thread, reason="Ticket erstellt", auto_archive_duration=1440, invitable=False)
                        await ticket.send(content=f"Willkommen {user.mention} — {mod.mention}", embed=tEmbed, view=Message())
                        await interaction.response.send_message(content=f"{icon_accept} Das Ticket wurde erstellt: {ticket.mention}", ephemeral=True)
                    except KeyError:
                        await interaction.response.send_message(content=f"{icon_denied} Der Nutzer konnte nicht gefunden werden!", ephemeral=True)
            await interaction.response.send_modal(Nutzer())
        else:
            class Fragen(ui.Modal, title=f"{interaction.guild.name} Tickets"):
                answer = ui.TextInput(label="Dein Anliegen", style=discord.TextStyle.paragraph, min_length=10, required=True,
                                      placeholder=f"Bitte teile uns dein Anliegen mit . . .")
                async def on_submit(self, interaction: discord.Interaction):
                    tEmbed.add_field(name="Anliegen", value=f"```{self.answer.value}```")
                    ticket = await interaction.channel.create_thread(name=f"Support - {interaction.user.name}", type=discord.ChannelType.private_thread, reason="Ticket erstellt", auto_archive_duration=1440, invitable=False)
                    await ticket.send(content=f"Willkommen {interaction.user.mention} — {mod.mention}", embed=tEmbed, view=Message())
                    await interaction.response.send_message(content=f"{icon_accept} Dein Ticket wurde erstellt: {ticket.mention}", ephemeral=True)
            await interaction.response.send_modal(Fragen())

class Report(discord.ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Mitglied melden", style=discord.ButtonStyle.danger, emoji="🛡️", custom_id="persistent_view:report")
    async def report(self, interaction: discord.Interaction, button: discord.ui.Button):
        tEmbed = discord.Embed(description=f"Bitte habe etwas Geduld, es wird sich gleich jemand um dich kümmern!",
                               color=color_green)
        tEmbed.set_author(name=f"{interaction.guild.name} Tickets", icon_url=interaction.guild.icon.url)

        try:
            mod = discord.utils.get(interaction.guild.roles, id=get_pingrole(self, interaction))
        except KeyError:
            return await interaction.response.send_message(content=mFehler, ephemeral=True)
        if mod in interaction.user.roles:
            class Nutzer(ui.Modal, title=f"{interaction.guild.name} Tickets"):
                answer = ui.TextInput(label="Ticket für Nutzer", style=discord.TextStyle.short, required=True, min_length=18, max_length=19,
                                      placeholder=f"Gebe die ID vom Nutzer ein . . .")
                async def on_submit(self, interaction: discord.Interaction):
                    try:
                        user = await interaction.guild.fetch_member(int(self.answer.value))
                        ticket = await interaction.channel.create_thread(name=f"Report - {user.mention}", type=discord.ChannelType.private_thread, reason="Meldung erstellt", auto_archive_duration=1440, invitable=False)
                        await ticket.send(content=f"Willkommen {interaction.user.mention} — {mod.mention}", embed=tEmbed, view=Message())
                        await interaction.response.send_message(content=f"{icon_accept} Das Ticket wurde erstellt: {ticket.mention}", ephemeral=True)
                    except KeyError:
                        await interaction.response.send_message(content=f"{icon_denied} Der Nutzer konnte nicht gefunden werden!", ephemeral=True)
            await interaction.response.send_modal(Nutzer())
        else:
            try:
                ticket = await interaction.channel.create_thread(name=f"Report - {interaction.user.name}",  type=discord.ChannelType.private_thread, reason="Meldung erstellt", auto_archive_duration=1440, invitable=False)
                await ticket.send(content=f"Willkommen {interaction.user.mention} — {mod.mention}", embed=tEmbed, view=Message())
                await interaction.response.send_message(content=f"{icon_accept} Dein Ticket wurde erstellt: {ticket.mention}", ephemeral=True)
            except KeyError:
                await interaction.response.send_message(content=mFehler, ephemeral=True)

class SuR(discord.ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Support anfordern", style=discord.ButtonStyle.success, emoji="🎫", custom_id="persistent_view:support")
    async def support(self, interaction: discord.Interaction, button: discord.ui.Button):
        tEmbed = discord.Embed(description=f"Bitte habe etwas Geduld, es wird sich gleich jemand um dich kümmern!",
                               color=color_green)
        tEmbed.set_author(name=f"{interaction.guild.name} Tickets", icon_url=interaction.guild.icon.url)
        try:
            mod = discord.utils.get(interaction.guild.roles, id=get_pingrole(self, interaction))
        except KeyError:
            return await interaction.response.send_message(content=mFehler, ephemeral=True)
        if mod in interaction.user.roles:
            class Nutzer(ui.Modal, title=f"{interaction.guild.name} Tickets"):
                answer = ui.TextInput(label="Ticket für Nutzer", style=discord.TextStyle.short, required=True, min_length=18, max_length=19,
                                      placeholder=f"Gebe die ID vom Nutzer ein . . .")
                async def on_submit(self, interaction: discord.Interaction):
                    try:
                        user = await interaction.guild.fetch_member(int(self.answer.value))
                        ticket = await interaction.channel.create_thread(name=f"Support - {user.name}", type=discord.ChannelType.private_thread, reason="Ticket erstellt", auto_archive_duration=1440, invitable=False)
                        await ticket.send(content=f"Willkommen {user.mention} — {mod.mention}", embed=tEmbed, view=Message())
                        await interaction.response.send_message(content=f"{icon_accept} Das Ticket wurde erstellt: {ticket.mention}", ephemeral=True)
                    except KeyError:
                        await interaction.response.send_message(content=f"{icon_denied} Der Nutzer konnte nicht gefunden werden!", ephemeral=True)
            await interaction.response.send_modal(Nutzer())
        else:
            class Fragen(ui.Modal, title=f"{interaction.guild.name} Tickets"):
                answer = ui.TextInput(label="Dein Anliegen", style=discord.TextStyle.paragraph, min_length=10, required=True,
                                      placeholder=f"Bitte teile uns dein Anliegen mit . . .")
                async def on_submit(self, interaction: discord.Interaction):
                    tEmbed.add_field(name="Anliegen", value=f"```{self.answer.value}```")
                    ticket = await interaction.channel.create_thread(name=f"Support - {interaction.user.name}", type=discord.ChannelType.private_thread, reason="Ticket erstellt", auto_archive_duration=1440, invitable=False)
                    await ticket.send(content=f"Willkommen {interaction.user.mention} — {mod.mention}", embed=tEmbed, view=Message())
                    await interaction.response.send_message(content=f"{icon_accept} Dein Ticket wurde erstellt: {ticket.mention}", ephemeral=True)
            await interaction.response.send_modal(Fragen())

    @discord.ui.button(label="Mitglied melden", style=discord.ButtonStyle.danger, emoji="🛡️", custom_id="persistent_view:report")
    async def report(self, interaction: discord.Interaction, button: discord.ui.Button):
        tEmbed = discord.Embed(description=f"Bitte habe etwas Geduld, es wird sich gleich jemand um dich kümmern!",
                               color=color_green)
        tEmbed.set_author(name=f"{interaction.guild.name} Tickets", icon_url=interaction.guild.icon.url)

        try:
            mod = discord.utils.get(interaction.guild.roles, id=get_pingrole(self, interaction))
        except KeyError:
            return await interaction.response.send_message(content=mFehler, ephemeral=True)
        if mod in interaction.user.roles:
            class Nutzer(ui.Modal, title=f"{interaction.guild.name} Tickets"):
                answer = ui.TextInput(label="Ticket für Nutzer", style=discord.TextStyle.short, required=True, min_length=18, max_length=19,
                                      placeholder=f"Gebe die ID vom Nutzer ein . . .")
                async def on_submit(self, interaction: discord.Interaction):
                    try:
                        user = await interaction.guild.fetch_member(int(self.answer.value))
                        ticket = await interaction.channel.create_thread(name=f"Report - {user.mention}", type=discord.ChannelType.private_thread, reason="Meldung erstellt", auto_archive_duration=1440, invitable=False)
                        await ticket.send(content=f"Willkommen {interaction.user.mention} — {mod.mention}", embed=tEmbed, view=Message())
                        await interaction.response.send_message(content=f"{icon_accept} Das Ticket wurde erstellt: {ticket.mention}", ephemeral=True)
                    except:
                        await interaction.response.send_message(content=f"{icon_denied} Der Nutzer konnte nicht gefunden werden!", ephemeral=True)
            await interaction.response.send_modal(Nutzer())
        else:
            try:
                ticket = await interaction.channel.create_thread(name=f"Report - {interaction.user.name}",  type=discord.ChannelType.private_thread, reason="Meldung erstellt", auto_archive_duration=1440, invitable=False)
                await ticket.send(content=f"Willkommen {interaction.user.mention} — {mod.mention}", embed=tEmbed, view=Message())
                await interaction.response.send_message(content=f"{icon_accept} Dein Ticket wurde erstellt: {ticket.mention}", ephemeral=True)
            except KeyError:
                await interaction.response.send_message(content=mFehler, ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))#, guilds=[discord.Object(id=756526359521656951)])