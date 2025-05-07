from dataclasses import dataclass, field
import io

import discord
import sentry_sdk

from bot.apps.voice_records.services.voice_process_storage import ActiveVoiceProcessStorage, ActiveVoiceProcessStruct
from bot.apps.voice_records.services.voice_records_api import VoiceRecordsAPI
from bot.apps.voice_records.structs.voice_record import VoiceRecord, VoiceProcessStatusEnum
from bot.apps.voice_records.ui.voice_process import VoiceProcessEmbed
from core.actions.abstract import AbstractAction
from core.shortcuts import get_or_fetch_channel


@dataclass
class VoiceProcessUpdateAction(AbstractAction):
    guild: discord.Guild

    _voice_process_storage: ActiveVoiceProcessStorage = field(default_factory=ActiveVoiceProcessStorage, init=False)
    _voice_records_api: VoiceRecordsAPI = field(default_factory=VoiceRecordsAPI, init=False)

    async def action(self):
        active_processes = await self._voice_process_storage.get_all_processes()
        for active_process in active_processes:
            try:
                await self._update_process_state(active_process)
            except Exception as ex:
                sentry_sdk.capture_exception(ex)

    async def _update_process_state(self, active_process: ActiveVoiceProcessStruct):
        message = await self._get_message(active_process.channel_id, active_process.message_id)
        state = await self._voice_records_api.get_voice_record(active_process.voice_record_id)

        embed = VoiceProcessEmbed.build(
            url=active_process.craig_url,
            state=state.process_status,
            is_error=state.is_process_error,
        )

        if state.transcribed_text:
            transcribe_file = self._get_transcribe_file(state.transcribed_text, filename=f'transcribe-{state.id}.txt')
            await message.edit(file=transcribe_file, embeds=[embed])
        else:
            await message.edit(embeds=[embed])

        if self._is_process_end(state):
            await self._voice_process_storage.delete_process(active_process.voice_record_id)

    async def _get_message(self, channel_id: int, message_id: int) -> discord.Message:
        channel = await get_or_fetch_channel(self.guild, channel_id)
        return await channel.fetch_message(message_id)

    def _is_process_end(self, voice_record: VoiceRecord) -> bool:
        return voice_record.is_process_error or voice_record.process_status == VoiceProcessStatusEnum.COMPLETED

    def _get_transcribe_file(self, transcribe_text: str, filename: str) -> discord.File:
        transcribe_file = discord.File(
            io.BytesIO(transcribe_text.encode()),
            filename=filename,
        )
        return transcribe_file
