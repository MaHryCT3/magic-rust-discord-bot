import asyncio

from core.clients.http import HTTPClient
from core.clients.server_data_api.models import (
    CombinedServerData,
    FullServerData,
    MonitoringServerData,
)

SERVER_LASTUPDATE_TRESHOLD = 45


class MagicRustServerDataAPI:
    def __init__(self, http_client: HTTPClient | None = None):
        self.http_client = http_client or HTTPClient(base_url='https://vk.magicrust.ru/')

    async def get_monitoring_servers_data(self) -> list[MonitoringServerData]:
        servers_data = await self.http_client.get('api/getShopOnline.php')
        response_json = await servers_data.json()
        return [
            MonitoringServerData(**server_data)
            for server_data in response_json
            if self._is_monitoring_server_data_valid(server_data)
        ]

    async def get_full_servers_data(self) -> list[FullServerData]:
        servers_data = await self.http_client.get('api/getOnline', headers={'Content-Type': 'text/html'})
        response_json: dict = await servers_data.json(content_type='text/html')
        return [
            FullServerData(**server_data)
            for server_data in response_json.values()
            if self._is_full_server_data_valid(server_data)
        ]

    async def get_combined_servers_data(self) -> list[CombinedServerData]:
        monitoring_servers_data_task = asyncio.create_task(self.get_monitoring_servers_data())
        full_servers_data_task = asyncio.create_task(self.get_full_servers_data())

        await monitoring_servers_data_task
        await full_servers_data_task

        monitoring_servers_data = monitoring_servers_data_task.result()
        full_servers_data = full_servers_data_task.result()

        combined_servers_data: list[CombinedServerData] = []
        for monitoring_server_data in monitoring_servers_data:
            for full_server_data in full_servers_data:
                if monitoring_server_data.ip == full_server_data.ip:
                    combined_servers_data.append(CombinedServerData.combine(monitoring_server_data, full_server_data))
                    break

        return combined_servers_data

    @staticmethod
    def _is_full_server_data_valid(server_data: dict) -> bool:
        gm = server_data.get('gm')
        return server_data['lastupdate'] <= SERVER_LASTUPDATE_TRESHOLD and gm and gm != 'test'

    @staticmethod
    def _is_monitoring_server_data_valid(server_data: dict) -> bool:
        return server_data.get('ip') is not None
