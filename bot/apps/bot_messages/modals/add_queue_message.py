import discord
from discord import Interaction

from bot.apps.bot_messages.modals.base import BaseSendMessageByBotModal
from bot.config import logger
from bot.constants import DATETIME_FORMAT


class AddQueueMessageModal(BaseSendMessageByBotModal):

    async def callback(self, interaction: Interaction):
        channel: discord.TextChannel = interaction.channel
        delayed_message = await self._add_message_to_queue(
            self.send_time,
            channel.id,
            channel.name,
            channel.mention,
        )
        logger.info(f'message {delayed_message} was added to queue by {interaction.user}:{interaction.user.id}')
        await interaction.respond(
            f'Сообщение добавлено в очередь и будет отправлено в {self.send_time.strftime(DATETIME_FORMAT)}',
            ephemeral=True,
        )
