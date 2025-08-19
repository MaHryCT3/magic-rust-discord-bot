from typing import Self

import discord
from discord import Interaction
from discord.ui import Item

from bot.apps.reports.constants import REPORT_COOLDOWN
from bot.apps.reports.errors import ReportsError, UserReportCooldownError
from bot.apps.reports.services.cooldowns import report_cooldown
from bot.apps.reports.ui.server_select_view import (
    BaseServerSelectView,
    CheaterServerSelectView,
    LimitServerSelectView,
)
from core.api_clients.magic_rust import MagicRustServerDataAPI
from core.localization import LocaleEnum, LocalizationDict


class BaseReportButton(discord.ui.Button):
    select_view_class: type[BaseServerSelectView]
    button_name: str
    localization_text_map: dict[LocaleEnum, str]
    style: discord.ButtonStyle

    select_server_localization_text_map: dict[LocaleEnum, str] = LocalizationDict(
        {
            LocaleEnum.en: 'Select server',
            LocaleEnum.ru: 'Выберите сервер',
        }
    )

    def __init__(self, locale: LocaleEnum):
        self.locale = locale
        super().__init__(
            label=self.localization_text_map[self.locale],
            style=self.style,
            custom_id=f'report:{self.locale.value}:button:{self.button_name}',
        )

    async def callback(self, interaction: Interaction):
        if cooldown_end_at := await report_cooldown.get_cooldown_end_at(
            interaction.user.id,
            self.locale,
            REPORT_COOLDOWN,
        ):
            raise UserReportCooldownError(cooldown_end_timestamp=cooldown_end_at, locale=self.locale)

        servers_data = await MagicRustServerDataAPI().get_server_data()

        select_server_view = self.select_view_class(servers_data, self.locale)
        await interaction.respond(
            self.select_server_localization_text_map[self.locale],
            view=select_server_view,
            ephemeral=True,
            delete_after=60,
        )


class CheaterReportButton(BaseReportButton):
    select_view_class = CheaterServerSelectView
    button_name = 'cheater'
    localization_text_map: dict[LocaleEnum, str] = {
        LocaleEnum.en: 'Report cheater',
        LocaleEnum.ru: 'Пожаловаться на читера',
    }
    style = discord.ButtonStyle.red


class LimitReportButton(BaseReportButton):
    select_view_class = LimitServerSelectView
    button_name = 'limit'
    localization_text_map: dict[LocaleEnum, str] = {
        LocaleEnum.en: 'Report players limit violations',
        LocaleEnum.ru: 'Пожаловаться на нарушение лимита',
    }
    style = discord.ButtonStyle.primary


class ReportView(discord.ui.View):

    def __init__(self, locale: LocaleEnum):
        super().__init__(
            CheaterReportButton(locale),
            LimitReportButton(locale),
            timeout=None,
        )

    @classmethod
    def all_locales_init(cls) -> list[Self]:
        return [cls(locale=locale) for locale in LocaleEnum]

    async def on_error(self, exception: Exception, item: Item, interaction: Interaction) -> None:
        if isinstance(exception, ReportsError):
            return await interaction.respond(exception.message, ephemeral=True, delete_after=REPORT_COOLDOWN)
        return await super().on_error(exception, item, interaction)
