from operator import attrgetter

from discord.ext import pages
from typing import Self
import discord

from bot.apps.bot_messages.embeds import QueueMessageEmbed
from bot.apps.bot_messages.exceptions import QueueMessageIsEmpty
from bot.apps.bot_messages.paginator.buttons import (
    QueueMessageDeleteButton,
    QueueMessageEditButton,
    QueueMessageSendButton,
)
from bot.apps.bot_messages.services import DelayedMessage, DelayedMessageService


class QueueMessagePaginator(pages.Paginator):
    messages: list[DelayedMessage]
    delayed_message_service: DelayedMessageService

    @classmethod
    async def from_delayed_message_service(
        cls,
        delayed_message_service: DelayedMessageService,
    ) -> Self:
        messages = await cls._get_messages(delayed_message_service)
        if not messages:
            raise QueueMessageIsEmpty()

        paginator_pages = cls._get_pages(messages)
        paginator = cls(
            pages=paginator_pages,
            use_default_buttons=False,
            show_indicator=True,
        )
        paginator.messages = messages
        paginator.delayed_message_service = delayed_message_service

        page_buttons = [
            pages.PaginatorButton("page_indicator", style=discord.ButtonStyle.secondary, disabled=True, row=0),
            pages.PaginatorButton("prev", emoji="⬅", style=discord.ButtonStyle.secondary, row=0),
            pages.PaginatorButton("next", emoji="➡", style=discord.ButtonStyle.secondary, row=0),
            QueueMessageDeleteButton(
                delayed_message_service,
                button_type='delete',
                emoji='🗑',
                style=discord.ButtonStyle.danger,
                row=1,
            ),
            QueueMessageEditButton(
                delayed_message_service,
                button_type='edit',
                emoji='📝',
                style=discord.ButtonStyle.primary,
                row=1,
            ),
            QueueMessageSendButton(
                delayed_message_service,
                button_type='send',
                emoji='📤',
                style=discord.ButtonStyle.success,
                row=1,
            ),
        ]

        for button in page_buttons:
            paginator.add_button(button)

        return paginator

    def get_current_message(self) -> DelayedMessage:
        return self.messages[self.current_page]

    async def update_messages(self, interaction: discord.Interaction):
        # дефолтная реализация self.update не подходит, так нужно иметь возмжность
        # использовать этот метод, уже после того как interaction был дан ответ
        if not interaction.response.is_done():
            await interaction.response.defer()

        self.messages = await self._get_messages(self.delayed_message_service)
        paginator_pages = self._get_pages(self.messages)
        if not paginator_pages:
            return await interaction.followup.edit_message(
                message_id=self.message.id,
                embeds=[discord.Embed(title='Очередь сообщений пуста')],
                attachments=[],
                files=[],
                view=None,
            )
        self.pages = paginator_pages
        self.page_count = len(paginator_pages) - 1
        self.current_page = min(self.current_page, self.page_count)
        self.update_buttons()

        # далее идет копипаста self.goto_page, без использования .defer
        if self.show_indicator:
            try:
                self.buttons["page_indicator"]["object"].label = f"{self.current_page + 1}/{self.page_count + 1}"
            except KeyError:
                pass

        page = self.pages[self.current_page]
        page = self.get_page_content(page)

        if page.custom_view:
            self.update_custom_view(page.custom_view)

        files = page.update_files()

        await interaction.followup.edit_message(
            message_id=self.message.id,
            content=page.content,
            embeds=page.embeds,
            attachments=[],
            files=files or [],
            view=self,
        )

    @staticmethod
    async def _get_messages(delayed_message_service) -> list[DelayedMessage]:
        messages = await delayed_message_service.get_messages()
        return sorted(messages, key=attrgetter('send_time'))

    @staticmethod
    def _get_pages(messages: list[DelayedMessage]) -> list[QueueMessageEmbed]:
        return [
            QueueMessageEmbed.build(
                send_time=message.send_time,
                content=message.embed_content,
                image_url=message.image_url,
                channel_mention=message.channel_mention,
                channel_name=message.channel_name,
            )
            for message in messages
        ]
