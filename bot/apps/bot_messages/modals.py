import datetime

import discord
from discord import Interaction

from bot.apps.bot_messages.embeds import SendMessageByBotEmbed
from bot.apps.bot_messages.services import DelayedMessage, DelayedMessageService
from bot.config import logger
from bot.constants import DATETIME_FORMAT
from bot.core.ui.modals import BaseModal, InputText


class SendMessageByBotModal(BaseModal):
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

    def __init__(
        self,
        delayed_message_service: DelayedMessageService,
        text_before: str,
        send_time: datetime.datetime | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.delayed_message_service = delayed_message_service
        self.send_time = send_time
        self.text_before = text_before

    async def callback(self, interaction: Interaction):
        channel: discord.TextChannel = interaction.channel
        if self.send_time:
            delayed_message = await self._add_message_to_queue(channel)
            logger.info(f'message {delayed_message} was added to queue by {interaction.user}:{interaction.user.id}')
            await interaction.respond(
                f'Сообщение добавлено в очередь и будет отправлено в {self.send_time.strftime(DATETIME_FORMAT)}',
                ephemeral=True,
            )
            return

        embed = SendMessageByBotEmbed.build(
            content=self.content,
            image_url=self.image_url,
        )

        await channel.send(content=self.text_before, embeds=[embed])
        logger.info(f'message "{self.content[:15]}..." was send by {interaction.user}:{interaction.user.id}')
        await interaction.respond('Сообщение отправлено', ephemeral=True)

    async def _add_message_to_queue(self, channel: discord.TextChannel):
        delayed_message = DelayedMessage(
            send_time=self.send_time.timestamp(),
            before_text=self.text_before,
            embed_content=self.content,
            image_url=self.image_url,
            channel_id=channel.id,
        )
        await self.delayed_message_service.add_message(delayed_message)
        return delayed_message
