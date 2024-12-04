from discord.ext import commands
import discord

class AdvancedMember(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            return await commands.UserConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                user_id = int(argument, base=10)
                return await ctx.bot.fetch_user(user_id)
            except (ValueError, discord.NotFound):
                raise commands.UserNotFound(argument)