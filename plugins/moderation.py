import discord
import datetime
import discord.errors
import json
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
from Utils.formatting import *

neuGrund = [
    ("ad", "Eigen-/Werbung"),
    ("dm", "Werbung via Direktnachricht"),
    ("age", "Minderjährig (unter 13 Jahre)"),
    ("u13", "Minderjährig (unter 13 Jahre)"),
    ("acc", "Account Handel"),
    ("talk", "Beleidigung im Sprachkanal"),
    ("voice", "Beleidigung im Sprachkanal"),
    ("scam", "Versenden von Discord Scam Einladungen"),
    ("hack", "Versenden von Discord Scam Einladungen"),
    ("sup", "Ausnutzung des Ticketsystems"),
    ("raid", "Teilnahme an einem Raid"),
    ("profil", "Unangebrachtes Profil"),
    ("chat", "Unangemessenes Chatverhalten"),
    ("rude", "Beleidigendes Verhalten"),
    ("alt", "Umgehung eines Banns")
]

def get_banmsg(client, ctx):
    with open("Legolas/datenbank/bannotify.json", "r") as f:
        banmsg = json.load(f)
        return banmsg[str(ctx.guild.id)]

class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def _has_ban_permissions(interaction: discord.Interaction, user: discord.User):
        if user in interaction.guild.members:
            member = interaction.guild.get_member(user.id)  # von User zu Member
            if member.top_role >= interaction.guild.me.top_role:
                await interaction.response.send_message(f"{icon_denied} Der Nutzer muss in der Serverhierarchie unter mir sein!", ephemeral=True)
                return False

            if interaction.user.top_role <= member.top_role:
                await interaction.response.send_message(f"{icon_denied} Der Nutzer muss in der Serverhierarchie unter dir sein!", ephemeral=True)
                return False
        return True

    @staticmethod
    async def _has_kick_permissions(interaction: discord.Interaction, member: discord.Member):
        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message(f"{icon_denied} Der Nutzer muss in der Serverhierarchie unter mir sein!")
            return False

        if interaction.user.top_role <= member.top_role:
            await interaction.response.send_message(f"{icon_denied} Der Nutzer muss in der Serverhierarchie unter dir sein!")
            return False
        return True



    @app_commands.command(name="channel", description="Ent-/sperrt einen Kanal")
    @app_commands.describe(aktion="Welche Aktion möchtest du durchführen?",
                           kanal="Welchen Kanal möchtest du sperren?")
    @app_commands.choices(aktion=[Choice(name="sperren", value=1),
                                  Choice(name="entsperren", value=2)])
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_channels=True, send_messages=True)
    async def lock(self, interaction: discord.Interaction, aktion: Choice[int], kanal: discord.TextChannel = None):
        logreason = f"Befehl ausgeführt von {interaction.user}"
        if kanal is None:
            kanal = interaction.channel
        await interaction.response.defer(ephemeral=True)
        if aktion.value == 1:
            overwrite = kanal.overwrites_for(interaction.guild.default_role)
            # overwrite.view_channel = False
            overwrite.send_messages = False
            await kanal.set_permissions(interaction.guild.default_role, overwrite=overwrite, reason=logreason)
            await kanal.send(content=f"**Hinweis**: Der Kanal wurde vorübergehend gesperrt!")
            await interaction.edit_original_response(content=f"{icon_accept} Der Kanal {kanal.mention} wurde gesperrt!")
        if aktion.value == 2:
            overwrite = kanal.overwrites_for(interaction.guild.default_role)
            # overwrite.view_channel = False
            overwrite.send_messages = None
            await kanal.set_permissions(interaction.guild.default_role, overwrite=overwrite, reason=logreason)
            await kanal.send(content=f"**Hinweis**: Die Kanalsperrung wurde aufgehoben!")
            await interaction.edit_original_response(content=f"{icon_accept} Der Kanal {kanal.mention} wurde entsperrt!")

    @app_commands.command(name="slowmode", description="Setze den Cooldown für einen Kanal")
    @app_commands.describe(sekunden="Auf welche Zeit soll der Cooldown gestellt werden?",
                           kanal="Für welchen Kanal möchtest du dies durchführen?")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, sekunden: int, kanal: discord.TextChannel = None):
        logreason = f"Befehl ausgeführt von {interaction.user}"
        if kanal is None:
            kanal = interaction.channel
        await interaction.response.defer(ephemeral=True)
        await kanal.edit(slowmode_delay=sekunden, reason=logreason)
        nachricht = f"{icon_accept} Der Slowmode des Kanales {kanal.mention} wurde auf **{sekunden} Sekunden** gesetzt!"
        class Mehr(discord.ui.View):
            @discord.ui.button(label="Zurücksetzen", style=discord.ButtonStyle.primary, emoji=icon_reset)
            async def reset(self, interaction: discord.Interaction, button: discord.ui.Button):
                button.disabled = True
                await kanal.edit(slowmode_delay=0, reason=logreason)
                await interaction.response.edit_message(content=nachricht + f"\n\n{icon_accept} Der Slowmode wurde zurückgesetzt!", view=self)
        await interaction.edit_original_response(content=nachricht, view=Mehr())

    @app_commands.command(name="purge", description="Löscht eine bestimmte Anzahl an Nachrichten")
    @app_commands.describe(anzahl="Wie viele Nachrichten möchtest du löschen?",
                           kanal="Für welchen Kanal möchtest du dies durchführen?")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, anzahl: int, nutzer: discord.User = None, kanal: discord.TextChannel = None):
        if kanal is None:
            kanal = interaction.channel
        if nutzer is not None:
            check = lambda msg: msg.author == nutzer and not msg.pinned
        else:
            check = lambda msg: not msg.pinned
        erfolgreich = f"{icon_accept} Im Kanal {kanal.mention} wurden **{anzahl} Nachrichten** gelöscht!"
        await interaction.response.defer(ephemeral=True)
        await kanal.purge(limit=anzahl, check=check, bulk=True, reason=f"Befehl ausgeführt von {interaction.user}")
        await interaction.edit_original_response(content=erfolgreich)

    @app_commands.command(name="mute", description="Schalte einen Nutzer stumm")
    @app_commands.describe(nutzer="Wer soll stumm geschaltet werden?",
                           stunden="Wie viele Stunden soll der Nutzer stummgeschalten werden?",
                           minuten="Wie viele Minuten soll der Nutzer stummgeschalten werden?",
                           grund="Für welchen Grun möchtest du den Nutzer stummschalten?",
                           loeschen="Wie viele Nachrichten sollen gelöscht werden?",
                           benachrichtigung="Soll der Nutzer eine Benachrichtigung erhalten?")
    @app_commands.choices(benachrichtigung=[Choice(name="deaktiviert", value=1)])
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.checks.bot_has_permissions(moderate_members=True, manage_messages=True)
    async def mute(self, interaction: discord.Interaction, nutzer: discord.Member, stunden: int = None, minuten: int = None, grund: str = None, benachrichtigung: Choice[int] = None, loeschen: int = None):
        if not await Mod._has_kick_permissions(interaction, nutzer):
            return
        await interaction.response.defer(ephemeral=False)
        if minuten is None and stunden is None:
            stunden = 2
            minuten = 0
        if stunden is None:
            stunden = 0
        if minuten is None:
            minuten = 0
        if grund is not None:
            for old, new in neuGrund:
                grund = grund.replace(old, new)
        else:
            grund = "Kein Grund angegeben"
        erfolgreich = f"{icon_accept} Der Nutzer **{nutzer}** wurde **{stunden} Stunden und {minuten} Minuten** stummgeschalten!"
        erfolgreichdm = f" (📫)"
        erfolgreichdel = f"\n`>` {loeschen} Nachrichten gelöscht"
        nachricht = erfolgreich
        fehler = f"{icon_denied} Die Zeit darf maximal 28 Tage sein!"
        logreason = f"{interaction.user} - {datetime.date.today().strftime(f'%d.%m.%Y')}: {grund}"
        delta = datetime.timedelta(hours=stunden, minutes=minuten)
        max = datetime.timedelta(days=27, hours=23, minutes=59, seconds=59)
        time = (datetime.datetime.now().astimezone() + delta)
        embed = discord.Embed(title=f"Du wurdest auf {interaction.guild} stummgeschaltet!",
                              description=f"```{grund}```",
                              color=color_red)
        embed.add_field(name="**Länge**",
                        value=f">>> {stunden} Stunden und {minuten} Minuten",
                        inline=False)
        embed.set_footer(text=f"{interaction.guild} ({interaction.guild.id})", icon_url=interaction.guild.icon.url)

        if not delta < max:
            return await interaction.edit_original_response(content=fehler)
        else:
            if benachrichtigung is None:
                try:
                    await nutzer.send(embed=embed)
                    nachricht += erfolgreichdm
                except:
                    pass
            await nutzer.timeout(time, reason=logreason)
            if loeschen is not None:
                await nutzer.purge(limit=loeschen)
                nachricht += erfolgreichdel
            await interaction.edit_original_response(content=nachricht)

    @app_commands.command(name="unmute", description="Schalte einen Nutzer stumm")
    @app_commands.describe(nutzer="Wer soll stumm geschaltet werden?",
                           grund="Für welchen Grun möchtest du den Nutzer stummschalten?",
                           benachrichtigung="Soll der Nutzer eine Benachrichtigung erhalten?")
    @app_commands.choices(benachrichtigung=[Choice(name="deaktiviert", value=1)])
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.checks.bot_has_permissions(moderate_members=True, manage_messages=True)
    async def unmute(self, interaction: discord.Interaction, nutzer: discord.Member, grund: str = None, benachrichtigung: Choice[int] = None):
        if not await Mod._has_kick_permissions(interaction, nutzer):
            return
        await interaction.response.defer(ephemeral=False)
        if grund is None:
            grund = "Kein Grund angegeben"
        erfolgreich = f"{icon_accept} Dem Nutzer **{nutzer}** wurde die Stummschaltung entfernt!"
        erfolgreichdm = f" (📫)"
        nachricht = erfolgreich
        logreason = f"{interaction.user} - {datetime.date.today().strftime(f'%d.%m.%Y')}: {grund}"
        embed = discord.Embed(title=f"Deine stummschaltung auf {interaction.guild} wurde entfernt!",
                              description=f"```{grund}```",
                              color=color_green)
        embed.set_footer(text=f"{interaction.guild} ({interaction.guild.id})", icon_url=interaction.guild.icon.url)
        if benachrichtigung is None:
            try:
                await nutzer.send(embed=embed)
                nachricht += erfolgreichdm
            except:
                pass
        await nutzer.timeout(None, reason=logreason)
        await interaction.edit_original_response(content=nachricht)

    @app_commands.command(name="kick", description="Schmeiße einen Nutzer vom Server")
    @app_commands.describe(nutzer="Wer soll geschmissen werden?",
                           grund="Für welchen Grund möchtest du den Nutzer schmeißen?",
                           benachrichtigung="Soll der Nutzer eine Benachrichtigung erhalten?",
                           loeschen="Von wie vielen Tagen sollen die Nachrichten gelöscht werden?")
    @app_commands.choices(benachrichtigung=[Choice(name="deaktiviert", value=1)])
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.checks.bot_has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, nutzer: discord.Member, grund: str = None, benachrichtigung: Choice[int] = None, loeschen: int = None):
        if not await Mod._has_kick_permissions(interaction, nutzer):
            return
        await interaction.response.defer(ephemeral=False)
        if grund is not None:
            for old, new in neuGrund:
                grund = grund.replace(old, new)
        else:
            grund = "Kein Grund angegeben"
        erfolgreich = f"{icon_accept} Der Nutzer **{nutzer}** wurde gekickt!"
        erfolgreichdm = f" (📫)"
        erfolgreichdel = f"\n`>` Von {loeschen} Tagen die Nachrichten gelöscht"
        nachricht = erfolgreich
        logreason = f"{interaction.user} - {datetime.date.today().strftime(f'%d.%m.%Y')}: {grund}"
        embed = discord.Embed(title=f"Du wurdest von {interaction.guild} geworfen!",
                              description=f"```{grund}```",
                              color=color_red)
        embed.set_footer(text=f"{interaction.guild} ({interaction.guild.id})", icon_url=interaction.guild.icon.url)
        if benachrichtigung is None:
            try:
                await nutzer.send(embed=embed)
                nachricht += erfolgreichdm
            except:
                pass
        if loeschen is not None:
            await interaction.guild.ban(nutzer, reason=grund, delete_message_days=loeschen)
            await interaction.guild.unban(nutzer, reason=grund)
            nachricht += erfolgreichdel
        else:
            await interaction.guild.kick(nutzer, reason=logreason)
        await interaction.edit_original_response(content=nachricht)

    @app_commands.command(name="ban", description="Banne einen Nutzer vom Server")
    @app_commands.describe(nutzer="Wer soll gebannt werden?",
                           grund="Für welchen Grund möchtest du den Nutzer bannen?",
                           benachrichtigung="Soll der Nutzer eine Benachrichtigung erhalten?",
                           loeschen="Von wie vielen Tagen sollen die Nachrichten gelöscht werden?")
    @app_commands.choices(benachrichtigung=[Choice(name="deaktiviert", value=1)])
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, nutzer: discord.User, grund: str = None, benachrichtigung: Choice[int] = None, loeschen: int = None):
        if not await Mod._has_ban_permissions(interaction, nutzer):
            return
        await interaction.response.defer(ephemeral=False)
        if grund is not None:
            for old, new in neuGrund:
                grund = grund.replace(old, new)
        else:
            grund = "Kein Grund angegeben"
        if loeschen is None:
            loeschen = 0
        msg = get_banmsg(self, interaction)
        erfolgreich = f"{icon_accept} Der Nutzer **{nutzer}** wurde gebannt!"
        erfolgreichdm = f" (📫)"
        erfolgreichdel = f"\n`>` Von {loeschen} Tagen die Nachrichten gelöscht"
        logreason = f"{interaction.user} - {datetime.date.today().strftime(f'%d.%m.%Y')}: {grund}"
        nachricht = erfolgreich
        embed = discord.Embed(title=f"Du wurdest von {interaction.guild} ausgeschlossen!",
                              description=f"```{grund}```",
                              color=color_red)
        if msg:
            embed.add_field(name="**Anmerkung**",
                            value=f"{msg}",
                            inline=False)
        embed.set_footer(text=f"{interaction.guild} ({interaction.guild.id})", icon_url=interaction.guild.icon.url)

        if benachrichtigung is None:
            try:
                await nutzer.send(embed=embed)
                nachricht += erfolgreichdm
            except:
                pass
        await interaction.guild.ban(nutzer, reason=logreason, delete_message_days=loeschen)
        if loeschen != 0:
            nachricht += erfolgreichdel
        await interaction.edit_original_response(content=nachricht)

    @app_commands.command(name="unban", description="Entbannt einen Nutzer vom Server")
    @app_commands.describe(nutzer="Wer soll entbannt werden?",
                           grund="Für welchen Grund möchtest du den Nutzer bannen?")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, nutzer: discord.User, grund: str = None):
        if not await Mod._has_ban_permissions(interaction, nutzer):
            return
        await interaction.response.defer(ephemeral=False)
        if grund is None:
            grund = "Kein Grund angegeben"
        erfolgreich = f"{icon_accept} Der Nutzer **{nutzer}** wurde entbannt!"
        fehler = f"{icon_denied} Der Nutzer **{nutzer}** ist nicht gebannt!"
        logreason = f"{interaction.user} - {datetime.date.today().strftime(f'%d.%m.%Y')}: {grund}"
        try:
            await interaction.guild.unban(nutzer, reason=logreason)
            await interaction.edit_original_response(content=erfolgreich)
        except discord.unknown_ban:
            await interaction.edit_original_response(content=fehler)



    @commands.command(name="unban", aliases=["ub"], description="Entbanne einen Nutzer", usage="unban <Nutzer> [Grund]")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def cunban(self, ctx, nutzer: discord.User, grund: str = None):
        async with ctx.channel.typing():
            if grund is None:
                grund = "Kein Grund angegeben"
            erfolgreich = f"{icon_accept} Der Nutzer **{nutzer}** wurde entbannt!"
            fehler = f"{icon_denied} Der Nutzer **{nutzer}** ist nicht gebannt!"
            logreason = f"{ctx.author} - {datetime.date.today().strftime(f'%d.%m.%Y')}: {grund}"
            try:
                await ctx.guild.unban(nutzer, reason=logreason)
                await ctx.reply(erfolgreich, mention_author=False)
            except discord.unknown_ban:
                await ctx.reply(fehler, mention_author=False)

    @commands.command(name="ban", aliases=["b"], description="Banne einen Nutzer", usage="ban <Nutzer> [Grund]")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def cban(self, ctx, nutzer: discord.User, *, grund=None):
        async with ctx.channel.typing():
            if grund is not None:
                for old, new in neuGrund:
                    grund = grund.replace(old, new)
            else:
                grund = "Kein Grund angegeben"
            msg = get_banmsg(self, ctx)
            erfolgreich = f"{icon_accept} Der Nutzer **{nutzer}** wurde gebannt!"
            erfolgreichdm = f" (📫)"
            logreason = f"{ctx.author} - {datetime.date.today().strftime(f'%d.%m.%Y')}: {grund}"
            nachricht = erfolgreich
            embed = discord.Embed(title=f"Du wurdest von {ctx.guild} ausgeschlossen!",
                                  description=f"```{grund}```",
                                  color=color_red)
            if msg:
                embed.add_field(name="**Anmerkung**",
                                value=f"{msg}",
                                inline=False)
            embed.set_footer(text=f"{ctx.guild} ({ctx.guild.id})", icon_url=ctx.guild.icon.url)
            try:
                await nutzer.send(embed=embed)
                nachricht += erfolgreichdm
            except:
                pass
            await ctx.guild.ban(nutzer, reason=logreason, delete_message_days=0)
            await ctx.message.delete()
            await ctx.send(content=nachricht)

    @commands.command(name="softban", aliases=["soban"], description="Banne einen Nutzer mit Nachrichten löschen", usage="ban <Nutzer> <Tage> [Grund]")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def csoban(self, ctx, nutzer: discord.User, tage: int, *, grund=None):
        async with ctx.channel.typing():
            if grund is not None:
                for old, new in neuGrund:
                    grund = grund.replace(old, new)
            else:
                grund = "Kein Grund angegeben"
            msg = get_banmsg(self, ctx)
            erfolgreich = f"{icon_accept} Der Nutzer **{nutzer}** wurde gebannt!"
            erfolgreichdm = f" (📫)"
            erfolgreichdel = f"\n`>` Von {tage} Tagen die Nachrichten gelöscht"
            logreason = f"{ctx.author} - {datetime.date.today().strftime(f'%d.%m.%Y')}: {grund}"
            nachricht = erfolgreich
            embed = discord.Embed(title=f"Du wurdest von {ctx.guild} ausgeschlossen!",
                                  description=f"```{grund}```",
                                  color=color_red)
            if msg:
                embed.add_field(name="**Anmerkung**",
                                value=f"{msg}",
                                inline=False)
            embed.set_footer(text=f"{ctx.guild} ({ctx.guild.id})", icon_url=ctx.guild.icon.url)
            try:
                await nutzer.send(embed=embed)
                nachricht += erfolgreichdm
            except:
                pass
            await ctx.guild.ban(nutzer, reason=logreason, delete_message_days=tage)
            await ctx.message.delete()
            await ctx.send(content=nachricht + erfolgreichdel)
        
    @commands.command(name="silentban", aliases=["siban"], description="Banne einen Nutzer ohne Benachrichtigung", usage="silentban <Nutzer> [Grund]")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def csiban(self, ctx, nutzer: discord.User, *, grund=None):
        async with ctx.channel.typing():
            if grund is not None:
                for old, new in neuGrund:
                    grund = grund.replace(old, new)
            else:
                grund = "Kein Grund angegeben"
            erfolgreich = f"{icon_accept} Der Nutzer **{nutzer}** wurde gebannt!"
            logreason = f"{ctx.author} - {datetime.date.today().strftime(f'%d.%m.%Y')}: {grund}"
            await ctx.guild.ban(nutzer, reason=logreason, delete_message_days=0)
            await ctx.message.delete()
            await ctx.send(content=erfolgreich)


async def setup(bot: commands.Bot):
    await bot.add_cog(Mod(bot))  # , guilds=[discord.Object(id=756526359521656951)])