from abc import ABC, abstractmethod


class AbstractAction(ABC):
    async def validate(self):  # noqa: B027
        pass

    @abstractmethod
    async def action(self):
        pass

    async def execute(self):
        await self.validate()
        await self.action()
