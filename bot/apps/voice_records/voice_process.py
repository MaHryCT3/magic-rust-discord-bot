import discord
from discord import SlashCommandGroup
from discord.ext import tasks
from discord.ext.commands import Cog

from bot import MagicRustBot
from bot.apps.voice_records.actions.voice_process_start import VoiceProcessStartAction
from bot.apps.voice_records.actions.voice_processes_update import (
    VoiceProcessUpdateAction,
)
from core.utils.decorators import suppress_exceptions


class VoiceProcessCog(Cog):
    voice_process = SlashCommandGroup(
        name='voice',
        contexts={discord.InteractionContextType.guild},
        default_member_permissions=discord.Permissions(ban_members=True),
    )

    def __init__(self, bot: MagicRustBot):
        self.bot = bot

        self._guild: discord.Guild = None

    def cog_unload(self):
        self._update_voice_process_status.cancel()

    @voice_process.command(description='Запустить обработку аудиозаписи')
    async def process(self, ctx: discord.ApplicationContext, craig_url: str):
        await VoiceProcessStartAction(
            craig_voice_url=craig_url,
            text_channel=ctx.channel,
        ).execute()

    @Cog.listener()
    async def on_ready(self):
        self._guild = await self.bot.get_or_fetch_main_guild()
        self._update_voice_process_status.start()

    @tasks.loop(seconds=25)
    @suppress_exceptions
    async def _update_voice_process_status(self):
        await VoiceProcessUpdateAction(self._guild).execute()
