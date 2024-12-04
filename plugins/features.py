import json
import aiohttp
import discord
import discord.errors
from discord import app_commands, ui
from discord.ext import commands
from Utils import welcome_variables
from Utils.formatting import *
from discord.ext.commands import bot_has_permissions


def get_suggest(client, ctx):
    with open('Legolas/datenbank/suggestlogging.json', 'r') as f:
        banmsg = json.load(f)
        return banmsg[str(ctx.guild.id)]

def get_pingrole(client, message):
    with open("Legolas/datenbank/suggestping.json", "r") as c:
        pingrole = json.load(c)
    return pingrole[str(message.guild.id)]

def get_welcomemsgchannel(client, ctx):
    with open('Legolas/datenbank/welcomemsgchannel.json', 'r') as c:
        webhook = json.load(c)
    return webhook[str(ctx.guild.id)]

def get_welcomemsg(client, ctx):
    with open('Legolas/datenbank/welcomemsg.json', 'r') as f:
        welcomemsg = json.load(f)
        return welcomemsg[str(ctx.guild.id)]

def get_votings(client, ctx):
    with open('Legolas/datenbank/votings.json', 'r') as f:
        channel = json.load(f)
        return channel[str(ctx.channel.id)]

def get_antipublish(client, ctx):
    with open('Legolas/datenbank/antipublisher.json', 'r') as f:
        channel = json.load(f)
        return channel[str(ctx.channel.id)]

emojis = ["<:VoteUp:816278399206031390>", "<:VoteDown:816278398996447293>"]


class Suggester(discord.ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)
    @discord.ui.button(label="Vorschlag einreichen", style=discord.ButtonStyle.success, emoji="💡", custom_id="persistent_view:suggestions")
    async def suggestion(self, interaction: discord.Interaction, button: discord.ui.Button):
        erfolgreich = f"{icon_accept} Dein Vorschlag wurde erfolgreich mitgeteilt!"
        fehler = f"{icon_denied} Das Vorschlägemodul ist auf dem Server deaktiviert!"
        try:
            suggestc = interaction.guild.get_channel(get_suggest(self, interaction))
        except KeyError:
            return await interaction.response.send_message(content=fehler, ephemeral=True)

        class Frage(ui.Modal, title=f"{interaction.guild.name} Vorschläge"):
            answer = ui.TextInput(label="Vorschlag", style=discord.TextStyle.paragraph, required=True,
                                  placeholder=f"Gebe deinen Vorschlag ein . . .")
            async def on_submit(self, interaction: discord.Interaction):
                embed = discord.Embed(title=f"Vorschlag von {interaction.user}",
                                      description=self.answer.value,
                                      color=color_gray)
                embed.set_thumbnail(url=interaction.user.display_avatar.url)
                embed.set_footer(text=f"Stimmt mit den Reaktionen über den Vorschlag ab!")
                try:
                    mod = discord.utils.get(interaction.guild.roles, id=get_pingrole(self, interaction))
                    suggestion_message = await suggestc.send(content=mod.mention, embed=embed)
                except KeyError:
                    suggestion_message = await suggestc.send(embed=embed)
                await suggestion_message.add_reaction(icon_vote_up)
                await suggestion_message.add_reaction(icon_vote_down)
                await interaction.response.send_message(content=erfolgreich, ephemeral=True)
        await interaction.response.send_modal(Frage())

