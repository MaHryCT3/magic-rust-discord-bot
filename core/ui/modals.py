import discord

from core.localization import LocaleEnum


class InputText(discord.ui.InputText):
    def __init__(self, *args, **kwargs):
        # Label kwarg required. Not handy on init with localization
        kwargs.setdefault('label', ' ')
        super().__init__(*args, **kwargs)

    def __set_name__(self, owner: 'BaseModal', name: str):
        self.owner = owner

        if not hasattr(owner, 'inputs'):
            owner.inputs = []
        else:
            owner.inputs = owner.inputs.copy()
        self.input_position = len(owner.inputs)
        owner.inputs.append(self)

    def __get__(self, instance: 'BaseModal', owner) -> str:
        return instance.children[self.input_position].value

    def __set__(self, instance: 'BaseModal', value):
        instance.children[self.input_position]._input_value = value


class BaseModal(discord.ui.Modal):
    inputs: list[InputText]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for input in self.inputs:
            self.add_item(input)


class BaseLocalizationModal(BaseModal):
    inputs_localization_map: dict[InputText, dict[LocaleEnum, dict]]
    title_localization_map: dict[LocaleEnum, str]

    def __init__(self, *args, locale: LocaleEnum, **kwargs):
        assert hasattr(
            self, 'inputs_localization_map'
        ), 'Used "BaseLocalizationModal", bust inputs_localization_map param skipped'
        self.locale = locale

        for input in self.inputs:
            input_translations = self.inputs_localization_map.get(input, {})
            locale_translations = input_translations.get(locale)
            if not locale_translations:
                continue

            for key, value in locale_translations.items():
                setattr(input, key, value)

        if hasattr(self, 'title_localization_map'):
            kwargs.setdefault('title', self.title_localization_map.get(self.locale))

        super().__init__(*args, **kwargs)
