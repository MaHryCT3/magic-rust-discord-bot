from typing import TYPE_CHECKING
import discord

from core.clients.server_data_api.models import LIMIT_LABELS
from core.localization import LocaleEnum
from core.utils.date_time import day_num_to_name

if TYPE_CHECKING:
    from bot.apps.image_updater.views import ServerFilterView


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
    placeholder_localization = {
        LocaleEnum.ru: 'Режим',
        LocaleEnum.en: 'Game mode'
    }
    @classmethod
    def build(cls, filter_view: 'ServerFilterView'):
        return cls(filter_view, placeholder=cls.placeholder_localization[filter_view.locale], custom_id=f'server_filter:select:gm', options=[discord.SelectOption(label='-', value='None'),
                                                                                                       discord.SelectOption(label='vanilla'),
                                                                                                       discord.SelectOption(label='vanillax2'),
                                                                                                       discord.SelectOption(label='modded')])
    
    def value_changed(self, value: str | None):
        self.filter_view.gm = value
    

class LimitSelect(BaseFilterSelect):
    placeholder_localization = {
        LocaleEnum.ru: 'Лимит игроков',
        LocaleEnum.en: 'Player limit'
    }
    @classmethod
    def build(cls, filter_view: 'ServerFilterView'):
        return cls(filter_view, placeholder=cls.placeholder_localization[filter_view.locale], custom_id=f'server_filter:select:limit', options=[discord.SelectOption(label='-', value='None'),
                                                                                  discord.SelectOption(label=LIMIT_LABELS[1], value='1'),
                                                                                  discord.SelectOption(label=LIMIT_LABELS[2], value='2'), 
                                                                                  discord.SelectOption(label=LIMIT_LABELS[3], value='3'),
                                                                                  discord.SelectOption(label=LIMIT_LABELS[0], value='0')])
    
    def value_changed(self, value: str | None):
        self.filter_view.limit = int(value) if value else None 
    

class WipeDaySelect(BaseFilterSelect):
    placeholder_localization = {
        LocaleEnum.ru: 'День вайпа',
        LocaleEnum.en: 'Wipe day'
    }
    @classmethod
    def build(cls, filter_view: 'ServerFilterView'):
        return cls(filter_view, placeholder=cls.placeholder_localization[filter_view.locale], custom_id=f'server_filter:select:wipeday', options=[discord.SelectOption(label='-', value='None'),
                                                                                  discord.SelectOption(label=day_num_to_name(1, filter_view.locale), value='1'),
                                                                                  discord.SelectOption(label=day_num_to_name(4, filter_view.locale), value='4'), 
                                                                                  discord.SelectOption(label=day_num_to_name(5, filter_view.locale), value='5')])
    
    def value_changed(self, value: str | None):
        self.filter_view.wipeday = int(value) if value else None

class MapSelect(BaseFilterSelect):
    placeholder_localization = {
        LocaleEnum.ru: 'Карта',
        LocaleEnum.en: 'Map'
    }
    @classmethod
    def build(cls, filter_view: 'ServerFilterView'):
        return cls(filter_view, placeholder=cls.placeholder_localization[filter_view.locale], custom_id=f'server_filter:select:map', options=[discord.SelectOption(label='-', value='None'),
                                                                                  discord.SelectOption(label='Procedural Plus'),
                                                                                  discord.SelectOption(label='Barren Plus')])
    
    def value_changed(self, value: str | None):
        self.filter_view.map = value