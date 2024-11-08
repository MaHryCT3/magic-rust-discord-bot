import discord
from discord import Interaction

from bot.apps.reports.ui.modals import (
    BaseReportModal,
    CheaterReportModal,
    LimitReportModal,
)
from core.api_clients.magic_rust import (
    MonitoringServerData,
    filter_monitoring_server_data_by_servers_with_limit,
)
from core.localization import LocaleEnum, LocalizationDict


class ServersSelect(discord.ui.Select):
    placeholder_localization = LocalizationDict(
        {
            LocaleEnum.ru: 'Выберите сервер',
            LocaleEnum.en: 'Select server',
        },
    )

    def __init__(self, servers: list[MonitoringServerData], locale: LocaleEnum, modal_class: type[BaseReportModal]):
        self.servers = servers
        self.locale = locale
        self.modal_class = modal_class
        super().__init__(
            select_type=discord.ComponentType.string_select,
            options=self._get_report_servers(),
            placeholder=self.placeholder_localization[locale],
        )

    def _get_report_servers(self) -> list[discord.SelectOption]:
        return [
            discord.SelectOption(
                label=server.title,
            )
            for server in self.servers[:25]
        ]

    async def callback(self, interaction: Interaction):
        modal = self.modal_class(server=self.selected_server, locale=self.locale)
        await interaction.response.send_modal(modal)
        await interaction.delete_original_response()

    @property
    def selected_server(self) -> MonitoringServerData:
        selected_server_title = self.values[0]
        for server in self.servers:
            if selected_server_title == server.title:
                return server


class SelectCheaterReportServerView(discord.ui.View):
    def __init__(self, servers: list[MonitoringServerData], locale: LocaleEnum):
        super().__init__(ServersSelect(servers, locale, modal_class=CheaterReportModal))


class SelectLimitReportServerView(discord.ui.View):
    def __init__(self, servers: list[MonitoringServerData], locale: LocaleEnum):
        servers = filter_monitoring_server_data_by_servers_with_limit(servers)
        super().__init__(ServersSelect(servers, locale, modal_class=LimitReportModal))
