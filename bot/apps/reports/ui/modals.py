from typing import Final

import discord
from discord import Interaction

from bot.apps.reports.constants import REPORT_COOLDOWN, VK_REPORT_MESSAGE_TEMPLATE
from bot.apps.reports.errors import UserReportCooldownError
from bot.apps.reports.services.cooldowns import report_cooldown
from bot.apps.reports.services.report_sender import ChatTypes, ReportVKSender
from core.api_clients.magic_rust import (
    GameModeTypes,
    MagicRustServerData,
)
from core.localization import LocaleEnum
from core.ui.modals import BaseLocalizationModal, InputText


class BaseReportModal(BaseLocalizationModal):
    MAX_SERVER_NAME_LENGTH_IN_TITLE: Final[int] = 25

    player_info_input = InputText(
        max_length=250,
        placeholder='https://steamcommunity.com/profiles/76561199999999999, https://steamcommu',
        style=discord.InputTextStyle.multiline,
        required=True,
    )

    message_input = InputText(
        max_length=1024,
        style=discord.InputTextStyle.multiline,
    )

    inputs_localization_map = {
        player_info_input: {
            LocaleEnum.ru: dict(
                label='На кого жалуетесь (ссылки на профиля)',
            ),
            LocaleEnum.en: dict(
                label='Who are you report about (link to profiles)',
            ),
        },
        message_input: {
            LocaleEnum.ru: dict(
                label='Текст жалобы',
            ),
            LocaleEnum.en: dict(
                label='Report text',
            ),
        },
    }

    answer_localization_map: dict[LocaleEnum, str] = {
        LocaleEnum.en: 'Report has send. Thank you for reaching out',
        LocaleEnum.ru: 'Жалоба отправлена. Спасибо за обращение',
    }

    def __init__(self, *args, server: MagicRustServerData, **kwargs):
        self.server = server
        super().__init__(*args, **kwargs)

        title = self.title_localization_map[self.locale].format(server_name=self.server.short_title)
        self.title = title[: self.MAX_SERVER_NAME_LENGTH_IN_TITLE]

    async def callback(self, interaction: Interaction):
        await self._check_on_cooldown(interaction.user.id)
        await self._send_report_to_vk(interaction)
        await self._set_cooldown(interaction.user.id)
        await self._send_answer(interaction)

    async def _check_on_cooldown(self, user_id: int):
        if cooldown_end_at := await report_cooldown.get_cooldown_end_at(
            user_id,
            self.locale,
            REPORT_COOLDOWN,
        ):
            raise UserReportCooldownError(cooldown_end_timestamp=cooldown_end_at, locale=self.locale)

    async def _send_report_to_vk(self, interaction: Interaction):
        raise NotImplementedError

    def _get_report_message(self, interaction: Interaction):
        return VK_REPORT_MESSAGE_TEMPLATE.format(
            server_name=self.server.short_title,
            discord_name=interaction.user.name,
            discord_id=interaction.user.id,
            players=self.player_info_input,
            report_text=self.message_input,
        )

    async def _set_cooldown(self, user_id: int):
        await report_cooldown.set_user_cooldown(user_id, self.locale, REPORT_COOLDOWN)

    async def _send_answer(self, interaction: Interaction):
        answer_message = self.answer_localization_map[self.locale]
        await interaction.respond(answer_message, ephemeral=True, delete_after=20)


class CheaterReportModal(BaseReportModal):
    title_localization_map = {
        LocaleEnum.en: 'Cheater. {server_name}',
        LocaleEnum.ru: 'Читер. {server_name}',
    }

    async def _send_report_to_vk(self, interaction: Interaction):
        chat_type = self._get_vk_chat_type_for_server()
        message = self._get_report_message(interaction)
        await ReportVKSender().send_message(chat_type, message=message)

    def _get_vk_chat_type_for_server(self) -> ChatTypes:
        if self.server.game_mode == GameModeTypes.VANILLA:
            return ChatTypes.OFFICIAL
        return ChatTypes.MODDED


class LimitReportModal(BaseReportModal):
    title_localization_map = {
        LocaleEnum.en: 'Players limit. {server_name}',
        LocaleEnum.ru: 'Лимит игроков. {server_name}',
    }

    async def _send_report_to_vk(self, interaction: Interaction):
        message = self._get_report_message(interaction)
        await ReportVKSender().send_message(ChatTypes.LIMIT, message=message)
