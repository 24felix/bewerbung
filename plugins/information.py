import re
import io
import time
import typing
import discord
import datetime
import requests
import discord.errors
from discord import ui
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from Utils.formatting import *

class PartialEmoji(typing.NamedTuple):
    x: discord.PartialEmoji
    y: discord.PartialEmoji

class getEmojis(app_commands.Transformer):
    @classmethod
    async def transform(cls, interaction: discord.Interaction, input: str):
        findEmojis = re.findall("<?(a)?:?(\w{2,32}):(\d{14,22})>", input)
        foundedEmojis = [{"name": emoji[1], "id": str(emoji[2]), "animated": emoji[0] == "a" if True else False} for emoji in findEmojis]
        if not (len(foundedEmojis) == 0):
            emojis = []
            for emoji in foundedEmojis:
                if emoji["animated"]:
                    emoji["url"] = f"https://cdn.discordapp.com/emojis/{emoji['id']}.gif"
                else:
                    emoji["url"] = f"https://cdn.discordapp.com/emojis/{emoji['id']}.png"
            emoji["created_at"] = f"<t:{int(datetime.datetime.timestamp(datetime.datetime.utcfromtimestamp(((int(emoji['id']) >> 22) + 1420070400000) / 1000)))}:R>"
            if emoji not in emojis:
                emojis.append(emoji)
            return emojis



