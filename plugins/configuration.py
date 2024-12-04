import aiohttp
import discord
import discord.errors
from discord.ext import commands
from discord import app_commands, ui
from discord.app_commands import Choice
import json
from Utils import welcome_variables
from Utils.formatting import *
from plugins.ticketing import Support, Report, SuR
from plugins.features import Suggester

def get_welcomemsg(client, ctx):
    with open('Legolas/datenbank/welcomemsg.json', 'r') as f:
        welcomemsg = json.load(f)
        return welcomemsg[str(ctx.guild.id)]

def get_pingrole(client, message):
    with open("Legolas/datenbank/suggestping.json", "r") as c:
        pingrole = json.load(c)
    return pingrole[str(message.guild.id)]

def get_suggest(client, ctx):
    with open('Legolas/datenbank/suggestlogging.json', 'r') as f:
        banmsg = json.load(f)
        return banmsg[str(ctx.guild.id)]

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    config = app_commands.Group(name="config", description="Konfiguration (hinzufügen)")
    reset = app_commands.Group(name="reset", description="Konfiguration (entfernen)")
    swelcome = app_commands.Group(name="welcome", description="Willkommensnachricht konfigurieren", parent=config)
    rwelcome = app_commands.Group(name="welcome", description=" Willkommensnachricht konfigurieren", parent=reset)
    sticket = app_commands.Group(name="ticket", description="Ticketsystem konfigurieren", parent=config)
    rticket = app_commands.Group(name="ticket", description="Ticketsystem konfigurieren", parent=reset)
    ssuggest = app_commands.Group(name="suggestions", description="Vorschlägesystem konfigurieren", parent=config)
    rsuggest = app_commands.Group(name="suggestions", description="Vorschlägesystem konfigurieren", parent=reset)

    @sticket.command(name="create", description="Ticketsystem erstellen")
    @app_commands.describe(kategorien="Welche Art Ticketsystem?",
                           kanal="In welchen Kanal?")
    @app_commands.choices(kategorien=[Choice(name="Support", value=1),
                                      Choice(name="Report", value=2),
                                      Choice(name="Support und Report", value=3)])
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.bot_has_permissions(create_private_threads=True, send_messages=True, manage_threads=True)
    async def ticketcreate(self, interaction: discord.Interaction, kategorien: Choice[int], kanal: discord.TextChannel = None):
        if kanal is None:
            kanal = interaction.channel
        class Text(ui.Modal, title=f"{interaction.guild.name} Tickets"):
            answer = ui.TextInput(label="Ticketnachricht", style=discord.TextStyle.paragraph, required=True,
                                  placeholder=f"Gebe die Ticketnachricht ein  . . .")
            async def on_submit(self, interaction: discord.Interaction):
                if kategorien.value == 1:
                    buttons = Support()
                if kategorien.value == 2:
                    buttons = Report()
                if kategorien.value == 3:
                    buttons = SuR()
                tEmbed = discord.Embed(description=self.answer.value, color=color_gray)
                tEmbed.set_author(name=f"{interaction.guild.name} Tickets", icon_url=interaction.guild.icon.url)
                await kanal.send(embed=tEmbed, view=buttons, allowed_mentions=False)
                await interaction.response.send_message(content=f"{icon_accept} Das Ticketsystem wurde erstellt!", ephemeral=True)
        await interaction.response.send_modal(Text())

    @sticket.command(name="ping", description="Teamrolle für Tickets festlegen")
    @app_commands.describe(rolle="Welche Rolle soll bei neuen Tickets markiert werden?")
    @app_commands.checks.has_permissions(administrator=True)
    async def setticketping(self, interaction: discord.Interaction, rolle: discord.Role):
        await interaction.response.defer(ephemeral=True)
        with open("Legolas/datenbank/ticketping.json", "r") as c:
            pingrole = json.load(c)
        pingrole[str(interaction.guild.id)] = rolle.id
        with open("Legolas/datenbank/ticketping.json", "w") as c:
            json.dump(pingrole, c, indent=4)
        await interaction.edit_original_response(content=f"{icon_accept} Die Ticketrolle wurde auf {rolle.mention} gesetzt!")

    @rticket.command(name="ping", description="Teamrolle für Tickets entfernen")
    @app_commands.checks.has_permissions(administrator=True)
    async def resetticketping(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            with open("Legolas/datenbank/ticketping.json", "r") as file:
                pingrole = json.load(file)
                del pingrole[str(interaction.guild_id)]
            with open("Legolas/datenbank/ticketping.json", "w") as c:
                json.dump(pingrole, c, indent=4)
        except KeyError:
            pass
        await interaction.edit_original_response(content=f"{icon_accept} Die Ticketrolle wurde zurückgesetzt!")

    @swelcome.command(name="variables", description="Verfügbare Variablen der Willkommensnachricht")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def variables(self, interaction: discord.Interaction):
        variablen = "Folgende Variablen stehen dir zur Anpassung der Willkommensnachricht frei:\r\n" \
                    "**{user}** -> Name + Tag des Nutzers " \
                    f"(z.B. {interaction.user})\r\n"\
                    "**{user.name}** -> Name des Nutzers " \
                    f"(z.B. {interaction.user.name})\r\n"\
                    "**{user.mention}** -> Erwähnung des Nutzers " \
                    f"(z.B. {interaction.user.mention})\r\n"\
                    "**{user.id}** -> ID des Nutzers " \
                    f"(z.B. {interaction.user.id})\r\n"\
                    "**{guild.name}** -> Name des Servers " \
                    f"(z.B. {interaction.guild.name})\r\n"\
                    "**{guild.member_counter}** -> Aktuelle Anzahl der Servermitglieder " \
                    f"(z.B. {interaction.guild.member_count})\r\n"\
                    "**{guild.id}** -> ID des Servers " \
                    f"(z.B. {interaction.guild.id})"
        await interaction.response.send_message(content=variablen, ephemeral=True)

    @swelcome.command(name="message", description="Welche Nachricht soll kommen, wenn ein Nutzer den Server betritt?")
    @app_commands.describe(nachricht="Welche Nachricht möchtest du setzen? Variablen: -> /config welcome variables")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setwelcomemsg(self, interaction: discord.Interaction, nachricht: str):
        await interaction.response.defer(ephemeral=True)
        try:
            with open("Legolas/datenbank/welcomemsg.json", "r") as f:
                welcomemsg = json.load(f)
                del welcomemsg[str(interaction.guild_id)]
            welcomemsg[int(interaction.guild_id)] = nachricht
            with open("Legolas/datenbank/welcomemsg.json", 'w') as f:
                json.dump(welcomemsg, f, indent=4)
        except KeyError:
            with open("Legolas/datenbank/welcomemsg.json", "r") as f:
                welcomemsg = json.load(f)
            welcomemsg[int(interaction.guild_id)] = nachricht
            with open("Legolas/datenbank/welcomemsg.json", "w") as f:
                json.dump(welcomemsg, f, indent=4)
        erfolgreich = f"{icon_accept} Die Willkommensnachricht wurde gesetzt auf```{nachricht}```\r\nVorschau: \r\n{welcome_variables.welcome_message(get_welcomemsg(self, interaction), interaction.user)}"
        await interaction.edit_original_response(content=erfolgreich)

    @rwelcome.command(name="message", description="Entferne die Nachricht die kommt, wenn ein User joined")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def resetwelcomemsg(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, allowed_mentions=False)
        erfolgreich = f"{icon_accept} Die Willkommensnachricht wurde zurückgesetzt!"
        try:
            with open("Legolas/datenbank/welcomemsg.json", "r") as file:
                suggestd = json.load(file)
                del suggestd[str(interaction.guild_id)]
            with open("Legolas/datenbank/welcomemsg.json", "w") as c:
                json.dump(suggestd, c, indent=4)
        except KeyError:
            pass
        await interaction.edit_original_response(content=erfolgreich)

    @swelcome.command(name="channel", description="Legt den Kanal für die Willkommensnachrichten fest")
    @app_commands.describe(kanal="In welchem Kanal sollen die neuen Nutzer begrüßt werden?")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.bot_has_permissions(manage_webhooks=True)
    async def setwelcomechannel(self, interaction: discord.Interaction, kanal: discord.TextChannel = None):
        if kanal is None:
            kanal = interaction.channel
        erfolgreich = f"{icon_accept} Der Kanal für die Willkommensnachrichten wurde auf {kanal.mention} gesetzt!"
        await interaction.response.defer(ephemeral=True)
        webhook = await kanal.create_webhook(name=self.bot.user.name, avatar=await self.bot.user.avatar.read(), reason=f"Willkommensnachrichten via Legolas")
        async with aiohttp.ClientSession() as session:
            try:
                with open("Legolas/datenbank/welcomemsgchannel.json", "r") as c:
                    webhook1 = json.load(c)
                    old_Webhook = discord.Webhook.from_url(webhook1[str(interaction.guild.id)], session=session)
                    await old_Webhook.delete(reason="Neuer Webhook wurde erstellt")
                    del webhook1[str(interaction.guild.id)]
                webhook1[str(interaction.guild.id)] = webhook.url
                with open("Legolas/datenbank/welcomemsgchannel.json", "w") as c:
                    json.dump(webhook1, c, indent=4)
            except KeyError:
                with open("Legolas/datenbank/welcomemsgchannel.json", "r") as c:
                    webhook1 = json.load(c)
                webhook1[str(interaction.guild.id)] = webhook.url
                with open("Legolas/datenbank/welcomemsgchannel.json", "w") as c:
                    json.dump(webhook1, c, indent=4)
        await interaction.edit_original_response(content=erfolgreich)

    @rwelcome.command(name="channel", description="Setze den Kanal für Willkommensnachrichten zurück")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.bot_has_permissions(manage_webhooks=True)
    async def resetwelcomechannel(self, interaction: discord.Interaction):
        erfolgreich = f"{icon_accept} Der Willkommenschannel wurde zurückgesetzt!"
        await interaction.response.defer(ephemeral=True)
        try:
            with open("Legolas/datenbank/welcomemsgchannel.json", "r") as file:
                welcomemsg = json.load(file)
                del welcomemsg[str(interaction.guild.id)]
            with open("Legolas/datenbank/welcomemsgchannel.json", "w") as c:
                json.dump(welcomemsg, c, indent=4)
        except KeyError:
            pass
        await interaction.edit_original_response(content=erfolgreich)

    @config.command(name="joinrole", description="Gebe neuen Nutzern auf dem Server eine Rolle (nur mit Membership Screening möglich)")
    @app_commands.describe(rolle="Welche Rolle soll vergeben werden?")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    async def setjoinrole(self, interaction: discord.Interaction, rolle: discord.Role):
        erfolgreich = f"{icon_accept} Die Beitrittsrolle wurde auf {rolle.mention} gesetzt!"
        await interaction.response.defer(ephemeral=True)
        with open("Legolas/datenbank/joinrole.json", "r") as c:
            joinrole = json.load(c)
        joinrole[str(interaction.guild.id)] = rolle.id
        with open("Legolas/datenbank/joinrole.json", "w") as c:
            json.dump(joinrole, c, indent=4)
        await interaction.edit_original_response(content=erfolgreich)

    @reset.command(name="joinrole", description="Setze die Beitrittsrolle für neue Neutzer zurück")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def resetjoinrole(self, interaction: discord.Interaction):
        erfolgreich = f"{icon_accept} Die Beitrittsrolle wurde zurückgesetzt!"
        await interaction.response.defer(ephemeral=True)
        try:
            with open("Legolas/datenbank/joinrole.json", "r") as file:
                joinrole = json.load(file)
                del joinrole[str(interaction.guild.id)]
            with open("Legolas/datenbank/joinrole.json", "w") as c:
                json.dump(joinrole, c, indent=4)
        except KeyError:
            pass
        await interaction.edit_original_response(content=erfolgreich)

    @config.command(name="banmsg", description="Schreibe eine zusätzliche Information zu Bannnachricht bei einem Bann")
    @app_commands.describe(nachricht="Welche Nachricht möchtest du setzen?")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setbanmsg(self, interaction: discord.Interaction, nachricht: str):
        erfolgreich = f"{icon_accept} Der Bannanhang wurde gesetzt auf```{nachricht}```"
        await interaction.response.defer(ephemeral=True)
        with open("Legolas/datenbank/bannotify.json", "r") as f:
            bannmsg = json.load(f)
        bannmsg[str(interaction.guild.id)] = nachricht
        with open("Legolas/datenbank/bannotify.json", "w") as f:
            json.dump(bannmsg, f, indent=4)
        await interaction.edit_original_response(content=erfolgreich)

    @reset.command(name="banmsg", description="Entferne die zusätzliche Information zur Bannnachricht bei einem Bann")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def resetbanmsg(self, interaction: discord.Interaction):
        erfolgreich = f"{icon_accept} Der Bannanhang wurde zurückgesetzt!"
        await interaction.response.defer(ephemeral=True)
        try:
            with open("Legolas/datenbank/bannotify.json", "r") as file:
                bannmsg = json.load(file)
                del bannmsg[str(interaction.guild.id)]
            with open("Legolas/datenbank/bannotify.json", "w") as c:
                json.dump(bannmsg, c, indent=4)
        except KeyError:
            pass
        await interaction.edit_original_response(content=erfolgreich)


    @ssuggest.command(name="create", description="Erstelle ein Vorschlägesystem")
    @app_commands.describe(kanal="In welchen Kanal soll die Nachricht gesendet werden?")
    @app_commands.checks.has_permissions(administrator=True)
    async def suggestcreate(self, interaction: discord.Interaction, kanal: discord.TextChannel = None):
        if kanal is None:
            kanal = interaction.channel
        class Text(ui.Modal, title=f"{interaction.guild.name} Vorschläge"):
            answer = ui.TextInput(label="Vorschlagnachricht", style=discord.TextStyle.paragraph, required=True,
                                  placeholder=f"Bitte gebe die Vorschlagnachricht ein  . . .")
            async def on_submit(self, interaction: discord.Interaction):
                tEmbed = discord.Embed(description=self.answer.value, color=color_gray)
                tEmbed.set_author(name=f"{interaction.guild.name} Vorschlägesystem", icon_url=interaction.guild.icon.url)
                await kanal.send(embed=tEmbed, view=Suggester(), allowed_mentions=False)
                await interaction.response.send_message(content=f"{icon_accept} Das Vorschlägesystem wurde erstellt!", ephemeral=True)
        await interaction.response.send_modal(Text())

    @ssuggest.command(name="channel", description="Setze den Vorschlägekanal für die Vorschläge")
    @app_commands.describe(kanal="In welchen Kanal sollen die Vorschläge kommen?")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setsuggestions(self, interaction: discord.Interaction, kanal: discord.TextChannel = None):
        if kanal is None:
            kanal = interaction.channel
        erfolgreich = f"{icon_accept} Der Vorschlägekanal wurde auf {kanal.mention} gesetzt!"
        await interaction.response.defer(ephemeral=True)
        with open("Legolas/datenbank/suggestlogging.json", "r") as c:
            suggestc = json.load(c)
        suggestc[str(interaction.guild.id)] = kanal.id
        with open("Legolas/datenbank/suggestlogging.json", "w") as c:
            json.dump(suggestc, c, indent=4)
        await interaction.edit_original_response(content=erfolgreich)

    @rsuggest.command(name="channel", description="Setze den Vorschlägekanal zurück")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def resetsuggestions(self, interaction: discord.Interaction):
        erfolgreich = f"{icon_accept} Der Vorschlägekanal wurde zurückgesetzt!"
        await interaction.response.defer(ephemeral=True)
        try:
            with open("Legolas/datenbank/suggestlogging.json", "r") as file:
                logd = json.load(file)
                del logd[str(interaction.guild.id)]
            with open("Legolas/datenbank/suggestlogging.json", "w") as c:
                json.dump(logd, c, indent=4)
        except KeyError:
            pass
        await interaction.edit_original_response(content=erfolgreich)

    @ssuggest.command(name="ping", description="Lege die Rolle für Vorschläge fest")
    @app_commands.describe(rolle="Welche Rolle soll markiert werden bei neuen Vorschlägen?")
    @app_commands.checks.has_permissions(administrator=True)
    async def setticketping(self, interaction: discord.Interaction, rolle: discord.Role):
        await interaction.response.defer(ephemeral=True)
        with open("Legolas/datenbank/suggestping.json", "r") as c:
            pingrole = json.load(c)
        pingrole[str(interaction.guild.id)] = rolle.id
        with open("Legolas/datenbank/suggestping.json", "w") as c:
            json.dump(pingrole, c, indent=4)
        await interaction.edit_original_response(content=f"{icon_accept} Die Vorschlägerolle wurde auf {rolle.mention} gesetzt!")

    @rsuggest.command(name="ping", description="Entferne die Rolle für Vorschläge")
    @app_commands.checks.has_permissions(administrator=True)
    async def resetticketping(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            with open("Legolas/datenbank/suggestping.json", "r") as file:
                pingrole = json.load(file)
                del pingrole[str(interaction.guild_id)]
            with open("Legolas/datenbank/suggestping.json", "w") as c:
                json.dump(pingrole, c, indent=4)
        except KeyError:
            pass
        await interaction.edit_original_response(content=f"{icon_accept} Die Vorschlägerolle wurde zurückgesetzt!")

    @config.command(name="logchannel", description="Setze den einen Logkanal für den Server")
    @app_commands.describe(modul="Welches Logmodul möchtest du festlegen", kanal="In welchem Kanal soll geloggt werden?")
    @app_commands.choices(modul=[Choice(name="nachrichten", value=1),
                                 Choice(name="moderation", value=2),
                                 Choice(name="sprachkanäle", value=3),
                                 Choice(name="nutzer", value=4),
                                 Choice(name="server", value=5)])
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.bot_has_permissions(manage_webhooks=True)
    async def setlogchannel(self, interaction: discord.Interaction, modul: Choice[int], kanal: discord.TextChannel = None):
        if kanal is None:
            kanal = interaction.channel
        erfolgreich = f"{icon_accept} Das Logging Modul **{modul.name}** wurde auf den Kanal {kanal.mention} gesetzt!"
        await interaction.response.defer(ephemeral=True)
        webhook = await kanal.create_webhook(name=self.bot.user.name, avatar=await self.bot.user.avatar.read(), reason=f"{modul.name}-log gesetzt")

        if modul.value == 1: # Nachrichten
            with open("Legolas/datenbank/messagelogging.json", "r") as c:
                webhook1 = json.load(c)
            webhook1[str(interaction.guild.id)] = webhook.url
            with open("Legolas/datenbank/messagelogging.json", "w") as c:
                json.dump(webhook1, c, indent=4)

        if modul.value == 2: # Moderation
            with open("Legolas/datenbank/modlogging.json", "r") as c:
                webhook1 = json.load(c)
            webhook1[str(interaction.guild.id)] = webhook.url
            with open("Legolas/datenbank/modlogging.json", "w") as c:
                json.dump(webhook1, c, indent=4)

        if modul.value == 3: # Sprachkanäle
            with open("Legolas/datenbank/voicelogging.json", "r") as c:
                webhook1 = json.load(c)
            webhook1[str(interaction.guild.id)] = webhook.url
            with open("Legolas/datenbank/voicelogging.json", "w") as c:
                json.dump(webhook1, c, indent=4)

        if modul.value == 4: # Nutzer
            with open("Legolas/datenbank/memberlogging.json", "r") as c:
                webhook1 = json.load(c)
            webhook1[str(interaction.guild.id)] = webhook.url
            with open("Legolas/datenbank/memberlogging.json", "w") as c:
                json.dump(webhook1, c, indent=4)

        if modul.value == 5: # Server
            with open("Legolas/datenbank/serverlogging.json", "r") as c:
                webhook1 = json.load(c)
            webhook1[str(interaction.guild.id)] = webhook.url
            with open("Legolas/datenbank/serverlogging.json", "w") as c:
                json.dump(webhook1, c, indent=4)

        await interaction.edit_original_response(content=erfolgreich)
        #await logKanal.send(embed=log)

    @reset.command(name="logchannel", description="Setze einen Logkanal zurück")
    @app_commands.describe(modul="Welches Logmodul möchtest du zurücksetzen")
    @app_commands.choices(modul=[Choice(name="nachrichten", value=1),
                                 Choice(name="moderation", value=2),
                                 Choice(name="sprachkanäle", value=3),
                                 Choice(name="nutzer", value=4),
                                 Choice(name="server", value=5)])
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.bot_has_permissions(manage_webhooks=True)
    async def resetlogchannel(self, interaction: discord.Interaction, modul: Choice[int]):
        erfolgreich = f"{icon_accept} Das Logmodul **{modul.name}** wurde zurückgesetzt!"
        await interaction.response.defer(ephemeral=True)
        if modul.value == 1:  # Nachrichten
            try:
                with open("Legolas/datenbank/messagelogging.json", "r") as file:
                    mlogd = json.load(file)
                    del mlogd[str(interaction.guild.id)]
                with open("Legolas/datenbank/messagelogging.json", "w") as c:
                    json.dump(mlogd, c, indent=4)
            except KeyError:
                pass

        if modul.value == 2: # Moderation
            try:
                with open("Legolas/datenbank/modlogging.json", "r") as file:
                    mlogd = json.load(file)
                    del mlogd[str(interaction.guild.id)]
                with open("Legolas/datenbank/modlogging.json", "w") as c:
                    json.dump(mlogd, c, indent=4)
            except KeyError:
                pass

        if modul.value == 3: # Sprachkanäle
            try:
                with open("Legolas/datenbank/voicelogging.json", "r") as file:
                    logd = json.load(file)
                    del logd[str(interaction.guild.id)]
                with open("Legolas/datenbank/voicelogging.json", "w") as c:
                    json.dump(logd, c, indent=4)
            except KeyError:
                pass

        if modul.value == 4: # Nutzer
            try:
                with open("Legolas/datenbank/memberlogging.json", "r") as file:
                    logd = json.load(file)
                    del logd[str(interaction.guild.id)]
                with open("Legolas/datenbank/memberlogging.json", "w") as c:
                    json.dump(logd, c, indent=4)
            except KeyError:
                pass

        if modul.value == 5: # Server
            try:
                with open("Legolas/datenbank/serverlogging.json", "r") as file:
                    logd = json.load(file)
                    del logd[str(interaction.guild.id)]
                with open("Legolas/datenbank/serverlogging.json", "w") as c:
                    json.dump(logd, c, indent=4)
            except KeyError:
                pass
        await interaction.edit_original_response(content=erfolgreich)

async def setup(bot: commands.Bot):
    await bot.add_cog(Config(bot))#, guilds=[discord.Object(id=756526359521656951)])