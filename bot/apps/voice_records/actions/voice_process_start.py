import discord

from bot.apps.voice_records.services.voice_process_storage import ActiveVoiceProcessStorage, ActiveVoiceProcessStruct
from bot.apps.voice_records.services.voice_records_api import VoiceRecordsAPI
from bot.apps.voice_records.ui.voice_process import VoiceProcessEmbed
from core.actions.abstract import AbstractAction
from dataclasses import dataclass, field


@dataclass
class VoiceProcessStartAction(AbstractAction):
    craig_voice_url: str
    text_channel: discord.TextChannel

    _voice_process_storage: ActiveVoiceProcessStorage = field(default_factory=ActiveVoiceProcessStorage, init=False)
    _voice_records_api: VoiceRecordsAPI = field(default_factory=VoiceRecordsAPI, init=False)

    async def action(self):
        voice_record_id = await self._voice_records_api.start_craig_transcribe(self.craig_voice_url)
        voice_record_state = await self._voice_records_api.get_voice_record(voice_record_id)

        embed = VoiceProcessEmbed.build(
            url=self.craig_voice_url,
            state=voice_record_state.process_status,
            is_error=voice_record_state.is_process_error,
        )

        message = await self.text_channel.send(embed=embed)
        voice_process = ActiveVoiceProcessStruct(
            voice_record_id=voice_record_id,
            channel_id=self.text_channel.id,
            message_id=message.id,
            craig_url=self.craig_voice_url,
        )
        await self._voice_process_storage.add_voice_process(voice_process)
