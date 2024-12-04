import io
import discord
import datetime
import discord.errors
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
from Utils.formatting import *
class Mass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    mass = app_commands.Group(name="mass", description="Befehle für Massenverfahren")

    @mass.command(name="addrole", description="Vergebe eine Rolle an mehrere Nutzer gleichzeitig")
    @app_commands.describe(hauptrolle="Welche Leute sollen die Rolle bekommen?", neuerolle="Welche Rolle sollen die bekommen?")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    async def addrole(self, interaction: discord.Interaction, hauptrolle: discord.Role, neuerolle: discord.Role):
        erfolgreich = f"{icon_accept} Die {neuerolle.mention} Rolle wurde an **{len(hauptrolle.members)} Nutzer** vergeben!"
        await interaction.response.defer(ephemeral=False)
        if not interaction.guild.chunked:
            await interaction.guild.chunk(cache=True)
        for member in hauptrolle.members:
            await member.add_roles(neuerolle)
        await interaction.edit_original_response(content=erfolgreich)

    @mass.command(name="removerole", description="Entziehe eine Rolle von mehreren Nutzer gleichzeitig")
    @app_commands.describe(rolle="Welche Rolle soll entzogen werden?")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    async def removerole(self, interaction: discord.Interaction, rolle: discord.Role,):
        erfolgreich = f"{icon_accept} Die {rolle.mention} Rolle wurde von **{len(rolle.members)} Nutzern** entzogen!"
        await interaction.response.defer(ephemeral=False)
        if not interaction.guild.chunked:
            await interaction.guild.chunk(cache=True)
        for member in rolle.members:
            await member.remove_roles(rolle)
        await interaction.edit_original_response(content=erfolgreich)

    @mass.command(name="mute", description="Schalte mehrere Nutzer Stumm")
    @app_commands.describe(nutzer="Wer soll stummgeschalten werden?",
                           stunden="Wie viele Stunden sollen die Nutzer stummgeschalten werden?",
                           minuten="Wie viele Minuten sollen die Nutzer stummgeschalten werden?",
                           grund="Für welchen Grund möchtest du die Nutzer stummschalten?")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.checks.bot_has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, nutzer: str, stunden: int = None, minuten: int = None, grund: str = None):
        if minuten is None and stunden is None:
            stunden = 2
            minuten = 0
        if stunden is None:
            stunden = 0
        if minuten is None:
            minuten = 0
        if grund is None:
            grund = "Kein Grund angegeben"
        bannutzer = f"{icon_loading} Die IDs werden gesucht . . ."
        ids = nutzer.split(" ")
        logreason = f"{interaction.user} - {datetime.date.today().strftime(f'%d.%m.%Y')}: {grund}"
        erfolgreich = f"{icon_accept} Es wurden **{len(ids)} Nutzer** **{stunden} Stunden und {minuten} Minuten** stummgeschalten!"
        abbruch = f"{icon_denied} Das Stummschaltungsverfahren wurde abgebrochen!"
        frage = f"Das massen Stummschalten beinhaltet **{len(ids)} Nutzer**, möchtest du fortfahren?"
        laden = f"{icon_loading} **{len(ids)} Nutzer** werden stummgeschalten . . ."
        fehler = f"{icon_denied} Die Zeit darf maximal 28 Tage sein!"
        delta = datetime.timedelta(hours=stunden, minutes=minuten)
        max = datetime.timedelta(days=27, hours=23, minutes=59, seconds=59)
        time = (datetime.datetime.now().astimezone() + delta)

        if delta < max:
            await interaction.response.send_message(content=bannutzer)
            class Mehr(discord.ui.View):
                bot = self.bot
                async def on_timeout(self):
                    pass
                @discord.ui.button(label="Stummschalten", style=discord.ButtonStyle.green, emoji=icon_accept)
                async def stumm(self, interaction: discord.Interaction, button: discord.ui.Button):
                    global user
                    #for button in self.children:
                    #    button.disabled = True
                    await interaction.response.edit_message(content=laden, view=None)
                    for id in ids:
                        try:
                            user = await self.bot.fetch_user(id)
                            await user.timeout(time, reason=logreason, delete_message_days=0)
                        except discord.HTTPException:
                            pass
                    #fmt = "\n".join(
                          #"{id}\tErstellt: {c}\t{m}".format(id=m.id, c=m.created_at.strftime(f'%d.%m.%Y %H:%M:%S'),
                                                            #m=str(m)) for m in user)
                    content = f"Anzahl der gebannten Nutzer: {len(ids)}"
                    #file = discord.File(io.BytesIO(content.encode('utf-8')), filename='multiban.txt')
                    await interaction.response.edit_message(content=erfolgreich, view=None)
                @discord.ui.button(label="Abbrechen", style=discord.ButtonStyle.red, emoji=icon_denied)
                async def abbrechen(self, interaction: discord.Interaction, button: discord.ui.Button):
                    for button in self.children:
                        button.disabled = True
                    await interaction.response.edit_message(content=abbruch, view=None)
            await interaction.response.edit_message(content=frage, view=Mehr())
        else:
            await interaction.response.send_message(content=fehler, ephemeral=True)

    @mass.command(name="unmute", description="Entferne die Stummschaltung von mehreren Nutzern")
    @app_commands.describe(nutzer="Von wem soll die Stummschaltung entfernt werden?",
                           grund="Für welchen Grund möchtest du die Stummschaltung der Nutzer entfernen?")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.checks.bot_has_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, nutzer: str, grund: str = None):
        if grund is None:
            grund = "Kein Grund angegeben"
        bannutzer = f"{icon_loading} Die IDs werden gesucht . . ."
        ids = nutzer.split(" ")
        logreason = f"{interaction.user} - {datetime.date.today().strftime(f'%d.%m.%Y')}: {grund}"
        erfolgreich = f"{icon_accept} Von **{len(ids)} Nutzern** wurden die Stummschaltung entfernt!"
        abbruch = f"{icon_denied} Das Verfahren zum entfernen der Stummschaltung wurde abgebrochen!"
        frage = f"Der massen entfernen von Stummschaltungen beinhaltet **{len(ids)} Nutzer**, möchtest du fortfahren?"
        laden = f"{icon_loading} Von **{len(ids)} Nutzer** wird die Stummschaltung entfernt . . ."

        await interaction.response.send_message(content=bannutzer)
        class Mehr(discord.ui.View):
            bot = self.bot
            async def on_timeout(self):
                pass
            @discord.ui.button(label="Stummschaltung aufheben", style=discord.ButtonStyle.green, emoji=icon_accept)
            async def unstumm(self, interaction: discord.Interaction, button: discord.ui.Button):
                global user
                #for button in self.children:
                #    button.disabled = True
                await interaction.response.edit_message(content=laden, view=None)
                for id in ids:
                    try:
                        user = await self.bot.fetch_user(id)
                        await user.timeout(None, reason=logreason)
                    except discord.HTTPException:
                        pass
                #fmt = "\n".join(
                      #"{id}\tErstellt: {c}\t{m}".format(id=m.id, c=m.created_at.strftime(f'%d.%m.%Y %H:%M:%S'),
                                                        #m=str(m)) for m in user)
                content = f"Anzahl der gebannten Nutzer: {len(ids)}"
                #file = discord.File(io.BytesIO(content.encode('utf-8')), filename='multiban.txt')
                await interaction.response.edit_message(content=erfolgreich, view=None)
            @discord.ui.button(label="Abbrechen", style=discord.ButtonStyle.red, emoji=icon_denied)
            async def abbrechen(self, interaction: discord.Interaction, button: discord.ui.Button):
                for button in self.children:
                    button.disabled = True
                await interaction.response.edit_message(content=abbruch, view=None)
        await interaction.edit_original_response(content=frage, view=Mehr())

    @mass.command(name="kick", description="Kicke mehrere Nutzer vom Server")
    @app_commands.describe(nutzer="Wer soll gekickt werden?",
                           grund="Für welchen Grund möchtest du die Nutzer kicken?")
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.checks.bot_has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, nutzer: str, grund: str = None):
        if grund is None:
            grund = "Kein Grund angegeben"
        bannutzer = f"{icon_loading} Die IDs werden gesucht . . ."
        ids = nutzer.split(" ")
        logreason = f"{interaction.user} - {datetime.date.today().strftime(f'%d.%m.%Y')}: {grund}"
        erfolgreich = f"{icon_accept} Es wurden **{len(ids)} Nutzer** gekickt!"
        abbruch = f"{icon_denied} Das Kickverfahren wurde abgebrochen!"
        frage = f"Der massen Kick beinhaltet **{len(ids)} Nutzer**, möchtest du fortfahren?"
        laden = f"{icon_loading} **{len(ids)} Nutzer** werden gekickt . . ."

        await interaction.response.send_message(content=bannutzer)
        class Mehr(discord.ui.View):
            bot = self.bot
            async def on_timeout(self):
                pass
            @discord.ui.button(label="Kicken", style=discord.ButtonStyle.green, emoji=icon_accept)
            async def bannen(self, interaction: discord.Interaction, button: discord.ui.Button):
                global user
                #for button in self.children:
                #    button.disabled = True
                await interaction.response.edit_message(content=laden, view=None)
                for id in ids:
                    try:
                        user = await self.bot.fetch_user(id)
                        await interaction.guild.kick(user, reason=logreason)
                    except discord.HTTPException:
                        pass
                #fmt = "\n".join(
                      #"{id}\tErstellt: {c}\t{m}".format(id=m.id, c=m.created_at.strftime(f'%d.%m.%Y %H:%M:%S'),
                                                        #m=str(m)) for m in user)
                content = f"Anzahl der gebannten Nutzer: {len(ids)}"
                #file = discord.File(io.BytesIO(content.encode('utf-8')), filename='multiban.txt')
                await interaction.response.edit_message(content=erfolgreich, view=None)
            @discord.ui.button(label="Abbrechen", style=discord.ButtonStyle.red, emoji=icon_denied)
            async def abbrechen(self, interaction: discord.Interaction, button: discord.ui.Button):
                for button in self.children:
                    button.disabled = True
                await interaction.response.edit_message(content=abbruch,view=None)
        await interaction.edit_original_response(content=frage, view=Mehr())

    @mass.command(name="ban", description="Banne mehrere Nutzer vom Server")
    @app_commands.describe(nutzer="Wer soll gebannt werden?",
                           grund="Für welchen Grund möchtest du die Nutzer bannen?")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, nutzer: str, grund: str = None):
        if grund is None:
            grund = "Kein Grund angegeben"
        bannutzer = f"{icon_loading} Die IDs werden gesucht . . ."
        ids = nutzer.split(" ")
        logreason = f"{interaction.user} - {datetime.date.today().strftime(f'%d.%m.%Y')}: {grund}"
        erfolgreich = f"{icon_accept} Es wurden **{len(ids)} Nutzer** gebannt!"
        abbruch = f"{icon_denied} Das Bannverfahren wurde abgebrochen!"
        frage = f"Der massen Bann beinhaltet **{len(ids)} Nutzer**, möchtest du fortfahren?"
        laden = f"{icon_loading} **{len(ids)} Nutzer** werden gebannt . . ."

        await interaction.response.send_message(content=bannutzer)
        class Mehr(discord.ui.View):
            bot = self.bot
            async def on_timeout(self):
                pass
            @discord.ui.button(label="Bannen", style=discord.ButtonStyle.green, emoji=icon_accept)
            async def bannen(self, interaction: discord.Interaction, button: discord.ui.Button):
                global user
                #for button in self.children:
                #    button.disabled = True
                await interaction.response.edit_message(content=laden, view=None)
                for id in ids:
                    try:
                        user = await self.bot.fetch_user(id)
                        await interaction.guild.ban(user, reason=logreason, delete_message_days=0)
                    except discord.HTTPException:
                        pass
                #fmt = "\n".join(
                      #"{id}\tErstellt: {c}\t{m}".format(id=m.id, c=m.created_at.strftime(f'%d.%m.%Y %H:%M:%S'),
                                                        #m=str(m)) for m in user)
                content = f"Anzahl der gebannten Nutzer: {len(ids)}"
                #file = discord.File(io.BytesIO(content.encode('utf-8')), filename='multiban.txt')
                await interaction.response.edit_message(content=erfolgreich, view=None)
            @discord.ui.button(label="Abbrechen", style=discord.ButtonStyle.red, emoji=icon_denied)
            async def abbrechen(self, interaction: discord.Interaction, button: discord.ui.Button):
                for button in self.children:
                    button.disabled = True
                await interaction.response.edit_message(content=abbruch, view=None)
        await interaction.edit_original_response(content=frage, view=Mehr())

    @mass.command(name="unban", description="Entbanne mehrere Nutzer vom Server")
    @app_commands.describe(nutzer="Wer soll entbannt werden?",
                           grund="Für welchen Grund möchtest du die Nutzer entbannen?")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, nutzer: str, grund: str = None):
        if grund is None:
            grund = "Kein Grund angegeben"
        bannutzer = f"{icon_loading} Die IDs werden gesucht . . ."
        ids = nutzer.split(" ")
        logreason = f"{interaction.user} - {datetime.date.today().strftime(f'%d.%m.%Y')}: {grund}"
        erfolgreich = f"{icon_accept} Es wurden **{len(ids)} Nutzer** entbannt!"
        abbruch = f"{icon_denied} Das Entbannungsverfahren wurde abgebrochen!"
        frage = f"Die massen Entbannung beinhaltet **{len(ids)} Nutzer**, möchtest du fortfahren?"
        laden = f"{icon_loading} **{len(ids)} Nutzer** werden entbannt . . ."

        await interaction.response.send_message(content=bannutzer)
        class Mehr(discord.ui.View):
            bot = self.bot
            async def on_timeout(self):
                pass
            @discord.ui.button(label="Entbannen", style=discord.ButtonStyle.green, emoji=icon_accept)
            async def bannen(self, interaction: discord.Interaction, button: discord.ui.Button):
                global user
                #for button in self.children:
                #    button.disabled = True
                await interaction.response.edit_message(content=laden, view=None)
                for id in ids:
                    try:
                        user = await self.bot.fetch_user(id)
                        await interaction.guild.unban(user, reason=logreason)
                    except discord.HTTPException:
                        pass
                #fmt = "\n".join(
                      #"{id}\tErstellt: {c}\t{m}".format(id=m.id, c=m.created_at.strftime(f'%d.%m.%Y %H:%M:%S'),
                                                        #m=str(m)) for m in user)
                content = f"Anzahl der entbannten Nutzer: {len(ids)}"
                #file = discord.File(io.BytesIO(content.encode('utf-8')), filename='multiban.txt')
                #await interaction.response.edit_message(content=erfolgreich, view=None)
                await interaction.edit_original_response(content=erfolgreich, view=None)
            @discord.ui.button(label="Abbrechen", style=discord.ButtonStyle.red, emoji=icon_denied)
            async def abbrechen(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.edit_message(content=abbruch, view=None)
        await interaction.edit_original_response(content=frage, view=Mehr())
        
    @mass.command(name="timeban", description="Banne mehrere Nutzer vom Server, welche ab einem bestimmten Zeitpunkt beigetreten sind")
    @app_commands.describe(joinlaenge="Bis zu welchem Zeitpunkt soll gebannt werden? (Angabe in Minuten)",
                           grund="Für welchen Grund möchtest du den Nutzer bannen?")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    async def timeban(self, interaction: discord.Interaction,  joinlaenge: int, grund: str = None):
        nutzer = []
        bannutzer = f"{icon_loading} Die Nutzer werden gesucht . . ."
        logreason = f"{interaction.user} - {datetime.date.today().strftime(f'%d.%m.%Y')}: {grund}"
        not_found = f"{icon_denied} Es wurden keine passenden Nutzer gefunden!"
        too_high = f"{icon_denied} Die angegebene Minutenanzahl ist zu hoch!"
        await interaction.response.send_message(content=bannutzer)

        if joinlaenge > 999999999:
            return await interaction.edit_original_response(content=too_high)
        zeit = datetime.datetime.now().astimezone() - datetime.timedelta(minutes=joinlaenge)

        async for member in interaction.guild.fetch_members(limit=None):
            if member.joined_at > zeit:
                nutzer.append(member.id)
        if len(nutzer) == 0:
            return await interaction.edit_original_response(content=not_found)
        erfolgreich = f"{icon_accept} Es wurden **{len(nutzer)} Nutzer** zwischen " \
                      f"<t:{int(zeit.timestamp())}:f> und <t:{int(datetime.datetime.now().astimezone().timestamp())}:f> gebannt!"
        abbruch = f"{icon_denied} Das Bannverfahren wurde abgebrochen!"
        frage = f"Der massen Bann beinhaltet **{len(nutzer)} Nutzer**, möchtest du fortfahren?"
        laden = f"{icon_loading} **{len(nutzer)} Nutzer** werden gebannt . . ."
        class Mehr(discord.ui.View):
            bot = self.bot
            async def on_timeout(self):
                pass
            @discord.ui.button(label="Bannen", style=discord.ButtonStyle.green, emoji=icon_accept)
            async def bannen(self, interaction: discord.Interaction, button: discord.ui.Button):
                global member
                await interaction.message.edit(content=laden, view=None)
                for id in nutzer:
                    try:
                        user = await self.bot.fetch_user(id)
                        await interaction.guild.ban(user, reason=logreason, delete_message_days=0)
                    except discord.HTTPException:
                        pass
                # fmt = "\n".join(
                # "{id}\tErstellt: {c}\t{m}".format(id=m.id, c=m.created_at.strftime(f'%d.%m.%Y %H:%M:%S'),
                # m=str(m)) for m in user)
                content = f"Anzahl der gebannten Nutzer: {len(nutzer)}"
                # file = discord.File(io.BytesIO(content.encode('utf-8')), filename='multiban.txt')
                await interaction.message.edit(content=erfolgreich, view=None)

            @discord.ui.button(label="Abbrechen", style=discord.ButtonStyle.red, emoji=icon_denied)
            async def abbrechen(self, interaction: discord.Interaction, button: discord.ui.Button):
                for button in self.children:
                    button.disable = True
                await interaction.message.edit(content=abbruch, view=None)

        await interaction.edit_original_response(content=frage, view=Mehr())

async def setup(bot: commands.Bot):
    await bot.add_cog(Mass(bot))#, guilds=[discord.Object(id=756526359521656951)])