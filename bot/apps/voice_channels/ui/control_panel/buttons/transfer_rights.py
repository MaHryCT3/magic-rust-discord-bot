import discord

from bot.apps.voice_channels.actions import TransferRightsAction
from bot.apps.voice_channels.ui.control_panel.permissions import check_panel_access
from core.localization import LocaleEnum, LocalizationDict


class TransferRightsButton(discord.ui.Button):
    label_localization = {
        LocaleEnum.en: ' Transfer rights',
        LocaleEnum.ru: ' Передать права',
    }

    no_user_to_transfer_rights_localization = {
        LocaleEnum.ru: 'Нет пользователей для передачи прав',
        LocaleEnum.en: 'No user to transfer rights',
    }

    embed_title_localization = LocalizationDict(
        {
            LocaleEnum.en: 'Transfer channel rights',
            LocaleEnum.ru: 'Передать права на канал',
        }
    )
    embed_description_localization = LocalizationDict(
        {
            LocaleEnum.en: 'Choose a member from the list below to transfer administrator rights',
            LocaleEnum.ru: 'Выберите участника из списка ниже, чтобы передать права администратора',
        }
    )

    def __init__(self, locale: LocaleEnum, voice_channel: discord.VoiceChannel):
        self.locale = locale
        self.voice_channel = voice_channel
        super().__init__(
            style=discord.ButtonStyle.primary,
            custom_id=f'control-panel:{voice_channel.id}:button:transfer-rights',
            # emoji=Emojis.DIZZY,  # TODO: Waiting emoji
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
                self.no_user_to_transfer_rights_localization[self.locale],
                ephemeral=True,
                delete_after=10,
            )
        await interaction.response.send_message(
            view=TransferRightsView(
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


class TransferRightsView(discord.ui.View):
    placeholder_localization = {
        LocaleEnum.ru: 'Передать права на канал',
        LocaleEnum.en: 'Transfer the rights to the channel',
    }
    succeed_localization = {
        LocaleEnum.ru: 'Вы передали права {member_mention}',
        LocaleEnum.en: 'You transferred the rights to {member_mention}',
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

        self.member_transfer_rights_select = discord.ui.Select(
            placeholder=self.placeholder_localization[self.locale],
            options=[
                discord.SelectOption(
                    label=member.display_name,
                    value=str(member.id),
                )
                for member in members
            ],
        )
        self.member_transfer_rights_select.callback = self._member_kick_select_callback

        super().__init__(self.member_transfer_rights_select, timeout=None)

    async def _member_kick_select_callback(self, interaction: discord.Interaction) -> None:
        await TransferRightsAction(
            self.voice_channel,
            self.selected_member,
            interaction.user,
        ).execute()
        await interaction.respond(
            self.succeed_localization[self.locale].format(member_mention=self.selected_member.mention),
            ephemeral=True,
            delete_after=15,
        )

    @property
    def selected_member(self) -> discord.Member:
        assert self.member_transfer_rights_select.values, 'метод использован некорректно'
        member_id = int(self.member_transfer_rights_select.values[0])
        for member in self.members:
            if member.id == member_id:
                return member
        raise AssertionError('метод использован некорректно')
