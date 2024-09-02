from abc import ABC, abstractmethod

from bot.apps.news_reposts.services.captures.structs import CapturedNews


class AbstractNewsCapture(ABC):
    @abstractmethod
    async def get_captured_news(self) -> list[CapturedNews]: ...
