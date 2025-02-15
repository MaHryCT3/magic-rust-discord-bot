from dataclasses import dataclass, field
from datetime import date, datetime

import discord

from bot.apps.voice_activity.services.activity_api import ActivityAPI
from bot.apps.voice_activity.structs.user_activity import UserActivity
from bot.constants import MAIN_COLOR
from core.actions.abstract import AbstractAction
from core.localization import LocaleEnum
from core.shortcuts import get_or_fetch_member
from core.utils.humanize import human_time

_title_localization: dict[LocaleEnum, str] = {
    LocaleEnum.ru: 'Рейтинг активности в голосовых каналах',
    LocaleEnum.en: 'Activity rating in voice channels',
}

# _line_template_localization: dict[LocaleEnum, str] = {
#     LocaleEnum.ru: '#{place} {user_name} ⏳{activity_time} | ⏱️{total_time} '
#     '| 🔇{total_microphone_disabled} | 🔕{total_sound_disabled_duration}',
#     LocaleEnum.en: '#{place} {user_name} ⏳{activity_time} | ⏱️{total_time} '
#     '| 🔇{total_microphone_disabled} | 🔕{total_sound_disabled_duration}',
# }
_line_template_localization: dict[LocaleEnum, str] = {
    LocaleEnum.ru: '#{place} {user_name} \n Активное время: ⏳{activity_time}\n'
    ' Не засчитанное: 🔇{total_sound_disabled} (no mic, no sound)',
    LocaleEnum.en: '#{place} {user_name} \n Active time: ⏳{activity_time}\n'
    ' Unscored: 🔇{total_sound_disabled} (no mic, no sound)',
}


@dataclass(kw_only=True)
class MakeActivityStatsResponseAction(AbstractAction[discord.Embed]):
    period_start: datetime | date | None = None
    period_end: datetime | date | None = None
    user: discord.Member | None = None
    channel: discord.VoiceChannel | discord.StageChannel | None = None
    offset: int = 0
    guild: discord.Guild
    locale: LocaleEnum

    activity_api: ActivityAPI = field(default_factory=ActivityAPI)

    async def action(self):
        activity = await self.activity_api.get_activity(
            start_at=self.period_start,
            end_at=self.period_end,
            user_id=self.user.id if self.user else None,
            channel_id=self.channel.id if self.channel else None,
        )
        return await self._make_embed(activity)

    async def _make_embed(self, activities: list[UserActivity]) -> discord.Embed:
        embed = discord.Embed(
            title=_title_localization[self.locale],
            colour=MAIN_COLOR,
        )

        for place, activity in enumerate(activities, start=1):
            line = await self._make_embed_line(
                place=self.offset + place,
                activity=activity,
            )
            embed.add_field(
                name='',
                value=line,
                inline=False,
            )
        return embed
        # rating_text = '\n'.join(lines)
        # print(rating_text)
        # return embed.add_field(name='', value=rating_text)

    async def _make_embed_line(self, place: int, activity: UserActivity) -> str:
        member = await get_or_fetch_member(self.guild, activity.user_id)

        line_template = _line_template_localization[self.locale]
        line = line_template.format(
            place=place,
            user_name=member.mention,
            activity_time=human_time(int(activity.activity_time_duration.total_seconds()), self.locale),
            total_time=human_time(int(activity.total_session_duration.total_seconds()), self.locale),
            total_sound_disabled=human_time(
                int((activity.total_microphone_mute_duration + activity.total_sound_disabled_duration).total_seconds()),
                self.locale,
            ),
            total_microphone_disabled=human_time(
                int(activity.total_microphone_mute_duration.total_seconds()), self.locale
            ),
            total_sound_disabled_duration=human_time(
                int(activity.total_sound_disabled_duration.total_seconds()), self.locale
            ),
        )
        return line
