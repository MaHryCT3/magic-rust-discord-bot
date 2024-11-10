import discord
from discord import Interaction

from bot.apps.reports.ui.modals import (
    BaseReportModal,
    CheaterReportModal,
    LimitReportModal,
)
from core.api_clients.magic_rust import CombinedServerData
from core.localization import LocaleEnum, day_name
from core.utils.date_time import WeekDay


class BaseServerSelectView(discord.ui.View):
    select_server_wipe_day_placeholder_localization = {
        LocaleEnum.ru: 'День вайпа',
        LocaleEnum.en: 'Wipe day',
    }

    select_server_placeholder_localization = {
        LocaleEnum.ru: 'Выберите сервер',
        LocaleEnum.en: 'Select server',
    }

    modal_to_send: type[BaseReportModal]

    def __init__(self, servers: list[CombinedServerData], locale: LocaleEnum):
        self.servers = servers
        self.locale = locale

        # WIPE DAY SELECTOR
        available_servers_wipe_days = {server.wipeday for server in self.servers}
        select_server_wipe_day = discord.ui.Select(
            select_type=discord.ComponentType.string_select,
            options=[
                discord.SelectOption(
                    label=day_name(wipe_day, locale=self.locale),
                    value=str(wipe_day.value),
                )
                for wipe_day in available_servers_wipe_days
            ],
            placeholder=self.select_server_wipe_day_placeholder_localization[self.locale],
        )
        select_server_wipe_day.callback = self._select_server_wipe_day_callback
        self._wipe_day_select = select_server_wipe_day

        # SERVER SELECTOR
        select_server = discord.ui.Select(
            select_type=discord.ComponentType.string_select,
            placeholder=self.select_server_placeholder_localization[self.locale],
        )
        select_server.callback = self._select_server_callback
        self._server_select = select_server

        super().__init__(self._wipe_day_select)

    @property
    def selected_wipe_day(self) -> WeekDay:
        value = self._wipe_day_select.values[0]
        return WeekDay(int(value))

    @property
    def filtered_servers(self) -> list[CombinedServerData]:
        return [server for server in self.servers if server.wipeday == self.selected_wipe_day]

    @property
    def selected_server(self) -> CombinedServerData:
        for server in self.servers:
            if server.title == self._server_select.values[0]:
                return server

    async def _select_server_wipe_day_callback(self, interaction: Interaction):
        self._server_select.options = [
            discord.SelectOption(
                label=server.title,
            )
            for server in self.filtered_servers
        ]
        if len(self.children) == 1:
            self.add_item(self._server_select)

        for option in self._wipe_day_select.options:
            if option.value == self._wipe_day_select.values[0]:
                option.default = True
            else:
                option.default = False

        await interaction.response.edit_message(files=[], attachments=[], view=self)

    async def _select_server_callback(self, interaction: Interaction):
        modal = self.modal_to_send(locale=self.locale, server=self.selected_server)
        await interaction.response.send_modal(modal)
        await interaction.delete_original_response()


class CheaterServerSelectView(BaseServerSelectView):
    modal_to_send = CheaterReportModal


class LimitServerSelectView(BaseServerSelectView):
    modal_to_send = LimitReportModal
