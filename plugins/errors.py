import discord
import discord.errors
from discord.ext import commands
from discord import app_commands
from Utils.formatting import *


class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.tree.on_error = self.on_app_command_error

    @commands.Cog.listener()
    async def on_app_command_error(self, interaction, error):
        if isinstance(error, app_commands.errors.BotMissingPermissions):
            fehler = f"{icon_denied} Ich besitze nicht die nötigen Rechte, um diesen Befehl ausführen zu können! (`{', '.join([f for f in error.missing_permissions])}`)"
        elif isinstance(error, app_commands.MissingPermissions):
            fehler = f"{icon_denied} Du besitzt nicht die benötigte Berechtigung, um diesen Befehl auszuführen! (`{', '.join([f for f in error.missing_permissions])}`)"
        elif isinstance(error, discord.errors.Forbidden):
            fehler = f"{icon_denied} Ich besitze nicht die nötigen Rechte, um diesen Befehl ausführen zu können! (`{error.args[0]}`)"
        elif isinstance(error, discord.Forbidden):
            fehler = f"{icon_denied} Ich besitze nicht die nötigen Rechte, um diesen Befehl ausführen zu können!"
        elif isinstance(error, discord.errors.NotFound):
            fehler = f"{icon_denied} Die angegebene Informationen sind ungültig!"
        elif isinstance(error, app_commands.CommandNotFound):
            fehler = f"{icon_denied} Dieser Befehl ist veraltet, bitte verwenden den aktuellen!"
        elif isinstance(error, app_commands.CommandInvokeError):
            fehler = f"{icon_denied} Bitte versuche es erneut, beim verarbeiten ist ein Fehler aufgetreten!"
            print(f"{interaction.guild.name} ({interaction.guild.id}): {error}")
        else:
            print(f"{interaction.guild.name} ({interaction.guild.id}): {error}")
            channel = self.bot.get_channel(778699147724587038)
            try:
                fehler = f"{icon_denied} Es ist ein unerklärlicher Fehler aufgetreten!"
            except Exception as e:
                interaction.send(f"Fehler\n{type(e).__name__}: {e}")
                embed = discord.Embed(title="**Fehler Meldung**",
                                      color=discord.Color.red())
                embed.add_field(name="**Server**",
                                value=f"{interaction.guild.name}\n"
                                      f"`{interaction.guild.id}`")
                embed.add_field(name="**Benutzer**",
                                value=f"{interaction.user}\n"
                                      f"`{interaction.user.id}`")
                embed.add_field(name="**Befehl**",
                                value=f"`{interaction.command.name}`")
                embed.add_field(name="**Code Fehler**",
                                value=f"```py\n{type(error).__name__}: {error}```",
                                inline=False)
                return await channel.send(embed=embed)
        link = discord.ui.View()
        link.add_item(discord.ui.Button(label="Support Server", style=discord.ButtonStyle.link, url=url_support))
        try:
            await interaction.response.send_message(content=fehler, view=link, ephemeral=True)
        except discord.errors.InteractionResponded:
            await interaction.edit_original_response(content=fehler, view=link)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, "on_error") or \
                (ctx.command and hasattr(ctx.cog, f"_{ctx.command.cog_name}__error")):
            return
        if isinstance(error, commands.CommandInvokeError):
            error = error.original
        if isinstance(error, commands.BadArgument) or isinstance(error, commands.BadUnionArgument):
            if isinstance(error, commands.RoleNotFound):
                fehler = f"{icon_denied} Die Rolle konnte nicht gefunden werden!"
            elif isinstance(error, commands.MemberNotFound):
                fehler = f"{icon_denied} Der Nutzer konnte nicht gefunden werden!"
            elif isinstance(error, commands.UserNotFound):
                fehler = f"{icon_denied} Der Nutzer konnte nicht gefunden werden!"
            elif isinstance(error, commands.ChannelNotFound):
                fehler = f"{icon_denied} Der Kanal konnte nicht gefunden werden!"
            elif isinstance(error, commands.GuildNotFound):
                fehler = f"{icon_denied} Der Server konnte nicht gefunden werden!"
            elif isinstance(error, commands.BadInviteArgument):
                fehler = f"{icon_denied} Die Einladung konnte nicht gefunden werden!"
            else:
                return print(error)
            await ctx.reply(content=fehler, mention_author=False)

        elif isinstance(error, commands.MissingRequiredArgument):
            fehler = f"{icon_denied} Bitte überprüfe deine Angaben auf Vollständigkeit!"
            await ctx.reply(content=fehler, mention_author=False)
        elif isinstance(error, commands.BotMissingPermissions):
            fehler = f"{icon_denied} Ich besitze nicht die nötigen Rechte, um diesen Befehl ausführen zu können!"
            await ctx.reply(content=fehler, mention_author=False)

        elif isinstance(error, commands.MissingPermissions):
            fehler = f"{icon_denied} Du hast nicht die nötige Berechtigung, diesen Befehl auszuführen zu können!"
            await ctx.reply(content=fehler, mention_author=False)

        elif isinstance(error, discord.errors.Forbidden):
            fehler = f"{icon_denied} Ich besitze nicht die nötigen Rechte, um diesen Befehl ausführen zu können!"
            await ctx.reply(content=fehler, mention_author=False)

        elif isinstance(error, commands.CommandNotFound):
            pass

        elif isinstance(error, commands.CommandInvokeError):
            return print(error)

        else:
            print(f"{ctx.guild.name} ({ctx.guild.id}): {error}")
            kanal = self.bot.get_channel(825132681502654504)
            try:
                fehler = f"```py\n{error}```"
                await ctx.reply(content=fehler, mention_author=False)
            except Exception as e:
                ctx.send(f'Fehler\n{type(e).__name__}: {e}')
                embed = discord.Embed(title="**Fehler Meldung**",
                                      color=discord.Color.red())
                embed.add_field(name="**Server**",
                                value=f"{ctx.guild.name}\n"
                                      f"`{ctx.guild.id}`")
                embed.add_field(name="**Benutzer**",
                                value=f"{ctx.author}\n"
                                      f"`{ctx.author.id}`")
                embed.add_field(name="**Befehl**",
                                value=f"`{ctx.command.name}`")
                embed.add_field(name="**Code Fehler**",
                                value=f'```py\n{type(error).__name__}: {error}```',
                                inline=False)
                return await kanal.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Errors(bot))