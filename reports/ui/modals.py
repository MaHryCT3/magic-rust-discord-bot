import discord
from discord import Interaction

from core.localization import LocaleEnum
from core.ui.modals import BaseLocalizationModal, InputText
from reports.constants import REPORT_COOLDOWN, VK_REPORT_MESSAGE_TEMPLATE
from reports.exceptions import UserReportCooldownError
from reports.services import ChatTypes, ReportVKSender
from reports.services.cooldowns import report_cooldown


class BaseReportModal(BaseLocalizationModal):
    player_info_input = InputText(
        max_length=250,
        placeholder='https://steamcommunity.com/profiles/76561198365812808, https://steamcommu',
        required=True,
    )

    server = InputText(
        max_length=10,
        placeholder='15',
        required=True,
    )

    message_input = InputText(
        max_length=1024,
        style=discord.InputTextStyle.multiline,
    )

    inputs_localization_map = {
        server: {
            LocaleEnum.en: dict(label='Server number or name (main, long)'),
            LocaleEnum.ru: dict(label='Номер сервера или название (main, long)'),
        },
        player_info_input: {
            LocaleEnum.ru: dict(
                label='На кого жалуетесь (ссылка на профиль)',
            ),
            LocaleEnum.en: dict(
                label='Who are you report about (link to profile)',
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
        LocaleEnum.en: 'Report has send',
        LocaleEnum.ru: 'Жалоба отправлена',
    }

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
        pass

    def _get_report_message(self, interaction: Interaction):
        return VK_REPORT_MESSAGE_TEMPLATE.format(
            server_name=self.server,
            discord_name=interaction.user.name,
            discord_id=interaction.user.id,
            players=self.player_info_input,
            report_text=self.message_input,
        )

    async def _set_cooldown(self, user_id: int):
        await report_cooldown.set_user_cooldown(user_id, self.locale, REPORT_COOLDOWN)

    async def _send_answer(self, interaction: Interaction):
        answer_message = self.answer_localization_map[self.locale]
        await interaction.respond(answer_message, ephemeral=True, delete_after=10)


class CheaterReportModal(BaseReportModal):
    title_localization_map = {
        LocaleEnum.en: 'Report cheat',
        LocaleEnum.ru: 'Жалоба на читера',
    }

    async def _send_report_to_vk(self, interaction: Interaction):
        chat_type = self._get_vk_chat_type_for_server()
        message = self._get_report_message(interaction)
        await ReportVKSender().send_message(chat_type, message=message)

    def _get_vk_chat_type_for_server(self) -> ChatTypes:
        # TODO: костыль, потом выбор свервера будет по другому
        official_names = [
            'mein',
            'меин',
            'ein',
            'main',
            'мейн',
            'мэйн',
            'майн',
            'айн',
            'ейн',
            'меин',
            'lng',
            'ong',
            'long',
            'лонг',
            'лонк',
            'онк',
            'онг',
            'main',
            'mein',
        ]
        for name in official_names:
            if name in self.server.lower():
                return ChatTypes.OFFICIAL
        return ChatTypes.MODDED


class LimitReportModal(BaseReportModal):
    title_localization_map = {
        LocaleEnum.en: 'Report players limit',
        LocaleEnum.ru: 'Жалоба на нарушение лимита',
    }

    async def _send_report_to_vk(self, interaction: Interaction):
        message = self._get_report_message(interaction)
        await ReportVKSender().send_message(ChatTypes.LIMIT, message=message)