class Features(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hit", description="Werfe einen anderen Nutzer mit einem Kissen ab")
    @app_commands.describe(nutzer="Welchen Nutzer möchtest du abwerfen?")
    async def hit(self, interaction: discord.Interaction, nutzer: discord.Member):
        if interaction.user == nutzer:
            return await interaction.response.send_message(
                content=f"{icon_denied} Du möchtest dich sicher nicht selbst abwerfen!")
        else:
            embed = discord.Embed(
                description=f"> {interaction.user.mention} hat {nutzer.mention} mit einem Kissen abgeworfen! ",
                color=interaction.user.color)
            embed.set_image(url=kill_image)
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="poll", description="Erstelle eine mini Umfrage")
    @app_commands.describe(kanal="In welchen Kanal, soll die Umfrage kommen?",
                           nachricht="Über was soll abgestimmt werden? (Nur Up-/Downvote Umfragen möglich)",
                           titel="Was soll im Titel stehen?")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(send_messages=True, embed_links=True, use_external_emojis=True,
                                             add_reactions=True)
    async def poll(self, interaction: discord.Interaction, kanal: discord.TextChannel, nachricht: str,
                   titel: str = None):
        await interaction.response.defer(ephemeral=True)
        if titel is None:
            embed1 = discord.Embed(title=f"Umfrage",
                                   description=nachricht,
                                   color=0xffdb5e)
            embed1.set_footer(text=f"Umfrage von {interaction.user}", icon_url=interaction.user.display_avatar.url)
            embed1.set_image(url=url_fett)
            msg = await kanal.send(embed=embed1)
        else:
            embed1 = discord.Embed(title=f"Umfrage: {titel}",
                                   description=nachricht,
                                   color=0xffdb5e)
            embed1.set_footer(text=f"Umfrage von {interaction.user}", icon_url=interaction.user.display_avatar.url)
            embed1.set_image(url=url_fett)
            msg = await kanal.send(embed=embed1)
        await msg.add_reaction(icon_vote_up)
        await msg.add_reaction(icon_vote_down)
        await interaction.edit_original_response(content=f"{icon_accept} Die Umfrage wurde erfolgreich gesendet!")

    @app_commands.command(name="suggest", description="Schicke einen Vorschlag für den Server")
    @app_commands.describe(vorschlag="Was möchtest du vorschlagen?")
    @app_commands.checks.bot_has_permissions(send_messages=True, embed_links=True, use_external_emojis=True,
                                             add_reactions=True)
    async def suggest(self, interaction: discord.Interaction, vorschlag: str):
        erfolgreich = f"{icon_accept} Dein Vorschlag wurde erfolgreich mitgeteilt!"
        fehler = f"{icon_denied} Das Vorschlägemodul ist auf dem Server deaktiviert!"
        await interaction.response.defer(ephemeral=True)
        try:
            suggestc = self.bot.get_channel(get_suggest(self, interaction))
        except KeyError:
            return await interaction.edit_original_response(content=fehler)
        embed = discord.Embed(title=f"Vorschlag von {interaction.user}",
                              description=vorschlag,
                              color=color_gray)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"Stimmt mit den Reaktionen über den Vorschlag ab!")
        try:
            mod = discord.utils.get(interaction.guild.roles, id=get_pingrole(self, interaction))
            suggestion_message = await suggestc.send(content=mod.mention, embed=embed)
        except KeyError:
            suggestion_message = await suggestc.send(embed=embed)
        await suggestion_message.add_reaction(icon_vote_up)
        await suggestion_message.add_reaction(icon_vote_down)
        await interaction.edit_original_response(content=erfolgreich)

    @commands.Cog.listener()
    async def react(self, message):
        for emoji in icon_votes:
            await message.add_reaction(emoji)

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.channel.type == discord.ChannelType.news and bot_has_permissions(send_messages=True, manage_messages=True):
                await message.publish()

            if not message.author.bot:
                if message.channel.id == 1113198958756516061:
                    await self.react(message)
        except discord.errors.Forbidden:
            pass

    @commands.Cog.listener()
    async def on_member_join(self, user):
        """Welcomer"""
        try:
            if user == self.bot.user:
                return
            if user.guild.id:
                message = welcome_variables.welcome_message(get_welcomemsg(self, user), user)
                webhook = discord.Webhook.from_url(get_welcomemsgchannel(self, user), session=aiohttp.ClientSession())
                await webhook.send(message)
            else:
                return
        except KeyError:
            return

async def setup(bot: commands.Bot):
    await bot.add_cog(Features(bot))  # , guild=discord.Object(id=756526359521656951))