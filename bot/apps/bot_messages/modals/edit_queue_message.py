import datetime

from discord import Interaction

from bot.apps.bot_messages.autocomplete import parse_autocomplete_time
from bot.apps.bot_messages.modals.base import BaseSendMessageByBotModal
from bot.apps.bot_messages.services import DelayedMessage
from bot.config import settings
from bot.constants import DATETIME_FORMAT
from core.ui.modals import InputText


class EditQueueMessageModal(BaseSendMessageByBotModal):
    send_time = InputText(
        label='Время отправки',
        placeholder='14:00 или 08.09.2024 14:00',
        required=True,
    )

    def __init__(
        self,
        edit_message: DelayedMessage,
        paginator,
        button_interaction,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.edit_message = edit_message
        self.paginator = paginator
        self.button_interaction = button_interaction

        # Предустанавливаем значение в модалку
        self.content = edit_message.embed_content
        self.image_url = edit_message.image_url
        self.send_time = datetime.datetime.fromtimestamp(
            edit_message.send_time,
            settings.TIMEZONE,
        ).strftime(DATETIME_FORMAT)

    async def callback(self, interaction: Interaction):
        await self.delayed_message_service.remove_message(self.edit_message.uuid)
        await self._add_message_to_queue(
            send_time=parse_autocomplete_time(self.send_time),
            channel_id=self.edit_message.channel_id,
            channel_name=self.edit_message.channel_name,
            channel_mention=self.edit_message.channel_mention,
        )

        await interaction.respond('Сообщение отредактировано', ephemeral=True)
        await self.paginator.update_messages(self.button_interaction)
