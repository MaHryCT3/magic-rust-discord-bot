from discord import Member, PermissionOverwrite, VoiceChannel, VoiceState
from discord.ext import commands

from bot.apps.voice_channels.constants import CREATE_VOICE_COOLDOWN_NAMESPACE
from bot.apps.voice_channels.embeds import RoomCreationCooldownEmbed
from bot.apps.voice_channels.exceptions import (
    CategoryNotConfiguredError,
    RoomCreateCooldownError,
)
from bot.bot import MagicRustBot
from bot.config import logger, settings
from bot.dynamic_settings import dynamic_settings
from core.localization import LocaleEnum, LocalizationDict
from core.redis_cooldown import RedisCooldown

CREATE_SERVER_UPDATE_SECONDS = 2.0


class RoomCreator(commands.Cog):
    room_name_localization = LocalizationDict(
        {
            LocaleEnum.en: 'Room {room_name}',
            LocaleEnum.ru: 'Комната {room_name}',
        },
    )

    def __init__(self, bot: MagicRustBot):
        self.bot = bot
        self.create_room_cooldown = RedisCooldown(settings.REDIS_URL, CREATE_VOICE_COOLDOWN_NAMESPACE)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, _before: VoiceState, after: VoiceState):
        if not after.channel:
            return
        for locale, channel_id in dynamic_settings.channel_creating_channels.items():
            if after.channel.id != channel_id:
                continue
            try:
                await self.create_room_for_user(member, dynamic_settings.user_room_create_cooldown, locale)
            except RoomCreateCooldownError as err:
                await member.move_to(None)
                await member.send(embed=RoomCreationCooldownEmbed.from_exception(err))
            except CategoryNotConfiguredError:
                await member.move_to(None)
                logger.error(f'Category for user voice rooms for locale {locale} not set!')
            break

    async def create_room_for_user(self, member: Member, cooldown: float, locale: LocaleEnum):
        if cooldown_residue := await self.create_room_cooldown.get_user_cooldown_residue(member.id, cooldown):
            raise RoomCreateCooldownError(cooldown=cooldown, retry_after=cooldown_residue, locale=locale)
        new_channel = await self.create_room(member.display_name, locale)
        await self.create_room_cooldown.set_user_cooldown(
            user_id=member.id,
            cooldown_in_seconds=cooldown,
        )
        await new_channel.set_permissions(
            member, manage_channels=True, move_members=True, set_voice_channel_status=True
        )
        await member.move_to(new_channel)

    async def create_room(self, room_name: str, locale: LocaleEnum) -> VoiceChannel:
        guild = self.bot.get_main_guild()
        category_id = dynamic_settings.user_rooms_categories.get(locale)
        category = self.bot.get_category(category_id)
        if not category:
            raise CategoryNotConfiguredError(locale)

        new_channel = await guild.create_voice_channel(
            name=self.room_name_localization[locale].format(room_name=room_name),
            category=category,
            overwrites={
                self._get_locale_role(locale): PermissionOverwrite(view_channel=True),
                guild.default_role: PermissionOverwrite(view_channel=False, stream=True),
            },
        )
        return new_channel

    def _get_locale_role(self, locale: LocaleEnum):
        for role_id, role_locale in dynamic_settings.locale_roles.items():
            if locale == role_locale:
                return self.bot.get_main_guild().get_role(role_id)
