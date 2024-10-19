from typing import Self

import discord
from discord import Interaction

from bot.apps.tickets.actions.create_ticket import CreateTicketAction
from bot.apps.tickets.errors import TicketError
from core.emojis import Emojis
from core.localization import LocaleEnum, LocalizationDict
from core.ui.modals import BaseLocalizationModal, InputText


class MakeTicketView(discord.ui.View):
    report_button_localization = LocalizationDict(
        {
            LocaleEnum.ru: 'Создать обращение',
            LocaleEnum.en: 'Create ticket',
        }
    )

    def __init__(self, locale: LocaleEnum):
        self.locale = locale

        make_report_button = discord.ui.Button(
            label=self.report_button_localization[self.locale],
            emoji=Emojis.TICKET,
            custom_id=f'ticket:{self.locale}:button:make',
        )
        make_report_button.callback = self.make_report_button_callback

        super().__init__(make_report_button, timeout=None)

    async def make_report_button_callback(self, interaction: discord.Interaction):
        modal = MakeTicketModal(locale=self.locale)
        await interaction.response.send_modal(modal)

    @classmethod
    def all_locales_init(cls) -> list[Self]:
        return [cls(locale=locale) for locale in LocaleEnum]


class MakeTicketModal(BaseLocalizationModal):
    title_localization_map = {
        LocaleEnum.ru: 'Создания обращения',
        LocaleEnum.en: 'Create ticket',
    }

    user_steam_input = InputText(
        min_length=17,
        max_length=100,
        placeholder='https://steamcommunity.com/profiles/76561199999999999',
    )
    description_input = InputText(
        style=discord.InputTextStyle.long,
        max_length=1024,
    )

    inputs_localization_map = {
        user_steam_input: {
            LocaleEnum.ru: dict(label='Ссылка на Ваш steam или steamid'),
            LocaleEnum.en: dict(label='Link to your steam or steamid'),
        },
        description_input: {
            LocaleEnum.ru: dict(label='Опишите ситуацию'),
            LocaleEnum.en: dict(label='Describe the situation'),
        },
    }

    created_channel_message_localization = {
        LocaleEnum.ru: 'Обращение создано: {channel_mention}',
        LocaleEnum.en: 'Ticket created: {channel_mention}',
    }

    async def callback(self, interaction: Interaction):
        channel = await CreateTicketAction(
            locale=self.locale,
            guild=interaction.guild,
            member=interaction.user,
            user_steam=self.user_steam_input,
            description=self.description_input,
        ).execute()

        message = self.created_channel_message_localization[self.locale].format(
            channel_mention=channel.mention,
        )
        await interaction.respond(message, ephemeral=True)

    async def on_error(self, error: TicketError, interaction: Interaction) -> None:
        if isinstance(error, TicketError):
            return await interaction.respond(error.message, ephemeral=True)
        raise error
