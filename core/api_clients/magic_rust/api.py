from aiocache import cached

from core.api_clients.magic_rust.models import (
    CombinedServerData,
    FullServerData,
    MonitoringServerData,
)
from core.clients.http import HTTPClient

SERVER_LASTUPDATE_TRESHOLD = 45
API_GET_REQUEST_CACHE_TIME = 15


class MagicRustServerDataAPI:
    def __init__(self, http_client: HTTPClient | None = None):
        self.http_client = http_client or HTTPClient(base_url='https://vk.magicrust.ru/')

    async def get_monitoring_servers_data(self) -> list[MonitoringServerData]:
        servers_data = await self.http_client.get('api/getShopOnline.php')
        response_json = servers_data.json()
        return [
            MonitoringServerData(**server_data)
            for server_data in response_json
            if self._is_monitoring_server_data_valid(server_data)
        ]

    @cached(ttl=API_GET_REQUEST_CACHE_TIME)
    async def get_full_servers_data(self) -> list[FullServerData]:
        servers_data = await self.http_client.get('api/getOnline', headers={'Content-Type': 'text/html'})
        response_json: dict = servers_data.json()
        return [
            FullServerData(**server_data)
            for server_data in response_json.values()
            if self._is_full_server_data_valid(server_data)
        ]

    async def get_combined_servers_data(self) -> list[CombinedServerData]:
        monitoring_servers_data = await self.get_monitoring_servers_data()
        full_servers_data = await self.get_full_servers_data()

        monitoring_servers_data_dict = {server_data.ip: server_data for server_data in monitoring_servers_data}
        combined_servers_data: list[CombinedServerData] = []
        for full_server_data in full_servers_data:
            if full_server_data.ip in monitoring_servers_data_dict:
                combined_servers_data.append(
                    CombinedServerData.combine(monitoring_servers_data_dict[full_server_data.ip], full_server_data)
                )

        return combined_servers_data

    @staticmethod
    def _is_full_server_data_valid(server_data: dict) -> bool:
        gm = server_data.get('gm')
        return (server_data['lastupdate'] <= SERVER_LASTUPDATE_TRESHOLD) and gm and gm != 'test'

    @staticmethod
    def _is_monitoring_server_data_valid(server_data: dict) -> bool:
        return server_data.get('ip') is not None
