import discord

from bot.apps.voice_channels.exceptions import DontHaveAccessError


async def check_panel_access(voice_channel: discord.VoiceChannel, member: discord.Member):
    if not voice_channel.permissions_for(member).manage_channels:
        raise DontHaveAccessError()
