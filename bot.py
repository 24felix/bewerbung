import sys
import discord
import time
import aiohttp
from discord import Webhook
from discord.ext import commands
from discord import app_commands
from Utils.formatting import *
from plugins.ticketing import Support, Report, SuR, Message, Close
from plugins.features import Suggester
from plugins.dreamland import Farben
from discord.gateway import DiscordWebSocket, _log

cogs = [
    "plugins.development",
    "plugins.errors",
    "plugins.configuration",
    "plugins.logging",
    "plugins.administration",
    "plugins.mass_commands",
    "plugins.moderation",
    "plugins.information",
    "plugins.ticketing",
    "plugins.features"
]

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class Legolas(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("&"),
            case_insensitive=True,
            max_messages=10000,
            allowed_mentions=discord.AllowedMentions(users=True, roles=True, everyone=True),
            intents=intents,
            help_command=None,
            owner_ids=[252364399669542913, 308320665403129866],
            status=discord.Status.idle,
            activity=discord.Activity(type=discord.ActivityType.watching, name="Stranger Things"),
            chunk_guilds_at_startup=False
        )

    async def setup_hook(self):
        self.add_view(Support())
        self.add_view(Report())
        self.add_view(SuR())
        self.add_view(Message())
        self.add_view(Close())
        self.add_view(Suggester())
        self.add_view(Farben())

    startzeit = time.time()
    async def on_ready(self):
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"Das Modul {cog} wurde erfolgreich geladen")
            except commands.ExtensionAlreadyLoaded:
                await self.reload_extension(cog)
        await self.tree.sync()
        if not self.get_guild(252365383258996736).chunked:
            await self.get_guild(252365383258996736).chunk(cache=True)
        await self.change_presence(status=discord.Status.online,
                                   activity=discord.Activity(type=discord.ActivityType.listening, name="Spotify"))
        async with aiohttp.ClientSession() as session:
            nachricht = icon_accept + f" **{self.user}** wurde gestartet!"
            log = "WEBHOOK LINK"
            webhook = Webhook.from_url(log, session=session)
            await webhook.send(content=nachricht, username=self.user.name, avatar_url=self.user.display_avatar.url)
        print(f"{self.user} wurde erfolgreich gestartet!\n")

Legolas().run("TOKEN")