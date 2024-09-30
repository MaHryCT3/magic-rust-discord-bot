from typing import Self

import discord

from core.localization import LocaleEnum


class VoiceMemberSelect(discord.ui.Select):
    def __init__(self, *args, voice_channel: discord.VoiceChannel, **kwargs):
        self.voice_channel = voice_channel
        super().__init__(*args, **kwargs)

    def add_empty_option(self):
        self.add_option(label='-')

    async def on_member_chosen(self, interaction: discord.Interaction, member: discord.Member):
        pass

    async def callback(self, interaction: discord.Interaction):
        await self.on_member_chosen(interaction, interaction.guild.get_member(int(self.values[0])))
        return await super().callback(interaction)

    @classmethod
    def _get_member_options(cls, voice_members: list[discord.Member]) -> list[discord.SelectOption]:
        return [discord.SelectOption(label=member.display_name, value=str(member.id)) for member in voice_members]


class MemberKickSelect(VoiceMemberSelect):
    empty_placeholder_localization = {
        LocaleEnum.ru: 'Нет подходящих участников',
        LocaleEnum.en: 'No valid members',
    }
    placeholder_localization = {
        LocaleEnum.ru: 'Выгнать участника',
        LocaleEnum.en: 'Kick member',
    }
    kick_succeed_localization = {
        LocaleEnum.ru: 'Вы выгнали `{kicked_member}`',
        LocaleEnum.en: 'Member `{kicked_member}` was kicked',
    }

    def __init__(self, *args, locale: LocaleEnum, **kwargs):
        self.locale = locale
        super().__init__(*args, **kwargs)

    @classmethod
    def build(
        cls, locale: LocaleEnum, voice_members: list[discord.Member], voice_channel: discord.VoiceChannel
    ) -> Self:
        result = cls(
            locale=locale,
            voice_channel=voice_channel,
            placeholder=cls.placeholder_localization[locale],
            options=cls._get_member_options(voice_members),
        )
        if not voice_members:
            result.disabled = True
            result.add_empty_option()
            result.placeholder = cls.empty_placeholder_localization[locale]
        return result

    async def on_member_chosen(self, interaction: discord.Interaction, member: discord.Member):
        permissions = discord.PermissionOverwrite()
        permissions.connect = False
        await self.voice_channel.set_permissions(member, overwrite=permissions)
        await member.move_to(None)
        await interaction.response.send_message(
            content=self.kick_succeed_localization[self.locale].format(kicked_member=member.display_name),
            ephemeral=True,
            delete_after=10,
        )
