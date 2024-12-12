import discord

from bot.apps.voice_channels.actions import KickMemberAction
from bot.apps.voice_channels.ui.control_panel.permissions import check_panel_access
from core.emojis import Emojis
from core.localization import LocaleEnum, LocalizationDict


class KickButton(discord.ui.Button):
    label_localization = {
        LocaleEnum.en: ' Kick',
        LocaleEnum.ru: ' Выгнать',
    }

    no_user_to_kick_localization = {
        LocaleEnum.ru: 'Нет пользователей для кика',
        LocaleEnum.en: 'No user to kick',
    }

    embed_title_localization = LocalizationDict(
        {
            LocaleEnum.en: 'Kick channel member',
            LocaleEnum.ru: 'Выгнать участника канала',
        }
    )
    embed_description_localization = LocalizationDict(
        {
            LocaleEnum.en: "Choose a member from the list below. He won't be able to connect to this channel again.",
            LocaleEnum.ru: 'Выберите участника из списка ниже. Он больше не сможет зайти в этот канал снова.',
        }
    )

    def __init__(self, locale: LocaleEnum, voice_channel: discord.VoiceChannel):
        self.locale = locale
        self.voice_channel = voice_channel
        super().__init__(
            style=discord.ButtonStyle.primary,
            custom_id=f'control-panel:{voice_channel.id}:button:kick',
            emoji=Emojis.DIZZY,
            label=self.label_localization[locale],
        )

    async def callback(self, interaction: discord.Interaction):
        await check_panel_access(self.voice_channel, interaction.user)

        members = (await interaction.guild.fetch_channel(self.voice_channel.id)).members
        members_except_managers = [
            member for member in members if not self.voice_channel.permissions_for(member).manage_channels
        ]
        if not members_except_managers:
            return await interaction.respond(
                self.no_user_to_kick_localization[self.locale],
                ephemeral=True,
                delete_after=10,
            )
        await interaction.response.send_message(
            view=KickView(
                locale=self.locale,
                members=members_except_managers,
                voice_channel=self.voice_channel,
            ),
            embed=self.get_embed(),
            ephemeral=True,
            delete_after=20,
        )

    def get_embed(
        self,
    ):
        embed = discord.Embed(
            title=self.embed_title_localization[self.locale],
        )
        embed.add_field(
            name='',
            value=self.embed_description_localization[self.locale],
            inline=False,
        )
        return embed


class KickView(discord.ui.View):
    placeholder_localization = {
        LocaleEnum.ru: 'Выгнать участника',
        LocaleEnum.en: 'Kick member',
    }
    kick_succeed_localization = {
        LocaleEnum.ru: 'Вы выгнали `{kicked_member}`',
        LocaleEnum.en: 'Member `{kicked_member}` was kicked',
    }

    def __init__(
        self,
        locale: LocaleEnum,
        members: list[discord.Member],
        voice_channel: discord.VoiceChannel,
    ):
        self.locale = locale
        self.members = members
        self.voice_channel = voice_channel

        self.member_kick_select = discord.ui.Select(
            placeholder=self.placeholder_localization[self.locale],
            options=[
                discord.SelectOption(
                    label=member.display_name,
                    value=str(member.id),
                )
                for member in members
            ],
        )
        self.member_kick_select.callback = self._member_kick_select_callback

        super().__init__(self.member_kick_select, timeout=None)

    async def _member_kick_select_callback(self, interaction: discord.Interaction) -> None:
        await KickMemberAction(self.voice_channel, self.selected_member).execute()
        await interaction.respond(
            self.kick_succeed_localization[self.locale].format(
                kicked_member=self.selected_member.mention,
            ),
            ephemeral=True,
            delete_after=15,
        )

    @property
    def selected_member(self) -> discord.Member:
        assert self.member_kick_select.values, 'метод использован некорректно'
        member_id = int(self.member_kick_select.values[0])
        for member in self.members:
            if member.id == member_id:
                return member
        raise AssertionError('метод использован некорректно')
