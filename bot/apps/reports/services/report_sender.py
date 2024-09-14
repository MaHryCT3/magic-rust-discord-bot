from enum import StrEnum

from bot.config import settings
from core.api_clients.vk import VKAPIClient


class ChatTypes(StrEnum):
    OFFICIAL = 'official'
    MODDED = 'modded'
    LIMIT = 'limit'


class ReportVKSender:
    peer_id_by_chat_type: dict[ChatTypes, int] = {
        ChatTypes.MODDED: 2000000001,
        ChatTypes.LIMIT: 2000000002,
        ChatTypes.OFFICIAL: 2000000003,
    }

    def __init__(self):
        self.vk_api = VKAPIClient(settings.REPORT_VK_BOT_TOKEN)

    async def send_message(self, chat_type: ChatTypes, message: str):
        chat_peer_id = self.peer_id_by_chat_type[chat_type]
        await self.vk_api.send_message(
            message=message,
            peer_id=chat_peer_id,
            random_id=0,
        )