class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    checks = app_commands.Group(name="check", description="Überprüfungsbefehle")
    infos = app_commands.Group(name="info", description="Informationsbefehle")
    emojis = app_commands.Group(name="emoji", description="Emojibefehle")

    @app_commands.command(name="about", description="Informationen zur Laufzeit, Partner usw.")
    async def about(self, interaction: discord.Interaction):
        laufzeit = datetime.timedelta(seconds=round(time.time() - self.bot.startzeit))
        embed1 = discord.Embed(title=f"Informationen über {self.bot.user.name}!",
                               description=f">>> Von [24felix](https://discord.com/users/252364399669542913) und [florian.lclr](https://discord.com/users/308320665403129866)",
                               color=color_gray)
        embed1.add_field(name=f"**Discord.py**",
                         value=f"```fix\n{discord.__version__}```")
        embed1.add_field(name=f"**Latenz**",
                         value=f"```fix\n{round(self.bot.latency * 1000)}ms```")
        embed1.add_field(name=f"**Laufzeit**",
                         value=f"```fix\n{laufzeit}```")
        embed1.add_field(name=f"**Betreute Server**",
                         value=f"```fix\n{len(self.bot.guilds)}```")
        embed1.add_field(name=f"**Betreute Nutzer**",
                         value=f"```fix\n{len(list(self.bot.get_all_members()))}```")
        buttons = discord.ui.View()
        buttons.add_item(discord.ui.Button(label="Support Server", style=discord.ButtonStyle.green,
                                           url=url_support))
        buttons.add_item(discord.ui.Button(label="Nutzungsbedingungen", style=discord.ButtonStyle.green,
                                           url=url_tos))
        buttons.add_item(discord.ui.Button(label="Datenschutzbestimmungen", style=discord.ButtonStyle.green,
                                           url=url_privacy))
        embed1.set_thumbnail(url=self.bot.user.display_avatar.url)
        await interaction.response.send_message(embed=embed1, view=buttons, ephemeral=False)

    @checks.command(name="ban", description="Überprüft ob ein Nutzer gebannt ist und mit welchem Grund")
    @app_commands.describe(nutzer="Welchen Nutzer möchtest du überprüfen?")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    async def bancheck(self, interaction: discord.Interaction, nutzer: discord.User):
        try:
            ban = await interaction.guild.fetch_ban(nutzer)
            nachricht = f"{icon_accept} Der Nutzer **{nutzer}** ist gebannt mit dem Grund```{ban.reason}```"
            class Unban(discord.ui.View):
                @discord.ui.button(label='Entbannen', style=discord.ButtonStyle.red)
                async def bancheckunban(self, interaction: discord.Interaction, button: discord.ui.Button):
                    class Questionnaire(ui.Modal, title=f"Moderation"):
                        answer = ui.TextInput(label="Entbannungsgrund", style=discord.TextStyle.short, required=True,
                                              placeholder=f"Bitte geben einen Grund für die Entbannung ein . . .")
                        async def on_submit(self, interaction: discord.Interaction):
                            reason1 = f'{interaction.user} - {datetime.date.today().strftime(f"%d.%m.%Y")}: {self.answer.value}'
                            await interaction.guild.unban(nutzer, reason=reason1)
                            await interaction.response.edit_message(content=nachricht + f"\n{icon_accept} Der Nutzer wurde entbannt!", view=None)
                    await interaction.response.send_modal(Questionnaire())
                    button.disabled = True
                    await interaction.edit_original_response(view=self)
            await interaction.response.send_message(content=nachricht, view=Unban(), ephemeral=False)
        except discord.NotFound:
            no = f"{icon_denied} Der Nutzer **{nutzer}** ist nicht gebannt!"
            await interaction.response.send_message(content=no, ephemeral=True)

    @checks.command(name="count", description="Überprüft die Bannliste auf einen Grund")
    @app_commands.describe(grund="Nach welchem Grund suchst du?")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    async def rolecheck(self, interaction: discord.Interaction, grund: str):
        anzahl = 0
        await interaction.response.defer(ephemeral=False)
        if not interaction.guild.chunked:
            await interaction.guild.chunk(cache=True)
        async for entry in interaction.guild.bans(limit=None):
            try:
                if grund in entry.reason:
                    anzahl += 1
            except TypeError:
                pass
        erfolgreich = f"{icon_accept} Es sind **{anzahl} Nutzer** mit dem Grund `{grund}` gebannt!"
        await interaction.edit_original_response(content=erfolgreich)

    @checks.command(name="role", description="Überprüft die Mitglieder einer Rolle")
    @app_commands.describe(rolle="Welche Rolle möchtest du überprüfen?")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    async def rolecheck(self, interaction: discord.Interaction, rolle: discord.Role):
        if not interaction.guild.chunked:
            await interaction.guild.chunk(cache=True)
        content = "\n".join(str(members.id) for members in rolle.members)
        file = discord.File(io.BytesIO(content.encode('utf-8')), filename='ids.txt')
        erfolgreich = f"{icon_accept} Die {rolle.mention} Rolle hat **{len(rolle.members)} Mitglieder**"
        await interaction.response.send_message(content=erfolgreich, file=file, ephemeral=False, allowed_mentions=discord.AllowedMentions(roles=False))

    @infos.command(name="avatar", description="Schaue den Avatar eines Nutzers an")
    @app_commands.describe(nutzer="Welchen Nutzer möchtest du begutachten?")
    async def avatar(self, interaction: discord.Interaction, nutzer: discord.User = None):
        if nutzer is None:
            nutzer = interaction.user
        member = await self.bot.fetch_user(nutzer.id)
        embed1 = discord.Embed(title="Benutzerinformationen",
                               description=f"Avatar vom Benutzer {nutzer.mention}")
        if member.accent_color is None:
            embed1.color = color_gray
        else:
            embed1.color = member.accent_color
        view = discord.ui.View()
        try:
            embed1.set_image(url=nutzer.guild_avatar.url)
            embed1.set_thumbnail(url=nutzer.avatar.url)
            view.add_item(discord.ui.Button(label="Server Avatar", style=discord.ButtonStyle.link, url=nutzer.guild_avatar.url))
            view.add_item(discord.ui.Button(label="Avatar", style=discord.ButtonStyle.link, url=nutzer.avatar.url))
        except AttributeError:
            embed1.set_image(url=nutzer.avatar.url)
            view.add_item(discord.ui.Button(label="Avatar", style=discord.ButtonStyle.link, url=nutzer.avatar.url))
        await interaction.response.send_message(embed=embed1, view=view, ephemeral=False)

    @infos.command(name="banner", description="Schaue den Banner eines Nutzers an")
    @app_commands.describe(nutzer="Welchen Nutzer möchtest du begutachten?")
    async def banner(self, interaction: discord.Interaction, nutzer: discord.User = None):
        if nutzer is None:
            nutzer = interaction.user
        member = await self.bot.fetch_user(nutzer.id)
        try:
            embed1 = discord.Embed(title="Benutzerinformationen",
                                   description=f"Banner vom Benutzer {nutzer.mention}")
            if member.accent_color is None:
                embed1.color = color_gray
            else:
                embed1.color = member.accent_color
            view = discord.ui.View()
            try:
                embed1.set_image(url=member.guild.banner.url)
                embed1.set_thumbnail(url=member.banner.url)
                view.add_item(discord.ui.Button(label="Server Banner", style=discord.ButtonStyle.link, url=member.guild.banner.url))
                view.add_item(discord.ui.Button(label="Banner", style=discord.ButtonStyle.link, url=member.banner.url))
            except AttributeError:
                embed1.set_image(url=member.banner.url)
                view.add_item(discord.ui.Button(label="Banner", style=discord.ButtonStyle.link, url=member.banner.url))
            await interaction.response.send_message(embed=embed1, view=view, ephemeral=False)
        except:
            await interaction.response.send_message(content=f"{icon_denied} Der Nutzer **{nutzer}** hat keinen Banner!", ephemeral=True)

    @infos.command(name="user", description="Lass dir Informationen über einen Nutzer anzeigen")
    @app_commands.describe(nutzer="Welchen Nutzer möchtest du begutachten?")
    async def user(self, interaction: discord.Interaction, nutzer: discord.User = None):
        if nutzer is None:
            nutzer = interaction.user
        member = await self.bot.fetch_user(nutzer.id)
        if nutzer in interaction.guild.members:
            embed1 = discord.Embed(title="Benutzerinformationen")
            if nutzer.is_on_mobile() is True:
                embed1.description = f"Information vom Benutzer {nutzer.mention} -> 📱"
            else:
                embed1.description = f"Information vom Benutzer {nutzer.mention}"
            if member.accent_color is None:
                embed1.color = color_gray
            else:
                embed1.color = member.accent_color
            embed1.add_field(name=f"**Nutzer**",
                             value=f"{nutzer} (`{nutzer.id}`)",
                             inline=False)
            if member.accent_color is not None and not nutzer.bot:
                embed1.add_field(name=f"**Sonderinformationen**",
                                 value=f"```Akzentfarbe: {member.accent_color}\n"
                                       f"Gemeinsame Server: {len(nutzer.mutual_guilds)}```",
                                 inline=False)
            elif member.accent_color is None and not nutzer.bot:
                embed1.add_field(name=f"**Sonderinformationen**",
                                 value=f"```Gemeinsame Server: {len(nutzer.mutual_guilds)}```",
                                 inline=False)
            elif not nutzer.bot:
                embed1.add_field(name=f"**Sonderinformationen**",
                                 value=f"```Akzentfarbe: {member.accent_color}```",
                                 inline=False)
            flag_string = ", ".join([f.name for f in nutzer.public_flags.all()])
            if len(flag_string) > 1:
                embed1.add_field(name=f"**Abzeichen**",
                                 value=f"```{flag_string}```",
                                 inline=False)
            embed1.add_field(name="**Accounterstellung**",
                             value=f"<t:{int(nutzer.created_at.timestamp())}:F> (<t:{int(nutzer.created_at.timestamp())}:R>)",
                             inline=False)
            embed1.add_field(name=f"**Serverbeitritt [#{str(interaction.guild.members.index(nutzer) + 1)}]**",
                             value=f"<t:{int(nutzer.joined_at.timestamp())}:F> (<t:{int(nutzer.joined_at.timestamp())}:R>)",
                             inline=False)
            if nutzer in interaction.guild.premium_subscribers:
                embed1.add_field(name="**Serverbooster**",
                                 value=f"<t:{int(nutzer.premium_since.timestamp())}:F> (<t:{int(nutzer.premium_since.timestamp())}:R>)",
                                 inline=False)
            if len(nutzer.roles) > 1:
                role_string = ", ".join([r.mention for r in nutzer.roles][1:])
                embed1.add_field(name=f"**Rollen [{len(nutzer.roles) - 1}]**",
                                 value=role_string,
                                 inline=False)
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="Avatar", style=discord.ButtonStyle.link, url=nutzer.display_avatar.url))
            embed1.set_thumbnail(url=nutzer.display_avatar.url)
            if member.banner:
                embed1.set_image(url=member.banner.url)
                view.add_item(discord.ui.Button(label="Banner", style=discord.ButtonStyle.link, url=member.banner.url))
            await interaction.response.send_message(embed=embed1, view=view, ephemeral=False)
        else:
            embed1 = discord.Embed(title="**Benutzerinformationen**",
                                   description=f"Information vom Benutzer {nutzer.mention}")
            if member.accent_color is None:
                embed1.color = color_gray
            else:
                embed1.color = member.accent_color
            embed1.add_field(name="**Nutzer**",
                             value=f"{nutzer} (`{nutzer.id}`)",
                             inline=False)
            if member.accent_color is not None and not nutzer.bot:
                embed1.add_field(name=f"**Sonderinformationen**",
                                 value=f"```Akzentfarbe: {member.accent_color}\n"
                                       f"Gemeinsame Server: {len(nutzer.mutual_guilds)}```",
                                 inline=False)
            elif member.accent_color is None and not nutzer.bot:
                embed1.add_field(name=f"**Sonderinformationen**",
                                 value=f"```Gemeinsame Server: {len(nutzer.mutual_guilds)}```",
                                 inline=False)
            elif not nutzer.bot:
                embed1.add_field(name=f"**Sonderinformationen**",
                                 value=f"```Akzentfarbe: {member.accent_color}```",
                                 inline=False)
            embed1.add_field(name="**Accounterstellung**",
                             value=f"<t:{int(nutzer.created_at.timestamp())}:F> (<t:{int(nutzer.created_at.timestamp())}:R>)",
                             inline=False)
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="Avatar", style=discord.ButtonStyle.link, url=nutzer.display_avatar.url))
            embed1.set_thumbnail(url=nutzer.display_avatar.url)
            if member.banner:
                embed1.set_image(url=member.banner.url)
                view.add_item(discord.ui.Button(label="Banner", style=discord.ButtonStyle.link, url=member.banner.url))
            await interaction.response.send_message(embed=embed1, view=view, ephemeral=False)

    @infos.command(name="server", description="Lass dir Informationen zu deinem Server anzeigen")
    async def server(self, interaction: discord.Interaction):
        if not interaction.guild.chunked:
            await interaction.guild.chunk(cache=True)
            
        if interaction.guild.description is not None:
            embed1 = discord.Embed(title="Serverinformationen",
                                   description=f">>> {interaction.guild.description}",
                                   color=color_gray)
        else:
            embed1 = discord.Embed(title="Serverinformationen",
                                   color=color_gray)
        embed1.add_field(name="**Server**",
                         value=f"{interaction.guild.name} (`{interaction.guild.id}`)",
                         inline=False)
        embed1.add_field(name="**Inhaber**",
                         value=f"{interaction.guild.owner} (`{interaction.guild.owner.id}`)",
                         inline=False)
        embed1.add_field(name="**Erstellung**",
                         value=f"<t:{int(interaction.guild.created_at.timestamp())}:F> (<t:{int(interaction.guild.created_at.timestamp())}:R>)",
                         inline=False)
        if interaction.guild.features:
            embed1.add_field(name="**Funktionen**",
                             value="\n".join([str("`>` " + f) for f in interaction.guild.features]),
                             inline=False)
        embed1.add_field(name="**Mitglieder**",
                         value=f"```{len([m for m in interaction.guild.members if not m.bot])}```")
        embed1.add_field(name="**Bots**",
                         value=f"```{len([m for m in interaction.guild.members if m.bot])}```")
        embed1.add_field(name="**Banns**",
                         value=f"```Deaktiviert```")
        embed1.add_field(name="**Rollen**",
                         value=f"```{len(interaction.guild.roles)}```")
        embed1.add_field(name="**Emojis**",
                         value=f"```{len(interaction.guild.emojis)}```")
        embed1.add_field(name="**Stickers**",
                         value=f"```{len(interaction.guild.stickers)}```")
        embed1.add_field(name=f"**Boost [{interaction.guild.premium_subscription_count} | Nutzer: {len(interaction.guild.premium_subscribers)}]**",
                         value=f"```Level: {interaction.guild.premium_tier} | Rolle: {interaction.guild.premium_subscriber_role}```",
                         inline=False)
        embed1.add_field(name=f"**Kanäle [{str(len(interaction.guild.text_channels) + len(interaction.guild.voice_channels))}]**",
                         value=f"```💬 {str(len(interaction.guild.text_channels))} | 🔊 {str(len(interaction.guild.voice_channels))} | 📁 {str(len(interaction.guild.categories))}```",
                         inline=False)
        embed1.set_thumbnail(url=interaction.guild.icon.url)
        if interaction.guild.banner:
            embed1.set_image(url=interaction.guild.banner.url)
        elif interaction.guild.discovery_splash:
            embed1.set_image(url=interaction.guild.discovery_splash.url)
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Icon", style=discord.ButtonStyle.link, url=interaction.guild.icon.url))
        if interaction.guild.banner:
            view.add_item(discord.ui.Button(label="Banner", style=discord.ButtonStyle.link, url=interaction.guild.banner.url))
        if interaction.guild.discovery_splash:
            view.add_item(discord.ui.Button(label="Splash", style=discord.ButtonStyle.link, url=interaction.guild.discovery_splash.url))
        await interaction.response.send_message(embed=embed1, view=view, ephemeral=False)

    @infos.command(name="invite", description="Lass dir Informationen über eine Einladung anzeigen")
    @app_commands.describe(einladung="Welche Aktion möchtest du durchführen?")
    async def invite(self, interaction: discord.Interaction, einladung: str):
        try:
            invite = await self.bot.fetch_invite(einladung, with_counts=True)
            embed1 = discord.Embed(title="Einladungsinformationen",
                                   color=color_gray)
            embed1.add_field(name="**Server**",
                             value=f"{invite.guild.name} (`{invite.guild.id}`)",
                             inline=False)
            if invite.inviter is None:
                embed1.add_field(name="**Einlader**",
                                 value=f"Discord",
                                 inline=False)
            else:
                embed1.add_field(name="**Einlader**",
                                 value=f"{invite.inviter} (`{invite.inviter.id}`)",
                                 inline=False)
            embed1.add_field(name="**Kanal**",
                             value=f"{invite.channel} (`{invite.channel.id}`)",
                             inline=False)
            embed1.add_field(name="**Servererstelllung**",
                             value=f"<t:{int(invite.guild.created_at.timestamp())}:F> (<t:{int(invite.guild.created_at.timestamp())}:R>)",
                             inline=False)
            if invite.guild.features:
                embed1.add_field(name="**Funktionen**",
                                 value="\n".join([str("`>` " + f) for f in invite.guild.features]),
                                 inline=False)
            embed1.add_field(name="**Mitglieder**",
                             value=f"```{invite.approximate_member_count} ({invite.approximate_presence_count} Online)```",
                             inline=False)
            embed1.set_thumbnail(url=invite.guild.icon.url)
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="Icon", style=discord.ButtonStyle.link, url=invite.guild.icon.url))
            if invite.guild.banner:
                embed1.set_image(url=invite.guild.banner.url)
                view.add_item(
                    discord.ui.Button(label="Banner", style=discord.ButtonStyle.link, url=invite.guild.banner.url))
            await interaction.response.send_message(content=invite, embed=embed1, view=view, ephemeral=False)
        except:
            await interaction.response.send_message(content=f"{icon_denied} Die Einladung `{einladung}` ist ungültig!", ephemeral=True)

    @emojis.command(name="add", description="Füge einen Emote zu deinem Server hinzu")
    @app_commands.describe(emoji="Um welchen Emoji handelt es sich?")
    @app_commands.checks.has_permissions(manage_emojis=True)
    @app_commands.checks.bot_has_permissions(manage_emojis=True)
    async def add(self, interaction: discord.Interaction, emoji: app_commands.Transform[str, getEmojis]):
        emoji = emoji[0]
        fehler = f"{icon_denied} Die angegebene URL ist ungültig!"
        try:
            antwort = requests.get(emoji["url"])
        except (requests.exceptions.MissingSchema, requests.exceptions.InvalidURL,
                requests.exceptions.InvalidSchema, requests.exceptions.ConnectionError):
            return await interaction.response.send_message(content=fehler, ephemeral=True)

        if antwort.status_code == 404:
            return await interaction.response.send_message(content=fehler, ephemeral=True)

        await interaction.response.defer(ephemeral=False)
        try:
            emoji = await interaction.guild.create_custom_emoji(name=emoji["name"], image=antwort.content)
        except discord.errors.InvalidArgument:
            return await interaction.edit_original_response(content="Ungültiger Dateityp")
        erfolgreich = icon_accept + " Der Emote <{1}:{0.name}:{0.id}> wurde zum Server hinzugefügt!".format(emoji, "a" if emoji.animated else "")
        await interaction.edit_original_response(content=erfolgreich)

    @emojis.command(name="info", description="Lasse dir Informationen zu einem Emoji anzeigen")
    @app_commands.describe(emoji="Um welchen Emoji handelt es sich?")
    async def info(self, interaction: discord.Interaction, emoji: app_commands.Transform[str, getEmojis]):
        emoji = emoji[0]
        embed = discord.Embed(title="Emoteinformationen",
                              color=0x7b68ee)
        embed.add_field(name="Name",
                        value=emoji['name'])
        embed.add_field(name="Emote ID",
                        value=emoji['id'])
        try:
            emoji1 = await discord.Guild.fetch_emoji(interaction.guild, emoji["id"])
            embed.add_field(name="Ersteller",
                            value=emoji1.user)
        except discord.NotFound:
            pass
        embed.add_field(name="Hinzugefügt",
                        value=f"<t:{int(datetime.datetime.timestamp(datetime.datetime.utcfromtimestamp(((int(emoji['id']) >> 22) + 1420070400000) / 1000)))}:F> (<t:{int(datetime.datetime.timestamp(datetime.datetime.utcfromtimestamp(((int(emoji['id']) >> 22) + 1420070400000) / 1000)))}:R>)",
                        inline=False)
        embed.set_thumbnail(url=emoji["url"])
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Link", style=discord.ButtonStyle.link, url=emoji["url"]))
        await interaction.response.send_message(embed=embed, view=view, ephemeral=False)

async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))#, guilds=[discord.Object(id=756526359521656951)])