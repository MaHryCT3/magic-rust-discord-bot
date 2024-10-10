from logging import getLogger

from core.api_clients.vk.models import LongPollServer
from core.clients.http import HTTPClient

logger = getLogger()


class VKAPIClient:
    def __init__(self, token: str, api_version: str = '5.199', http_client: HTTPClient | None = None):
        self.token = token
        self.api_version = api_version
        self.http_client = http_client or HTTPClient(
            base_url='https://api.vk.com/method/',
            headers={'Authorization': f'Bearer {token}'},
        )

        self.default_payload = {'v': self.api_version}

    async def send_message(
        self,
        message: str,
        random_id: int,
        user_id: int | None = None,
        peer_id: int | None = None,
    ):
        assert not (user_id and peer_id), 'Нельзя использовать user_id и peer_id одновременно'
        payload = {
            'message': message,
            'random_id': random_id,
        }
        if user_id:
            payload['user_id'] = user_id
        if peer_id:
            payload['peer_id'] = peer_id

        await self.call_method('messages.send', payload=payload)

    async def get_long_poll_server(self, group_id: int) -> LongPollServer:
        payload = {'group_id': group_id}
        data = await self.call_method('groups.getLongPollServer', payload=payload)
        print(data)
        return LongPollServer(**data['response'])

    async def call_method(self, method_name: str, payload: dict) -> dict:
        payload = payload | self.default_payload
        response = await self.http_client.post(url=method_name, payload=payload)
        return response.json()
