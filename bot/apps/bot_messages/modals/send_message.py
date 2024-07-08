import datetime

import discord
from discord import Interaction

from bot.apps.bot_messages.embeds import SendMessageByBotEmbed
from bot.apps.bot_messages.modals.base import BaseSendMessageByBotModal
from bot.apps.bot_messages.services import DelayedMessage, DelayedMessageService
from bot.config import logger
from bot.constants import DATETIME_FORMAT


class SendMessageByBotModal(BaseSendMessageByBotModal):

    async def callback(self, interaction: Interaction):
        channel: discord.TextChannel = interaction.channel

        embed = SendMessageByBotEmbed.build(
            content=self.content,
            image_url=self.image_url,
        )

        await channel.send(content=self.text_before, embeds=[embed])
        logger.info(f'message "{self.content[:15]}..." was send by {interaction.user}:{interaction.user.id}')
        await interaction.respond('Сообщение отправлено', ephemeral=True)
