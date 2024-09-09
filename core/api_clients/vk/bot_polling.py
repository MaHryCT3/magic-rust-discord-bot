from enum import StrEnum
from logging import getLogger

from core.api_clients.vk.api import VKAPIClient
from core.api_clients.vk.models import LongPollServer, WallPost
from core.api_clients.vk.models.base import BaseUpdateEvent
from core.clients.http import HTTPClient

logger = getLogger()


class UpdateTypes(StrEnum):
    WALL_POST_NEW = 'wall_post_new'


update_type_to_model_mapper: dict[UpdateTypes, type[BaseUpdateEvent]] = {
    UpdateTypes.WALL_POST_NEW: WallPost,
}


class BotPolling:
    def __init__(
        self,
        api: VKAPIClient,
        group_id: int,
        server: LongPollServer | None = None,
        wait: int = 20,
        http_client: HTTPClient | None = None,
    ):
        self.api = api
        self.group_id = group_id
        self.server = server
        self.wait = wait

        self.http_client = http_client or HTTPClient()

    async def get_new_events(
        self,
        update_types: list[UpdateTypes] | None = None,
        ts: int | None = None,
        parse_response: bool = False,
    ) -> list[dict] | list[BaseUpdateEvent] | None:
        """
        Возвращает новые евенты с сервера, для этого после запроса сдвигается номер последнего поста.
        Можно указать update_types, чтобы ожидать только определнный тип событий
        """
        if not self.server:
            self.server = await self.api.get_long_poll_server(self.group_id)

        logger.debug(f'Making long poll request... ts={self.server.ts}')
        events_response = await self.http_client.post(
            url=self.server.server,
            query={
                'act': 'a_check',
                'key': self.server.key,
                'ts': ts or self.server.ts,
                'wait': self.wait,
            },
        )
        events = events_response.json()

        # если нет 'ts', то скорее всего нужно обновить лонгпулл сервер, взято с
        # https://github.com/vkbottle/vkbottle/blob/master/vkbottle/polling/bot_polling.py
        if 'ts' not in events:
            logger.info('Long poll server reset')

            self.server = None
            return await self.get_new_events(update_types=update_types, ts=ts, parse_response=parse_response)

        if not events:
            logger.debug('No updates')
            return None

        logger.info(f'New vk updates: {events}')
        # Обновляем номер последнего события
        self.server.ts = events['ts']

        updates = events['updates']
        if update_types:
            updates = [update for update in updates if update['type'] in update_types]
        if parse_response:
            updates = [self._parse_response(update) for update in updates if self._is_available_to_parse(update)]

        return updates

    @staticmethod
    def _parse_response(update: dict) -> BaseUpdateEvent | None:
        update_type = UpdateTypes(update['type'])
        object_data = update['object']

        model = update_type_to_model_mapper[update_type]
        return model(**object_data | {'group_id': update['group_id']})

    @staticmethod
    def _is_available_to_parse(update: dict) -> bool:
        if update['type'] in list(update_type_to_model_mapper.keys()):
            return True

        logger.warning(f'Received update, that is not supported yet. type={update["type"]}')
        return False
