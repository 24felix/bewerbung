import discord
import requests
import discord.errors
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from Utils.formatting import *

class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    dev = app_commands.Group(name="development", description="Entwicklerbefehle")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        join = self.bot.get_channel(816274360318033930)
        if not guild.chunked:
            await guild.chunk(cache=True)
        embed1 = discord.Embed(title="**Server beigetreten**",
                               color=color_green)
        if guild.description:
            embed1.description = f"> {guild.description}"
        embed1.add_field(name=f"**Server**",
                         value=f"{guild}\n"
                               f"`{guild.id}`")
        embed1.add_field(name="**Inhaber**",
                         value=f"{guild.owner}\n"
                               f"`{guild.owner_id}`")
        embed1.add_field(name="**Mitglieder**",
                         value=f"Nutzer: {len([m for m in guild.members if not m.bot])}\nBots: {len([m for m in guild.members if m.bot])}")
        if guild.features:
            embed1.add_field(name='**Funktionen**',
                             value=f"```{', '.join([str(f) for f in guild.features])}```")
        embed1.set_thumbnail(url=guild.icon.url)
        await join.send(embed=embed1)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        leave = self.bot.get_channel(816274360318033930)
        if not guild.chunked:
            try:
                await guild.chunk(cache=True)
            except:
                pass
        embed1 = discord.Embed(title="**Server verlassen**",
                               color=color_red)
        if guild.description:
            embed1.description = f"> {guild.description}"
        embed1.add_field(name=f"**Server**",
                         value=f"{guild}\n"
                               f"`{guild.id}`")
        embed1.add_field(name="**Inhaber**",
                         value=f"{guild.owner}\n"
                               f"`{guild.owner_id}`")
        embed1.add_field(name="**Mitglieder**",
                         value=f"Nutzer: {len([m for m in guild.members if not m.bot])}\nBots: {len([m for m in guild.members if m.bot])}")
        if guild.features:
            embed1.add_field(name='**Funktionen**',
                             value=f"```{', '.join([str(f) for f in guild.features])}```")
        embed1.set_thumbnail(url=guild.icon.url)
        await leave.send(embed=embed1)

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.guild is None and not message.author.bot:
                log = self.bot.get_channel(816274293884583966)
                await log.send(content=f"**{message.author}** (`{message.author.id}`): {message.content}", allowed_mentions=False)
        except:
            return

    @commands.command()
    @commands.is_owner()
    async def dm(self, ctx, nutzer: discord.User, *, nachricht: str):
        async with ctx.channel.typing():
            await nutzer.send(content=nachricht)
            await ctx.message.add_reaction(icon_accept)

    @commands.command()
    @commands.is_owner()
    async def unbanall(self, ctx, *, grund: str):
        zahl = 0
        async with ctx.channel.typing():
            async for entry in ctx.guild.bans(limit=None):
                try:
                    if grund in entry.reason:
                        try:
                            await ctx.guild.unban(entry.user, reason=f"von {ctx.author} entbannt")
                            zahl += 1
                            await ctx.send(content=f"{zahl}. **{entry.user}** (`{entry.user.id}`) | {entry.reason}")
                        except discord.HTTPException:
                            pass
                except TypeError:
                    pass
        await ctx.reply(content=f"{icon_accept} Alle **{zahl} Nutzer** mit dem Grund `{grund}` wurden entbannt!")

    @commands.command()
    @commands.is_owner()
    async def bancount(self, ctx, *, grund: str):
        anzahl = 0
        total = 0
        async with ctx.channel.typing():
            async for entry in ctx.guild.bans(limit=None):
                total += 1
                try:
                    if grund in entry.reason:
                        anzahl += 1
                except TypeError:
                    pass
            await ctx.reply(content=f"Es sind **{anzahl} / {total} Nutzer** mit dem Grund `{grund}` gebannt!")

    @commands.group(aliases=["f"], description="Verwalte die Cogs", invoke_without_command=True)
    @commands.is_owner()
    async def file(self, ctx):
        async with ctx.channel.typing():
            nachricht = (f"```{ctx.prefix}file avatar\n" \
                         f"{ctx.prefix}file load <Datei>\n" \
                         f"{ctx.prefix}file reload <Datei>\n" \
                         f"{ctx.prefix}file unload <Datei>\n" \
                         f"{ctx.prefix}file commands```")
            await ctx.reply(content=nachricht)

    @file.command(name="avatar", aliases=["a"], description="Lade den Avatar neu")
    @commands.is_owner()
    async def reloadavatar(self, ctx):
        async with ctx.channel.typing():
            with open("Legolas/plugins/img.gif", 'rb') as image:
                await self.bot.user.edit(avatar=requests.get(image).content)
            await ctx.send(f"{icon_accept} Der Avatar wurde neu geladen!")

    @file.command(name="commands", aliases=["c"], description="Lade alle Befehle neu")
    @commands.is_owner()
    async def reloadcommands(self, ctx):
        async with ctx.channel.typing():
            await self.bot.tree.sync()
            print(f"Alle Befehle wurden von {ctx.author} geladen")
            await ctx.reply(content=f"{icon_accept} Alle Befehle wurden neu geladen!")

    @file.command(name="load", aliases=["l"], description="Lade eine Datei")
    @commands.is_owner()
    async def load(self, ctx, datei: str):
        async with ctx.channel.typing():
            await self.bot.load_extension(f"plugins.{datei}")
            print(f"Das Modul {datei} wurde von {ctx.author} geladen")
            await ctx.reply(content=f"{icon_accept} Die Datei **{datei}** wurde geladen!")

    @file.command(name="reload", aliases=["r"], description="Lade eine Datei neu")
    @commands.is_owner()
    async def reload(self, ctx, datei: str):
        async with ctx.channel.typing():
            await self.bot.reload_extension(f"plugins.{datei}")
            print(f"Das Modul {datei} wurde von {ctx.author} neugeladen")
            await ctx.reply(content=f"{icon_accept} Die Datei **{datei}** wurde neu geladen!")

    @file.command(name="unload", aliases=["u"], description="Stoppe eine Datei")
    @commands.is_owner()
    async def unload(self, ctx, datei: str):
        async with ctx.channel.typing():
            await self.bot.unload_extension(f"plugins.{datei}")
            print(f"Das Modul {datei} wurde von {ctx.author} gestoppt")
            await ctx.reply(content=f"{icon_accept} Die Datei **{datei}** wurde gestoppt!")


    @dev.command(name="status", description="Verändere den Aktivitätsstatus")
    @app_commands.describe(status="Welcher Aktivitätsstatus soll gesetzt werden?", spiel="Welche Spieleaktivität soll gesetzt werden?", text="Welcher Text soll gesetzt werden?")
    @app_commands.choices(status=[Choice(name="online", value=1),
                                  Choice(name="abwesend", value=2),
                                  Choice(name="nicht stören", value=3),
                                  Choice(name="offline", value=4)],
                          spiel=[Choice(name="spielen", value=1),
                                 Choice(name="sehen", value=2),
                                 Choice(name="hören", value=3)])
    @app_commands.checks.has_role(950756376135737374)
    async def status(self, interaction: discord.Interaction, status: Choice[int], spiel: Choice[int], text: str = None):
        if text is None:
            text = "Spotify"
        laden = f"{icon_loading} Der Status wird geändert. . ."
        erfolgreich = f"{icon_accept} Der Status wurde erfolgreich geändert!\n" \
                      f"`>` Status: `{status.name}`\n" \
                      f"`>` Aktivität: `{spiel.name}`\n" \
                      f"`>` Text: `{text}`"
        erfolgreichp = f"{self.bot.name} Status wurde von {interaction.user} geändert | {status.name}: {spiel.name} {text}"
        if spiel.value == 1:
            spiel = discord.ActivityType.playing
        if spiel.value == 2:
            spiel = discord.ActivityType.watching
        if spiel.value == 3:
            spiel = discord.ActivityType.listening
        if status.value == 1:
            status = discord.Status.online
        if status.value == 2:
            status = discord.Status.idle
        if status.value == 3:
            status = discord.Status.do_not_disturb
        if status.value == 4:
            status = discord.Status.invisible
        await interaction.response.send_message(content=laden, ephemeral=True)
        await self.bot.change_presence(status=status, activity=discord.Activity(type=spiel, name=text))
        await interaction.edit_original_response(content=erfolgreich)
        print(erfolgreichp)


    @commands.group(name="server", aliases=["s"], description="Verwalte die Cogs", invoke_without_command=True)
    @commands.is_owner()
    async def server(self, ctx):
        async with ctx.channel.typing():
            nachricht = f"```{ctx.prefix}server list\n" \
                        f"{ctx.prefix}server invite <ServerID>\n" \
                        f"{ctx.prefix}server leave <ServerID>\n```"
            await ctx.reply(content=nachricht)

    @server.command(name="list", aliases=["a"], description="Lade alle Befehle neu")
    @commands.is_owner()
    async def list(self, ctx):
        async with ctx.channel.typing():
            for guild in self.bot.guilds:
                server = discord.Embed(colour=color_gray)
                server.add_field(name="**Inhaber**",
                                 value=f"{guild.owner}\n"
                                       f"`{guild.owner.id}`")
                server.add_field(name="**Server**",
                                 value=f"{guild.name}\n"
                                       f"`{guild.id}`")
                server.add_field(name="**Mitglieder**",
                                 value=f"Nutzer: `{len([m for m in guild.members])}`\n"
                                       f"Davon Bots: `{len([m for m in guild.members if m.bot])}`")
                server.set_thumbnail(url=guild.icon.url)
                await ctx.channel.send(embed=server)

    @server.command(name="invite", aliases=["i"], description="Erstelle eine Einladung")
    @commands.is_owner()
    async def invite(self, ctx, server: str):
        async with ctx.channel.typing():
            try:
                server = self.bot.get_guild(int(server))
                invite = await server.text_channels[0].create_invite(max_age=0, max_uses=0, reason="Einladungslink für die Entwickler")
                await ctx.reply(content=f"{icon_accept} Einladung für **{server}** erstellt: {invite}", mention_author=False)
            except discord.Forbidden:
                await ctx.reply(content=f"{icon_denied} Keine Berechtigung, einen Einladungslink für **{server}** zu erstellen!", mention_author=False)
            except:
                await ctx.reply(content=f"{icon_denied} Ich bin nicht auf diesem Server vertreten!", mention_author=False)

    @server.command(name="leave", aliases=["l"], description="Erstelle eine Einladung")
    @commands.is_owner()
    async def leave(self, ctx, server: str):
        async with ctx.channel.typing():
            server = self.bot.get_guild(int(server))
            try:
                await server.leave()
                await ctx.reply(content=f"{icon_accept} Der Server **{server}** wurde erfolgreich verlassen!")
            except discord.ext.commands.GuildNotFound:
                await ctx.reply(content=f"{icon_denied} Der Server **{server}** konnte nicht gefunden werden!")
            except discord.HTTPException:
                await ctx.reply(content=f"{icon_denied} Der Server **{server}** konnte nicht verlassen werden!")

async def setup(bot: commands.Bot):
    await bot.add_cog(Dev(bot), guild=discord.Object(id=252365383258996736))