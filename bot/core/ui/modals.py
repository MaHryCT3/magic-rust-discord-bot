import discord

from bot.core.localization import LocaleEnum


class InputText(discord.ui.InputText):
    def __set_name__(self, owner: 'BaseModal', name: str):
        if not hasattr(owner, 'inputs'):
            owner.inputs = []
        self.input_position = len(owner.inputs)
        owner.inputs.append(self)

    def __get__(self, instance: 'BaseModal', owner):
        return instance.children[self.input_position].value


class BaseModal(discord.ui.Modal):
    inputs: list[InputText]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for input in self.inputs:
            self.add_item(input)


class BaseLocalizationModal(BaseModal):
    localization_map: dict[InputText, dict[LocaleEnum, dict]]

    def __init__(self, *args, locale: LocaleEnum, **kwargs):
        assert hasattr(self, 'localization_map'), 'Used "BaseLocalizationModal", bust localization_map param skipped'
        self.locale = locale

        for input in self.inputs:
            input_translations = self.localization_map.get(input, {})
            locale_translations = input_translations.get(locale)
            if not locale_translations:
                continue

            for key, value in locale_translations.items():
                setattr(input, key, value)

        super().__init__(*args, **kwargs)
