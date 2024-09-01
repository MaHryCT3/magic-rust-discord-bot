from typing import Any, Callable, Coroutine, TYPE_CHECKING
import discord

from core.clients.server_data_api import LIMIT_LABELS

if TYPE_CHECKING:
    from bot.apps.server_filter.views import ServerFilterView


class BaseFilterSelect(discord.ui.Select):
    def __init__(self, filter_view: 'ServerFilterView', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filter_view = filter_view
    
    def value_changed(self, value: str | None):
        pass

    async def callback(self, interaction: discord.Interaction):
        self.value_changed(self.values[0] if not self.values[0] == 'None' else None)
        for option in self.options:
            option.default = False
            if option.value == self.values[0] and not self.values[0] == 'None':
                option.default = True
        await self.filter_view.update(interaction)
        return await super().callback(interaction)

class GameModeSelect(BaseFilterSelect):
    @classmethod
    def build(cls, filter_view: 'ServerFilterView'):
        return cls(filter_view, placeholder='Game mode', custom_id=f'server_filter:select:gm', options=[discord.SelectOption(label='-', value='None'),
                                                                                                       discord.SelectOption(label='vanilla'),
                                                                                                       discord.SelectOption(label='vanillax2'),
                                                                                                       discord.SelectOption(label='modded')])
    
    def value_changed(self, value: str | None):
        self.filter_view.gm = value
    

class LimitSelect(BaseFilterSelect):
    @classmethod
    def build(cls, filter_view: 'ServerFilterView'):
        return cls(filter_view, placeholder='Player limit', custom_id=f'server_filter:select:limit', options=[discord.SelectOption(label='-', value='None'),
                                                                                  discord.SelectOption(label=LIMIT_LABELS[1], value='1'),
                                                                                  discord.SelectOption(label=LIMIT_LABELS[2], value='2'), 
                                                                                  discord.SelectOption(label=LIMIT_LABELS[3], value='3'),
                                                                                  discord.SelectOption(label=LIMIT_LABELS[0], value='0')])
    
    def value_changed(self, value: str | None):
        self.filter_view.limit = int(value) if value else None 
    

class WipeDaySelect(BaseFilterSelect):
    @classmethod
    def build(cls, filter_view: 'ServerFilterView'):
        return cls(filter_view, placeholder='Wipe day', custom_id=f'server_filter:select:wipeday', options=[discord.SelectOption(label='-', value='None'),
                                                                                  discord.SelectOption(label='Monday', value='1'),
                                                                                  discord.SelectOption(label='Thursday', value='4'), 
                                                                                  discord.SelectOption(label='Friday', value='5')])
    
    def value_changed(self, value: str | None):
        self.filter_view.wipeday = int(value) if value else None

class MapSelect(BaseFilterSelect):
    @classmethod
    def build(cls, filter_view: 'ServerFilterView'):
        return cls(filter_view, placeholder='Map', custom_id=f'server_filter:select:map', options=[discord.SelectOption(label='-', value='None'),
                                                                                  discord.SelectOption(label='Procedural Plus'),
                                                                                  discord.SelectOption(label='Barren Plus')])
    
    def value_changed(self, value: str | None):
        self.filter_view.map = value