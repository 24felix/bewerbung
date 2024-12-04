import io
import json
import aiohttp
import discord
import datetime
from datetime import timezone, datetime, timedelta
import discord.errors
from typing import Union
from discord import Webhook
from discord.ext import commands
from Utils.formatting import *

def get_messageloggingchannel(client, ctx):
    with open("Legolas/datenbank/messagelogging.json", "r") as c:
        webhook1 = json.load(c)
    return str(webhook1[str(ctx.guild.id)])

def get_serverloggingchannel(client, ctx):
    with open("Legolas/datenbank/serverlogging.json", "r") as c:
        webhook1 = json.load(c)
    return str(webhook1[str(ctx.guild.id)])

def get_joinrole(client, message):
    with open("Legolas/datenbank/joinrole.json", "r") as c:
        joinroles = json.load(c)
    return joinroles[str(message.guild.id)]

def get_memberlogging(client, message):
    with open("Legolas/datenbank/memberlogging.json", "r") as c:
        memberupdate = json.load(c)
    return str(memberupdate[str(message.guild.id)])

def get_voicelogging(client, message):
    with open("Legolas/datenbank/voicelogging.json", "r") as c:
        voicelog = json.load(c)
    return str(voicelog[str(message.channel.guild.id)])

def get_modlogging(client, ctx):
    with open("Legolas/datenbank/modlogging.json", "r") as c:
        webhook1 = json.load(c)
    return str(webhook1[str(ctx.id)])


