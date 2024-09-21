from discord import InputTextStyle, Interaction, TextChannel

from bot.dynamic_settings import dynamic_settings
from core.localization import LocaleEnum, LocalizationDict
from core.redis_cooldown import RedisLocaleCooldown
from core.ui.modals import BaseLocalizationModal, InputText

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
            LocaleEnum.en: "You've successfully sent a find freind request.",
            LocaleEnum.ru: 'Вы успешно отправили заявку на поиск друга.',
        }
    )
    article_input = InputText(
        max_length=50,
    )
    message_input = InputText(
        max_length=1024,
        style=InputTextStyle.multiline,
    )
    server_input = InputText()

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

    def __init__(self, locale: LocaleEnum, redis_cooldown: RedisLocaleCooldown):
        title = self.title_localization[locale]
        super().__init__(title=title, locale=locale)
        self.locale = locale
        self.redis_cooldown = redis_cooldown

    async def callback(self, interaction: Interaction):
        if await self.redis_cooldown.is_user_on_cooldown(interaction.user.id, self.locale):
            raise

        embed = FindFriendEmbed.build(
            interaction.user.display_name,
            interaction.user.display_avatar.url,
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
        await interaction.response.send_message(content=self.response_localization[self.locale], ephemeral=True)
        await self.redis_cooldown.set_user_cooldown(
            user_id=interaction.user.id,
            locale=self.locale,
            cooldown_in_seconds=dynamic_settings.find_friend_cooldown,
        )
