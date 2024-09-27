import sys

from core.api_clients.magic_rust.models import MonitoringServerData, ServerTypes


def sort_monitoring_server_data_by_server_number(servers_data: list[MonitoringServerData]):
    def sort_key_getter(data: MonitoringServerData) -> int:
        if data.server_type == ServerTypes.OFFICIAL:
            return -1
        try:
            title_number = data.title[3:5].strip()
        except IndexError:
            return sys.maxsize

        try:
            return int(title_number)
        except ValueError:
            return sys.maxsize

    servers_data.sort(key=sort_key_getter)


def is_title_contain_limit_signs(server_title: str) -> bool:
    for sign in ['max ', 'solo']:
        if sign in server_title.lower():
            return True
    return False


def filter_monitoring_server_data_by_servers_with_limit(
    servers_data: list[MonitoringServerData],
) -> list[MonitoringServerData]:
    return [server_data for server_data in servers_data if is_title_contain_limit_signs(server_data.title)]


def get_only_server_name_from_title(server_title: str) -> str:
    first_bracket = server_title.find('[')
    if first_bracket != -1:
        return server_title[:first_bracket].strip()
    return server_title
