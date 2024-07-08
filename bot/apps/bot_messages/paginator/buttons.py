from typing import TYPE_CHECKING

import discord
from discord.ext import pages

from bot.apps.bot_messages.modals import EditQueueMessageModal
from bot.apps.bot_messages.services import DelayedMessageService
from bot.apps.bot_messages.utils import send_delayed_message

if TYPE_CHECKING:
    from bot.apps.bot_messages.paginator.paginator import QueueMessagePaginator


class BaseQueueMessageButton(pages.PaginatorButton):
    def __init__(self, delayed_message_service: DelayedMessageService, **kwargs):
        super().__init__(**kwargs)
        self.delayed_message_service = delayed_message_service


class QueueMessageDeleteButton(BaseQueueMessageButton):
    paginator: 'QueueMessagePaginator'

    async def callback(self, interaction: discord.Interaction):
        message = self.paginator.messages.pop(self.paginator.current_page)
        await self.paginator.delayed_message_service.remove_message(message.uuid)
        return await self.paginator.update_messages(interaction)


class QueueMessageEditButton(BaseQueueMessageButton):
    paginator: 'QueueMessagePaginator'

    async def callback(self, interaction: discord.Interaction):
        message_to_edit = self.paginator.get_current_message()
        modal = EditQueueMessageModal(
            title='Редактирование сообщения из очереди',
            delayed_message_service=self.delayed_message_service,
            edit_message=message_to_edit,
            paginator=self.paginator,
            button_interaction=interaction,
        )

        await interaction.response.send_modal(modal)


class QueueMessageSendButton(BaseQueueMessageButton):
    paginator: 'QueueMessagePaginator'

    async def callback(self, interaction: discord.Interaction):
        message_to_send = self.paginator.get_current_message()
        await send_delayed_message(message_to_send, interaction.client)
        await self.delayed_message_service.remove_message(message_to_send.uuid)
        await self.paginator.update_messages(interaction)
