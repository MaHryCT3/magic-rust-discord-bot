from logging import ERROR

from discord import VoiceChannel
from discord.ext import commands, tasks

from bot.apps.channel_cleaner.exceptions import (
    CategoryNotConfiguredError,
    RoomCreateCooldownError,
)
from bot.bot import MagicRustBot
from bot.config import logger, settings
from bot.dynamic_settings import dynamic_settings
from core.localization import LocaleEnum, LocalizationDict
from core.redis_cooldown import RedisCooldown
from core.utils.decorators import loop_stability_checker
from global_constants import CREATE_VOICE_COOLDOWN_NAMESPACE

CREATE_SERVER_UPDATE_SECONDS = 1.0


class RoomCreator(commands.Cog):
    room_name_localization = LocalizationDict({LocaleEnum.en: 'Room {room_name}', LocaleEnum.ru: 'Комната {room_name}'})

    def __init__(self, bot: MagicRustBot):
        self.bot = bot
        self.create_room_cooldown = RedisCooldown(settings.REDIS_URL, CREATE_VOICE_COOLDOWN_NAMESPACE)

    @commands.Cog.listener()
    async def on_ready(self):
        self.check_creating_channels.start()

    @tasks.loop(seconds=CREATE_SERVER_UPDATE_SECONDS)
    @loop_stability_checker(seconds=CREATE_SERVER_UPDATE_SECONDS)
    async def check_creating_channels(self):
        cooldown = dynamic_settings.user_room_create_cooldown
        for locale, channel_id in dynamic_settings.channel_creating_channels.items():
            channel: VoiceChannel = await self.bot.fetch_channel(channel_id)
            for member in channel.members:
                try:
                    if cooldown_residue := await self.create_room_cooldown.get_user_cooldown_residue(
                        member.id, cooldown
                    ):
                        raise RoomCreateCooldownError(cooldown=cooldown, retry_after=cooldown_residue, locale=locale)
                    new_channel = await self.create_room(member.display_name, locale)
                    await self.create_room_cooldown.set_user_cooldown(
                        user_id=member.id,
                        cooldown_in_seconds=cooldown,
                    )
                    await new_channel.set_permissions(member, manage_channels=True)
                    await member.move_to(new_channel)
                except RoomCreateCooldownError as err:
                    await member.move_to(None)
                    await member.send(embed=err.get_embed())
                except CategoryNotConfiguredError:
                    await member.move_to(None)
                    logger.log(ERROR, f'Category for user voice rooms for locale {locale} not set!')

    async def create_room(self, room_name: str, locale: LocaleEnum) -> VoiceChannel:
        guild = self.bot.get_main_guild()
        category_id = dynamic_settings.user_rooms_categories.get(locale)
        category = self.bot.get_category(category_id)
        if not category:
            raise CategoryNotConfiguredError(locale)
        new_channel = await guild.create_voice_channel(
            name=self.room_name_localization[locale].format(room_name=room_name), category=category
        )
        return new_channel