class Log(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        link = f"https://discord.com/channels/{before.guild.id}/{before.channel.id}/{before.id}"
        async with aiohttp.ClientSession() as session:
            try:
                webhook = Webhook.from_url(get_messageloggingchannel(self, before), session=session)
                webhook = await Webhook.fetch(webhook, prefer_auth=True)
                if before.guild.id == webhook.guild_id:
                    try:
                        if before.author.bot:
                            return
                        elif len(after.embeds) > 1 or before.content == after.content:
                            return
                        else:
                            embed1 = discord.Embed(title=f"Nachricht bearbeitet",
                                                   description=f">>> **Kanal**: [{before.channel}]({before.channel.jump_url}) ({before.channel.mention})\n"
                                                               f"**Nutzer**: [{before.author}](https://discord.com/users/{before.author.id}) ({before.author.mention})\n"
                                                               f"**Nachricht**: [{before.id}]({before.jump_url})\n"
                                                               f"**Erstellt**: <t:{int(before.created_at.timestamp())}:F> (<t:{int(before.created_at.timestamp())}:R>)",
                                                   color=color_orange)

                            if len(before.content) > 1024:
                                vorher = discord.File(io.BytesIO(before.content.encode("utf-8")),
                                                      filename=f"vorher.txt")
                            else:
                                embed1.add_field(name=f"**Vorher**",
                                                 value=f"{before.content}",
                                                 inline=False)

                            if len(after.content) > 1024:
                                nachher = discord.File(io.BytesIO(after.content.encode("utf-8")),
                                                       filename=f"nachher.txt")
                            else:
                                embed1.add_field(name=f"**Nachher**",
                                                 value=f"{after.content}",
                                                 inline=False)
                            view = discord.ui.View()
                            view.add_item(discord.ui.Button(label="Zur Nachricht", style=discord.ButtonStyle.link, url=link))

                            if len(before.content) > 1024 and len(after.content) > 1024:
                                await webhook.send(embed=embed1, files=[vorher, nachher])
                            elif len(before.content) > 1024:
                                await webhook.send(embed=embed1, file=vorher)
                            elif len(after.content) > 1024:
                                await webhook.send(embed=embed1, file=nachher)
                            else:
                                await webhook.send(embed=embed1)
                    except KeyError:
                        return
                    except discord.errors.HTTPException:
                        return
            except KeyError:
                return
            except discord.errors.HTTPException:
                return

    @commands.Cog.listener()
    async def on_message_delete(self, ctx):
        """Message Log"""
        link = f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{ctx.id}"
        async with aiohttp.ClientSession() as session:
            try:
                webhook = Webhook.from_url(get_messageloggingchannel(self, ctx), session=session)
                webhook = await Webhook.fetch(webhook, prefer_auth=True)
                anhang = []
                if ctx.guild.id == webhook.guild_id:
                    try:
                        if ctx.author.bot:
                            return
                        else:
                            embed1 = discord.Embed(title=f"Nachricht gelöscht",
                                                   description=f">>> **Kanal**: [{ctx.channel}]({ctx.channel.jump_url}) ({ctx.channel.mention})\n"
                                                               f"**Nutzer**: [{ctx.author}](https://discord.com/users/{ctx.author.id}) ({ctx.author.mention})\n"
                                                               f"**Nachricht**: [{ctx.id}]({ctx.jump_url})\n"
                                                               f"**Erstellt**: <t:{int(ctx.created_at.timestamp())}:F> (<t:{int(ctx.created_at.timestamp())}:R>)",
                                                   color=color_red)
                            async for entry in ctx.guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete):
                                if entry.user.id != ctx.author.id:
                                    if entry.created_at > datetime.now(timezone.utc) - timedelta(seconds=2):
                                        embed1.set_footer(text=f"Moderator: {entry.user}",
                                                          icon_url=entry.user.display_avatar.url)
                            if ctx.attachments:
                                for bild in ctx.attachments:
                                    file = bild
                                    datei = await file.to_file()
                                    anhang.append(datei)
                            if len(ctx.content) > 1024:
                                anhang.append(discord.File(io.BytesIO(ctx.content.encode("utf-8")), filename=f"nachricht.txt"))
                            else:
                                embed1.add_field(name=f"**Nachricht**",
                                                 value=f"{ctx.content}",
                                                 inline=False)
                            view = discord.ui.View()
                            view.add_item(discord.ui.Button(label="Zur Nachrichtenstelle", style=discord.ButtonStyle.link, url=link))
                            if anhang:
                                await webhook.send(embed=embed1, files=anhang)
                            else:
                                await webhook.send(embed=embed1)
                    except KeyError:
                        return
                    except discord.errors.HTTPException:
                        return
            except KeyError:
                return
            except discord.errors.HTTPException:
                return

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        """Message Log"""
        nachrichten = []
        nutzer = []
        async with aiohttp.ClientSession() as session:
            try:
                webhook = Webhook.from_url(get_messageloggingchannel(self, messages[0]), session=session)
                webhook = await Webhook.fetch(webhook, prefer_auth=True)
                if messages[0].guild.id == webhook.guild_id:
                    try:

                        embed1 = discord.Embed(title=f"{len(messages)} Nachrichten gelöscht",
                                               description=f">>> **Kanal**: [{messages[0].channel}]({messages[0].channel.jump_url}) ({messages[0].channel.mention})\n",
                                               color=color_red)
                        async for entry in messages[0].guild.audit_logs(limit=1, action=discord.AuditLogAction.message_bulk_delete):
                            if entry.user.id:
                                embed1.set_footer(text=f"Moderator: {entry.user}", icon_url=entry.user.display_avatar.url)
                        for m in messages:
                            nachrichten.append(f"[{m.created_at.strftime('%H:%M:%S')}] {m.author} ({m.author.id}) | {m.id}: {m.content}")
                            if m.author.mention not in nutzer:
                                nutzer.append(m.author.mention)
                        liste = "\n".join(nachrichten)
                        datei = discord.File(io.StringIO(str(liste)), filename=f"nachricht.txt")
                        pings = ", ".join(nutzer)
                        embed1.add_field(name=f"**Nutzer**", value=f"{pings}", inline=False)
                        await webhook.send(embed=embed1, file=datei)
                    except KeyError:
                        return
                    except discord.errors.HTTPException:
                        return
            except KeyError:
                return
            except discord.errors.HTTPException:
                return

    @commands.Cog.listener()
    async def on_member_join(self, nutzer):
        """Join Log"""
        async with aiohttp.ClientSession() as session:
            try:
                webhook = Webhook.from_url(get_serverloggingchannel(self, nutzer), session=session)
                webhook = await Webhook.fetch(webhook, prefer_auth=True)
                if nutzer.guild.id == webhook.guild_id:
                    try:
                        embed1 = discord.Embed(title="Nutzer beigetreten" if not nutzer.bot else "Bot hinzugefügt",
                                               description=f">>> **Nutzer**: [{nutzer}](https://discord.com/users/{nutzer.id}) ({nutzer.mention})\n"
                                                           f"**Aktuelle Mitglieder**: {nutzer.guild.member_count}\n"
                                                           f"**Accounterstellung**: <t:{int(nutzer.created_at.timestamp())}:d> - <t:{int(nutzer.created_at.timestamp())}:t> (<t:{int(nutzer.created_at.timestamp())}:R>)",
                                               color=color_green)
                        embed1.set_thumbnail(url=nutzer.display_avatar.url)
                        await webhook.send(embed=embed1)
                    except KeyError:
                        return
            except KeyError:
                return
            except discord.errors.HTTPException:
                return

    @commands.Cog.listener()
    async def on_member_remove(self, nutzer):
        """Leave Log"""
        async with aiohttp.ClientSession() as session:
            try:
                webhook = Webhook.from_url(get_serverloggingchannel(self, nutzer), session=session)
                webhook = await Webhook.fetch(webhook, prefer_auth=True)
                if nutzer.guild.id == webhook.guild_id:
                    try:
                        embed1 = discord.Embed(title="Nutzer verlassen" if not nutzer.bot else "Bot entfernt",
                                               description=f">>> **Nutzer**: [{nutzer}](https://discord.com/users/{nutzer.id}) ({nutzer.mention})\n"
                                                           f"**Aktuelle Mitglieder**: {nutzer.guild.member_count}\n"
                                                           f"**Serverbeitritt**: <t:{int(nutzer.joined_at.timestamp())}:d> - <t:{int(nutzer.joined_at.timestamp())}:t> (<t:{int(nutzer.joined_at.timestamp())}:R>)",
                                               color=color_red)
                        if len(nutzer.roles) > 1:
                            role_string = ", ".join([r.mention for r in nutzer.roles][1:])
                            embed1.add_field(name=f"**Rollen [{len(nutzer.roles) - 1}]**",
                                             value=role_string,
                                             inline=False)
                        embed1.set_thumbnail(url=nutzer.display_avatar.url)
                        await webhook.send(embed=embed1)
                    except KeyError:
                        return
            except KeyError:
                return
            except discord.errors.HTTPException:
                return

    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry: discord.AuditLogEntry):
        """Kick Log"""
        if entry.action is discord.AuditLogAction.kick:
            async with aiohttp.ClientSession() as session:
                try:
                    webhook = Webhook.from_url(get_modlogging(self, entry.guild), session=session)
                    webhook = await Webhook.fetch(webhook, prefer_auth=True)
                    if entry.guild.id == webhook.guild_id:
                        try:
                            if entry.reason is None:
                                entry.reason = "Es wurde kein Grund angegeben"
                            embed = discord.Embed(title="Nutzer gekickt", color=color_red)
                            embed.description = f">>> **Nutzer**: [{entry.target}](https://discord.com/users/{entry.target.id}) ({entry.target.mention})\n" \
                                                f"**Accounterstellung**: <t:{int(entry.target.created_at.timestamp())}:d> - <t:{int(entry.target.created_at.timestamp())}:t> (<t:{int(entry.target.created_at.timestamp())}:R>)"
                            embed.add_field(name="**Grund**",
                                            value=f"```{entry.reason}```",
                                            inline=False)
                            embed.set_footer(text=f"Moderator: {entry.user}", icon_url=entry.user.display_avatar.url)
                            embed.set_thumbnail(url=entry.target.display_avatar.url)
                            if "BannSystem" not in entry.reason:
                                await webhook.send(embed=embed)
                        except KeyError:
                            pass
                        except discord.errors.NotFound:
                            pass
                        except discord.errors.HTTPException:
                            pass
                except KeyError:
                    return
                except discord.errors.HTTPException:
                    return

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, nutzer: (Union[discord.User, discord.Member])):
        """Ban Log"""
        async with aiohttp.ClientSession() as session:
            try:
                webhook = Webhook.from_url(get_modlogging(self, guild), session=session)
                webhook = await Webhook.fetch(webhook, prefer_auth=True)
                if guild.id == webhook.guild_id:
                    try:
                        ban = await guild.fetch_ban(nutzer)
                        embed = discord.Embed(title="Nutzer gebannt", color=color_red)
                        if nutzer is discord.Member:
                            embed.description = f">>> **Nutzer**: [{nutzer}](https://discord.com/users/{nutzer.id}) ({nutzer.mention})\n" \
                                                f"**Serverbeitritt**: <t:{int(nutzer.joined_at.timestamp())}:d> - <t:{int(nutzer.joined_at.timestamp())}:t> (<t:{int(nutzer.joined_at.timestamp())}:R>)\n" \
                                                f"**Accounterstellung**: <t:{int(nutzer.created_at.timestamp())}:d> - <t:{int(nutzer.created_at.timestamp())}:t> (<t:{int(nutzer.created_at.timestamp())}:R>)"
                        else:
                            embed.description = f">>> **Nutzer**: [{nutzer}](https://discord.com/users/{nutzer.id}) ({nutzer.mention})\n" \
                                                f"**Accounterstellung**: <t:{int(nutzer.created_at.timestamp())}:d> - <t:{int(nutzer.created_at.timestamp())}:t> (<t:{int(nutzer.created_at.timestamp())}:R>)"
                        embed.add_field(name="**Grund**",
                                        value=f"```{ban.reason if not None else 'Es wurde kein Grund angegeben'}```",
                                        inline=False)
                        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
                            if entry.user.id != nutzer.id:
                                embed.set_footer(text=f"Moderator: {entry.user}", icon_url=entry.user.display_avatar.url)
                        embed.set_thumbnail(url=nutzer.display_avatar.url)
                        if "BannSystem" not in ban.reason:
                            await webhook.send(embed=embed)
                    except KeyError:
                        pass
                    except discord.errors.NotFound:
                        pass
                    except discord.errors.HTTPException:
                        pass
            except KeyError:
                return
            except discord.errors.HTTPException:
                return

    @commands.Cog.listener()
    async def on_member_unban(self, guild, nutzer: (Union[discord.User, discord.Member])):
        """Ban Log"""
        async with aiohttp.ClientSession() as session:
            try:
                webhook = Webhook.from_url(get_modlogging(self, guild), session=session)
                webhook = await Webhook.fetch(webhook, prefer_auth=True)
                if guild.id == webhook.guild_id:
                    try:
                        embed = discord.Embed(title="Nutzer entbannt",
                                              description=f">>> **Nutzer**: [{nutzer}](https://discord.com/users/{nutzer.id}) ({nutzer.mention})\n" \
                                                          f"**Accounterstellung**: <t:{int(nutzer.created_at.timestamp())}:d> - <t:{int(nutzer.created_at.timestamp())}:t> (<t:{int(nutzer.created_at.timestamp())}:R>)",
                                              color=color_green)
                        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban):
                            if entry.reason is not None:
                                embed.add_field(name="**Grund**",
                                                value=f"```{entry.reason}```")
                            if entry.user.id != nutzer.id:
                                embed.set_footer(text=f"Moderator: {entry.user}", icon_url=entry.user.display_avatar.url)
                        embed.set_thumbnail(url=nutzer.display_avatar.url)
                        await webhook.send(embed=embed)
                    except KeyError:
                        pass
                    except discord.errors.HTTPException:
                        pass
                    except discord.errors.NotFound:
                        pass
            except KeyError:
                return
            except discord.errors.HTTPException:
                return

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        try:
            role = discord.utils.get(before.guild.roles, id=get_joinrole(self, before))
            member = self.bot.get_guild(before.guild.id).get_member(before.id)
            if before.bot or after.bot:
                return
            else:
                if before.pending is True and after.pending is False:
                    try:
                        await member.add_roles(role, atomic=True)
                    except:
                        return
        except KeyError:
            pass
        async with aiohttp.ClientSession() as session:
            try:
                webhook = Webhook.from_url(get_memberlogging(self, before), session=session)
                webhook = await Webhook.fetch(webhook, prefer_auth=True)
                if before.guild.id == webhook.guild_id:
                    if before.nick != after.nick:
                        try:
                            embed1 = discord.Embed(title=f"**Nutzernickname geändert**", color=color_orange)

                            async for entry in after.guild.audit_logs(limit=1,
                                                                      action=discord.AuditLogAction.member_update):
                                if entry.reason:
                                    embed1.description = f">>> **Nutzer**: [{before}](https://discord.com/users/{before.id}) ({before.mention})\n**Grund**: {entry.reason}"
                                else:
                                    embed1.description = f">>> **Nutzer**: [{before}](https://discord.com/users/{before.id}) ({before.mention})"
                                if entry.user.id != before.id:
                                    embed1.set_footer(text=f"Moderator: {entry.user}", icon_url=entry.user.display_avatar.url)
                            embed1.add_field(name="**Vorher**", value=f"```{before.nick}```")
                            embed1.add_field(name="**Nachher**", value=f"```{after.nick}```")
                            embed1.set_thumbnail(url=before.display_avatar.url)
                            await webhook.send(embed=embed1)
                        except KeyError:
                            pass
                        except discord.errors.NotFound:
                            pass
                        except discord.HTTPException:
                            pass

                if before.roles != after.roles:
                    try:

                        added_String = []
                        removed_String = []

                        embed1 = discord.Embed()
                        async for entry in after.guild.audit_logs(limit=1,
                                                                  action=discord.AuditLogAction.member_role_update):
                            if entry.reason:
                                embed1.description = f">>> **Nutzer**: [{before}](https://discord.com/users/{before.id}) ({before.mention})\n**Grund**: {entry.reason}"
                            else:
                                embed1.description = f">>> **Nutzer**: [{before}](https://discord.com/users/{before.id}) ({before.mention})"
                            try:
                                embed1.set_footer(text=f"Moderator: {entry.user}", icon_url=entry.user.display_avatar.url)
                            except AttributeError:
                                pass

                        for before1 in before.roles:
                            if before1 not in after.roles:
                                removed_String.append(before1.mention)

                        for after1 in after.roles:
                            if after1 not in before.roles:
                                added_String.append(after1.mention)

                        added_role_string = ", ".join([str(r) for r in added_String])
                        removed_role_string = ", ".join([str(r) for r in removed_String])

                        if added_String:
                            embed1.add_field(name="**Hinzugefügt**", value=added_role_string)
                        if removed_String:
                            embed1.add_field(name="**Entfernt**", value=removed_role_string)

                        if not added_String:
                            embed1.title = f"**Nutzerrollen entfernt**"
                            embed1.color = color_red

                        if not removed_String:
                            embed1.title = f"**Nutzerrollen hinzugefügt**"
                            embed1.color = color_green

                        if added_String and removed_String:
                            embed1.title = f"**Nutzerrollen geändert**"
                            embed1.color = color_orange

                        embed1.set_thumbnail(url=before.display_avatar.url)
                        await webhook.send(embed=embed1)
                    except KeyError:
                        pass
                    except discord.errors.NotFound:
                        pass
                    except discord.HTTPException:
                        pass
            except KeyError:
                return
            except discord.errors.HTTPException:
                return

    @commands.Cog.listener()
    async def on_voice_state_update(self, nutzer: discord.Member, before, after):
        try:
            if before.channel is None:
                async with aiohttp.ClientSession() as session:
                    webhook = Webhook.from_url(get_voicelogging(self, after), session=session)
                    webhook = await self.bot.fetch_webhook(webhook.id)
            else:
                async with aiohttp.ClientSession() as session:
                    webhook = Webhook.from_url(get_voicelogging(self, before), session=session)
                    webhook = await self.bot.fetch_webhook(webhook.id)

            if nutzer.guild == webhook.guild:
                if before.channel is None and after.channel is not None:
                    try:
                        async with aiohttp.ClientSession() as session:
                            webhook = Webhook.from_url(get_voicelogging(self, after), session=session)
                            embed1 = discord.Embed(title=f"**Sprachkanal beigetreten**",
                                                   description=f">>> **Nutzer**: [{nutzer}](https://discord.com/users/{nutzer.id}) ({nutzer.mention})\n"
                                                               f"**Kanal**: [{after.channel.name}]({after.channel.jump_url}) ({after.channel.mention})",
                                                   color=color_green)
                            embed1.set_thumbnail(url=nutzer.display_avatar.url)
                            await webhook.send(embed=embed1)
                    except KeyError:
                        pass
                    except discord.errors.NotFound:
                        pass
                    except discord.HTTPException:
                        pass

                elif before.channel is not None and after.channel is not None and before.channel != after.channel:
                    try:
                        async with aiohttp.ClientSession() as session:
                            webhook = Webhook.from_url(get_voicelogging(self, before), session=session)
                            embed1 = discord.Embed(title=f"**Sprachkanal gewechselt**",
                                                   description=f">>> **Nutzer**: [{nutzer}](https://discord.com/users/{nutzer.id}) ({nutzer.mention})\n"
                                                               f"**Vorher**: {before.channel.name} ({before.channel.mention})\n"
                                                               f"**Nachher**: [{after.channel.name}]({after.channel.jump_url}) ({after.channel.mention})",
                                                   color=color_orange)
                            embed1.set_thumbnail(url=nutzer.display_avatar.url)
                            await webhook.send(embed=embed1)
                    except KeyError:
                        pass
                    except discord.errors.NotFound:
                        pass
                    except discord.HTTPException:
                        pass

                elif before.channel is not None and after.channel is None:
                    try:
                        async with aiohttp.ClientSession() as session:
                            webhook = Webhook.from_url(get_voicelogging(self, before), session=session)
                            embed1 = discord.Embed(title=f"**Sprachkanal verlassen**",
                                                   description=f">>> **Nutzer**: [{nutzer}](https://discord.com/users/{nutzer.id}) ({nutzer.mention})\n"
                                                               f"**Kanal**: [{before.channel.name}]({before.channel.jump_url}) ({before.channel.mention})",
                                                   color=color_red)
                            embed1.set_thumbnail(url=nutzer.display_avatar.url)
                            await webhook.send(embed=embed1)
                    except KeyError:
                        pass
                    except discord.errors.NotFound:
                        pass
                    except discord.HTTPException:
                        pass

                elif before.self_mute is False and after.self_mute is True:
                    try:
                        async with aiohttp.ClientSession() as session:
                            webhook = Webhook.from_url(get_voicelogging(self, before), session=session)
                            embed1 = discord.Embed(title=f"**Nutzer Mikrofon stummgeschalten**",
                                                   description=f">>> **Nutzer**: [{nutzer}](https://discord.com/users/{nutzer.id}) ({nutzer.mention})\n"
                                                               f"**Kanal**: [{after.channel.name}]({after.channel.jump_url}) ({after.channel.mention})",
                                                   color=color_red)
                            embed1.set_thumbnail(url=nutzer.display_avatar.url)
                            await webhook.send(embed=embed1)
                    except KeyError:
                        pass
                    except discord.errors.NotFound:
                        pass
                    except discord.HTTPException:
                        pass
                elif before.self_mute is True and after.self_mute is False:
                    try:
                        async with aiohttp.ClientSession() as session:
                            webhook = Webhook.from_url(get_voicelogging(self, before), session=session)
                            embed1 = discord.Embed(title=f"**Nutzer Mikrofon stummschaltung aufgehoben**",
                                                   description=f">>> **Nutzer**: [{nutzer}](https://discord.com/users/{nutzer.id}) ({nutzer.mention})\n"
                                                               f"**Kanal**: [{after.channel.name}]({after.channel.jump_url}) ({after.channel.mention})",
                                                   color=color_green)
                            embed1.set_thumbnail(url=nutzer.display_avatar.url)
                            await webhook.send(embed=embed1)
                    except KeyError:
                        pass
                    except discord.errors.NotFound:
                        pass
                    except discord.HTTPException:
                        pass

                elif before.self_deaf is False and after.self_deaf is True:
                    try:
                        async with aiohttp.ClientSession() as session:
                            webhook = Webhook.from_url(get_voicelogging(self, before), session=session)
                            embed1 = discord.Embed(title=f"**Nutzer Sound stummgeschalten**",
                                                   description=f">>> **Nutzer**: [{nutzer}](https://discord.com/users/{nutzer.id}) ({nutzer.mention})\n"
                                                               f"**Kanal**: [{after.channel.name}]({after.channel.jump_url}) ({after.channel.mention})",
                                                   color=color_red)
                            embed1.set_thumbnail(url=nutzer.display_avatar.url)
                            await webhook.send(embed=embed1)
                    except KeyError:
                        pass
                    except discord.errors.NotFound:
                        pass
                    except discord.HTTPException:
                        pass
                elif before.self_deaf is True and after.self_deaf is False:
                    try:
                        async with aiohttp.ClientSession() as session:
                            webhook = Webhook.from_url(get_voicelogging(self, before), session=session)
                            embed1 = discord.Embed(title=f"**Nutzer Sound stummschaltung aufgehoben**",
                                                   description=f">>> **Nutzer**: [{nutzer}](https://discord.com/users/{nutzer.id}) ({nutzer.mention})\n"
                                                               f"**Kanal**: [{after.channel.name}]({after.channel.jump_url}) ({after.channel.mention})",
                                                   color=color_green)
                            embed1.set_thumbnail(url=nutzer.display_avatar.url)
                            await webhook.send(embed=embed1)
                    except KeyError:
                        pass
                    except discord.errors.NotFound:
                        pass
                    except discord.HTTPException:
                        pass

                elif before.mute is False and after.mute is True:
                    try:
                        async with aiohttp.ClientSession() as session:
                            webhook = Webhook.from_url(get_voicelogging(self, before), session=session)
                            embed1 = discord.Embed(title=f"**Serverweit Mikrofon stummgeschalten**",
                                                   description=f">>> **Nutzer**: [{nutzer}](https://discord.com/users/{nutzer.id}) ({nutzer.mention})\n"
                                                               f"**Kanal**: [{after.channel.name}]({after.channel.jump_url}) ({after.channel.mention})",
                                                   color=color_green)
                            embed1.set_thumbnail(url=nutzer.display_avatar.url)
                            await webhook.send(embed=embed1)
                    except KeyError:
                        pass
                    except discord.errors.NotFound:
                        pass
                    except discord.HTTPException:
                        pass
                elif before.mute is True and after.mute is False:
                    try:
                        async with aiohttp.ClientSession() as session:
                            webhook = Webhook.from_url(get_voicelogging(self, before), session=session)
                            embed1 = discord.Embed(title=f"**Serverweite Mikrofon stummschaltung aufgehoben**",
                                                   description=f">>> **Nutzer**: [{nutzer}](https://discord.com/users/{nutzer.id}) ({nutzer.mention})\n"
                                                               f"**Kanal**: [{after.channel.name}]({after.channel.jump_url}) ({after.channel.mention})",
                                                   color=color_red)
                            embed1.set_thumbnail(url=nutzer.display_avatar.url)
                            await webhook.send(embed=embed1)
                    except KeyError:
                        pass
                    except discord.errors.NotFound:
                        pass
                    except discord.HTTPException:
                        pass

                elif before.deaf is False and after.deaf is True:
                    try:
                        async with aiohttp.ClientSession() as session:
                            webhook = Webhook.from_url(get_voicelogging(self, before), session=session)
                            embed1 = discord.Embed(title=f"**Serverweit Nutzer Sound stummgeschalten**",
                                                   description=f">>> **Nutzer**: [{nutzer}](https://discord.com/users/{nutzer.id}) ({nutzer.mention})\n"
                                                               f"**Kanal**: [{after.channel.name}]({after.channel.jump_url}) ({after.channel.mention})",
                                                   color=color_green)
                            embed1.set_thumbnail(url=nutzer.display_avatar.url)
                            await webhook.send(embed=embed1)
                    except KeyError:
                        pass
                    except discord.errors.NotFound:
                        pass
                    except discord.HTTPException:
                        pass
                elif before.deaf is True and after.deaf is False:
                    try:
                        async with aiohttp.ClientSession() as session:
                            webhook = Webhook.from_url(get_voicelogging(self, before), session=session)
                            embed1 = discord.Embed(title=f"**Serverweite Sound stummschaltung aufgehoben**",
                                                   description=f">>> **Nutzer**: [{nutzer}](https://discord.com/users/{nutzer.id}) ({nutzer.mention})\n"
                                                               f"**Kanal**: [{after.channel.name}]({after.channel.jump_url}) ({after.channel.mention})",
                                                   color=color_red)
                            embed1.set_thumbnail(url=nutzer.display_avatar.url)
                            await webhook.send(embed=embed1)
                    except KeyError:
                        pass
                    except discord.errors.NotFound:
                        pass
                    except discord.HTTPException:
                        pass

                elif before.self_stream is False and after.self_stream is True:
                    try:
                        async with aiohttp.ClientSession() as session:
                            webhook = Webhook.from_url(get_voicelogging(self, before), session=session)
                            embed1 = discord.Embed(title=f"**Bildschirmübertragung gestartet**",
                                                   description=f">>> **Nutzer**: [{nutzer}](https://discord.com/users/{nutzer.id}) ({nutzer.mention})\n"
                                                               f"**Kanal**: [{after.channel.name}]({after.channel.jump_url}) ({after.channel.mention})",
                                                   color=color_green)
                            embed1.set_thumbnail(url=nutzer.display_avatar.url)
                            await webhook.send(embed=embed1)
                    except KeyError:
                        pass
                    except discord.errors.NotFound:
                        pass
                    except discord.HTTPException:
                        pass
                elif before.self_stream is True and after.self_stream is False:
                    try:
                        async with aiohttp.ClientSession() as session:
                            webhook = Webhook.from_url(get_voicelogging(self, before), session=session)
                            embed1 = discord.Embed(title=f"**Bildschirmübertragung beendet**",
                                                   description=f">>> **Nutzer**: [{nutzer}](https://discord.com/users/{nutzer.id}) ({nutzer.mention})\n"
                                                               f"**Kanal**: [{after.channel.name}]({after.channel.jump_url}) ({after.channel.mention})",
                                                   color=color_red)
                            embed1.set_thumbnail(url=nutzer.display_avatar.url)
                            await webhook.send(embed=embed1)
                    except KeyError:
                        pass
                    except discord.errors.NotFound:
                        pass
                    except discord.HTTPException:
                        pass

                elif before.self_video is False and after.self_video is True:
                    try:
                        async with aiohttp.ClientSession() as session:
                            webhook = Webhook.from_url(get_voicelogging(self, before), session=session)
                            embed1 = discord.Embed(title=f"**Kameraübertragung gestartet**",
                                                   description=f">>> **Nutzer**: [{nutzer}](https://discord.com/users/{nutzer.id}) ({nutzer.mention})\n"
                                                               f"**Kanal**: [{after.channel.name}]({after.channel.jump_url}) ({after.channel.mention})",
                                                   color=color_green)
                            embed1.set_thumbnail(url=nutzer.display_avatar.url)
                            await webhook.send(embed=embed1)
                    except KeyError:
                        pass
                    except discord.errors.NotFound:
                        pass
                    except discord.HTTPException:
                        pass
                elif before.self_video is True and after.self_video is False:
                    try:
                        async with aiohttp.ClientSession() as session:
                            webhook = Webhook.from_url(get_voicelogging(self, before), session=session)
                            embed1 = discord.Embed(title=f"**Kameraübertragung beendet**",
                                                   description=f">>> **Nutzer**: [{nutzer}](https://discord.com/users/{nutzer.id}) ({nutzer.mention})\n"
                                                               f"**Kanal**: [{after.channel.name}]({after.channel.jump_url}) ({after.channel.mention})",
                                                   color=color_red)
                            embed1.set_thumbnail(url=nutzer.display_avatar.url)
                            await webhook.send(embed=embed1)
                    except KeyError:
                        pass
                    except discord.errors.NotFound:
                        pass
                    except discord.HTTPException:
                        pass
        except KeyError:
            pass
        except discord.errors.NotFound:
            pass
        except discord.HTTPException:
            pass

async def setup(bot: commands.Bot):
    await bot.add_cog(Log(bot))  # , guilds=[discord.Object(id=756526359521656951)])