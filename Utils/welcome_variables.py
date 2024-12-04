import discord

def welcome_message(message: str, member: discord.Member) -> str:
    guild = member.guild

    return (
        message.replace("{user}", str(member))
        .replace("{user.name}", member.name)
        .replace("{user.mention}", member.mention)
        .replace("{user.id}", str(member.id))
        .replace("{guild.name}", guild.name)
        .replace("{guild.member_counter}", str(guild.member_count))
        .replace("{guild.id}", str(guild.id))
    )