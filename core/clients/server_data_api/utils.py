import sys

from core.clients.server_data_api.models import MonitoringServerData


def sort_monitoring_server_data_by_server_number(servers_data: list[MonitoringServerData]):
    def sort_key_getter(data: MonitoringServerData):
        try:
            title_number = data.title[3:5].strip()
        except IndexError:
            return sys.maxsize

        try:
            return int(title_number)
        except ValueError:
            return sys.maxsize

    servers_data.sort(key=sort_key_getter)
