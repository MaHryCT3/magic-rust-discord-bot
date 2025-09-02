from abc import ABC, abstractmethod
from typing import Final

import discord


class BaseAutocomplete(ABC):
    SUGGESTION_COUNT: Final[int] = 10

    def __call__(self, ctx: discord.AutocompleteContext) -> list[str]:
        try:
            return self.autocomplete(ctx)
        except Exception:
            return []

    @abstractmethod
    def autocomplete(self, ctx: discord.AutocompleteContext) -> list[str]: ...
