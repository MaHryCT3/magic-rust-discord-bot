from abc import ABC, abstractmethod
from typing import Generic, TypeVar

ActionReturn = TypeVar('ActionReturn')


class AbstractAction(ABC, Generic[ActionReturn]):
    async def validate(self):  # noqa: B027
        pass

    @abstractmethod
    async def action(self):
        pass

    async def execute(self) -> ActionReturn:
        await self.validate()
        return await self.action()
