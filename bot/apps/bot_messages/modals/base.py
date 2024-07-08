import datetime

import discord

from bot.apps.bot_messages.services import DelayedMessage, DelayedMessageService
from bot.core.ui.modals import BaseModal, InputText


class BaseSendMessageByBotModal(BaseModal):
    content = InputText(
        label='Текст',
        placeholder='Вышло обновление в расте, очень круто!',
        style=discord.InputTextStyle.long,
        required=False,
        max_length=1024,
    )
    image_url = InputText(
        label='Ссылка на картинку',
        placeholder='Прямая ссылка на картинку. Например, ссылку можно взять из дискорд чата',
        required=False,
    )
    # TODO: Добавить в валидацию image_url

    def __init__(
        self,
        delayed_message_service: DelayedMessageService,
        text_before: str = '',
        send_time: datetime.datetime | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.delayed_message_service = delayed_message_service
        self.text_before = text_before
        self.send_time = send_time

    async def _add_message_to_queue(
        self,
        send_time: datetime.datetime,
        channel_id: int,
        channel_name: str,
        channel_mention: str,
    ):
        delayed_message = DelayedMessage(
            send_time=send_time.timestamp(),
            before_text=self.text_before,
            embed_content=self.content,
            image_url=self.image_url,
            channel_id=channel_id,
            channel_name=channel_name,
            channel_mention=channel_mention,
        )
        await self.delayed_message_service.add_message(delayed_message)
        return delayed_message
