import discord


async def can_dm_user(user: discord.User) -> bool:
    try:
        await user.send()
    except discord.Forbidden:
        return False
    except discord.HTTPException:
        return True


async def get_or_fetch_member(guild: discord.Guild, user_id: int) -> discord.Member | None:
    if member := guild.get_member(user_id):
        return member
    return await guild.fetch_member(user_id)


async def get_or_fetch_channel(guild: discord.Guild, channel_id: int) -> discord.TextChannel | None:
    if channel := guild.get_channel(channel_id):
        return channel
    return await guild.fetch_channel(channel_id)
