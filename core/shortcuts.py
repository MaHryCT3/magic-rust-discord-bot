from typing import TYPE_CHECKING, Union

import discord
from discord import Thread

if TYPE_CHECKING:
    from discord.guild import GuildChannel


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


async def get_or_fetch_channel(guild: discord.Guild, channel_id: int) -> Union['GuildChannel', Thread, None]:
    if channel := guild.get_channel(channel_id):
        return channel
    return await guild.fetch_channel(channel_id)


async def get_or_fetch_user(bot: discord.Client, user_id: int) -> discord.User:
    if user := bot.get_user(user_id):
        return user
    return await bot.fetch_user(user_id)


async def get_or_fetch_user_message(bot: discord.Client, user_id: int, message_id: int) -> discord.Message:
    if message := bot.get_message(message_id):
        return message

    user = await get_or_fetch_user(bot, user_id)
    return await user.fetch_message(message_id)


async def fetch_active_forum_threads(channel: discord.ForumChannel) -> list[discord.Thread]:
    active_threads = await channel.guild.active_threads()
    return [thread for thread in active_threads if thread.parent_id == channel.id]
