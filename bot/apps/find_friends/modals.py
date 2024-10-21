from discord import InputTextStyle, Interaction, TextChannel

from bot.apps.find_friends.cooldowns import find_friend_cooldown
from bot.dynamic_settings import dynamic_settings
from core.localization import LocaleEnum, LocalizationDict
from core.ui.modals import BaseLocalizationModal, InputText
from core.utils.regex import remove_url_from_text

from .embeds import FindFriendEmbed
from .exceptions import CommandNotConfiguredError


class FindFriendModal(BaseLocalizationModal):
    title_localization = LocalizationDict(
        {
            LocaleEnum.en: 'Find a friend!',
            LocaleEnum.ru: 'Найди друга!',
        }
    )
    response_localization = LocalizationDict(
        {
            LocaleEnum.en: "You've successfully sent a find friend request.",
            LocaleEnum.ru: 'Вы успешно отправили заявку на поиск друга.',
        }
    )
    url_in_response_localization = LocalizationDict(
        {
            LocaleEnum.en: 'Links have been removed from the form. You should not use them from now on.',
            LocaleEnum.ru: 'Из формы были удалены ссылки. Впредь не стоит их использовать.',
        }
    )

    article_input = InputText(
        max_length=50,
    )
    message_input = InputText(
        max_length=1024,
        style=InputTextStyle.multiline,
    )
    server_input = InputText(
        max_length=50,
    )

    inputs_localization_map = {
        article_input: {
            LocaleEnum.ru: dict(
                label='Заголовок',
                placeholder='Ищу команду, напарника/Проводим набор в клан',
            ),
            LocaleEnum.en: dict(
                label='Article',
                placeholder='Searching for a team, teammate/Recruiting clan members',
            ),
        },
        message_input: {
            LocaleEnum.ru: dict(
                label='Сообщение',
                placeholder='Мне 19 лет, адекват, 500 часов.\nили\nФорма заявки:...',
            ),
            LocaleEnum.en: dict(
                label='Message',
                placeholder='19 y.o., adequate, 500 hours. \nor\nApplication form:...',
            ),
        },
        server_input: {
            LocaleEnum.ru: dict(
                label='Номера серверов',
                placeholder='Обязательно укажите номер(а) сервера(-ов) MR',
            ),
            LocaleEnum.en: dict(
                label='Servers',
                placeholder='Required! Specify number(s) of MR server(s)',
            ),
        },
    }

    def __init__(self, locale: LocaleEnum):
        title = self.title_localization[locale]
        super().__init__(title=title, locale=locale)
        self.locale = locale

    async def callback(self, interaction: Interaction):
        if await find_friend_cooldown.is_user_on_cooldown(
            interaction.user.id,
            self.locale,
            cooldown_in_seconds=dynamic_settings.find_friend_cooldown,
        ):
            raise

        is_have_urls = self._clear_url_from_inputs()

        embed = FindFriendEmbed.build(
            interaction.user.display_name,
            getattr(interaction.user.display_avatar, 'url', None),
            self.article_input,
            self.message_input,
            self.server_input,
            locale=self.locale,
        )
        find_friends_channel: TextChannel = interaction.guild.get_channel(
            dynamic_settings.find_friend_channels[self.locale]
        )
        if not find_friends_channel:
            raise CommandNotConfiguredError(self.locale)

        await find_friends_channel.send(content=interaction.user.mention, embed=embed)
        await interaction.response.send_message(content=self._get_respond_message(is_have_urls), ephemeral=True)
        await find_friend_cooldown.set_user_cooldown(
            user_id=interaction.user.id,
            locale=self.locale,
            cooldown_in_seconds=dynamic_settings.find_friend_cooldown,
        )

    def _clear_url_from_inputs(self) -> bool:
        is_have_urls = False
        for attr in ['article_input', 'message_input', 'server_input']:
            attr_value = getattr(self, attr)
            len_before_clear = len(attr_value)
            cleared_text = remove_url_from_text(attr_value)
            if len(cleared_text) < len_before_clear:
                is_have_urls = True
                setattr(self, attr, cleared_text)
        return is_have_urls

    def _get_respond_message(self, is_have_url: bool) -> str:
        text = self.response_localization[self.locale]
        if is_have_url:
            extra_text = self.url_in_response_localization[self.locale]
            text += f'\n{extra_text}'
        return text
