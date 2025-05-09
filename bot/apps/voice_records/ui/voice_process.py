import discord

from bot.apps.voice_records.structs.voice_record import VoiceProcessStatusEnum
from bot.constants import MAIN_COLOR


class VoiceProcessEmbed(discord.Embed):
    process_status_translate = {
        VoiceProcessStatusEnum.AWAITING_PROCESS: '🕒 В ожидании',
        VoiceProcessStatusEnum.DOWNLOADING_AUDIO: '⬇️🎵 Скачивание аудиозаписи',
        VoiceProcessStatusEnum.AUDIO_PROCESS: '🛠️🎧 Обработка аудио',
        VoiceProcessStatusEnum.AUDIO_TRANSCRIPTION: '📝🎤 Транскрибация аудио',
        VoiceProcessStatusEnum.COMPLETED: '✅ Процесс завершен',
    }

    text_template: str = """[Запись в обработке]({url})
Состояние: {voice_state}
    """

    text_template_error: str = """[Запись в обработке]({url})
❌Состояние: {voice_state}
Произошла ошибка.
    """

    @classmethod
    def build(cls, url: str, state: VoiceProcessStatusEnum, is_error: bool):
        embed = cls(
            color=MAIN_COLOR,
        )

        template = cls.text_template
        if is_error:
            template = cls.text_template_error

        text = template.format(
            url=url,
            voice_state=cls.process_status_translate[state],
        )
        embed.add_field(
            name='',
            value=text,
        )

        return embed
