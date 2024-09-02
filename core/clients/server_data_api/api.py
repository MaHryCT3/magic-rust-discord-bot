import asyncio

from aiocache import cached

from core.clients.http import HTTPClient
from core.clients.server_data_api.models import FullServerData, MonitoringServerData

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
        response_json = servers_data.json()
        return [
            FullServerData(**server_data)
            for server_data in response_json
            if self._is_full_server_data_valid(server_data)
        ]

    def get_full_servers_data_sync(self) -> list[FullServerData]:
        return asyncio.run(self.get_full_servers_data_sync())

    @staticmethod
    def _is_full_server_data_valid(server_data: dict) -> bool:
        return server_data['lastupdate'] <= SERVER_LASTUPDATE_TRESHOLD and server_data.get('gm', None) != 'test'

    @staticmethod
    def _is_monitoring_server_data_valid(server_data: dict) -> bool:
        return server_data.get('ip') is not None
