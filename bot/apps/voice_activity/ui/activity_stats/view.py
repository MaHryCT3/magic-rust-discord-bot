import discord

from bot.apps.voice_activity.actions.make_stats_response import (
    MakeActivityStatsResponseAction,
)
from bot.apps.voice_activity.ui.activity_stats.enum import (
    ACTIVITY_PERIOD_TYPE_TRANSLATE,
    ActivityPeriodTypeEnum,
)
from bot.apps.voice_activity.ui.activity_stats.period_select_service import (
    PeriodSelectService,
)
from core.localization import LocaleEnum


class ActivityView(discord.ui.View):
    def __init__(
        self,
        locale: LocaleEnum,
        user: discord.User | None = None,
        channel: discord.StageChannel | discord.VoiceChannel | None = None,
    ):
        self.locale = locale
        self.user = user
        self.channel = channel
        self.offset = 0

        # Селектор выбора периода (Недели, месяца)
        self._period_type_translator = ACTIVITY_PERIOD_TYPE_TRANSLATE[self.locale]
        self._period_type_selector = discord.ui.Select(
            placeholder='Период',
        )
        self._period_type_selector.options = self._get_period_type_options()
        self._period_type_selector.callback = self._period_select_type_callback

        # Селектор для выбора промежутка дат
        self._period_selector = discord.ui.Select(
            placeholder='Промежуток времени',
        )
        self._period_selector.options = self.period_selector_service.get_available_options()
        self._period_selector.callback = self._period_select_callback

        # Кнопки для переключения между страницами
        self._next_button = discord.ui.Button(emoji='➡', row=2)
        self._next_button.callback = self._next_button_callback

        self._prev_button = discord.ui.Button(emoji='⬅', row=2, disabled=True)
        self._prev_button.callback = self._prev_button_callback
        super().__init__(
            self._period_type_selector,
            self._period_selector,
            self._prev_button,
            self._next_button,
            timeout=None,
        )

    @property
    def period_selector_service(self) -> PeriodSelectService:
        selected_type = self._period_type_selector.values
        if selected_type:
            period_type = ActivityPeriodTypeEnum(selected_type[0])
        else:
            period_type = ActivityPeriodTypeEnum.WEEK
        return PeriodSelectService(locale=self.locale, period_type=period_type)

    async def get_embed(self, guild: discord.Guild):
        if period_value := self._period_selector.values:
            period_start, period_end = self.period_selector_service.get_time_period_by_select(period_value[0])
        else:
            period_start, period_end = self.period_selector_service.get_default_period()
        embed = await MakeActivityStatsResponseAction(
            offset=self.offset,
            period_start=period_start,
            period_end=period_end,
            guild=guild,
            locale=self.locale,
        ).execute()

        if not embed.fields:
            self._next_button.disabled = True
        else:
            self._next_button.disabled = False

        return embed

    async def update(self, interaction: discord.Interaction):
        embed = await self.get_embed(interaction.guild)
        await interaction.response.edit_message(
            embeds=[embed],
            files=[],
            attachments=[],
            view=self,
        )

    def refresh_select_options(self):
        if period := self._period_selector.values:
            self._period_selector.options = self.period_selector_service.get_available_options(default_value=period[0])
        else:
            self._period_selector.options = self.period_selector_service.get_available_options()

        self._period_type_selector.options = self._get_period_type_options()

    async def _period_select_callback(self, interaction: discord.Interaction) -> None:
        self.refresh_select_options()
        await self.update(interaction)

    async def _period_select_type_callback(self, interaction: discord.Interaction) -> None:
        self.refresh_select_options()
        self.offset = 0
        await self.update(interaction)

    async def _next_button_callback(self, interaction: discord.Interaction) -> None:
        self.offset += 1
        self._prev_button.disabled = False
        await self.update(interaction)

    async def _prev_button_callback(self, interaction: discord.Interaction):
        self.offset -= 1
        if self.offset == 0:
            self._prev_button.disabled = True
        self._next_button.disabled = False
        await self.update(interaction)

    def _get_period_type_options(self):
        default = ActivityPeriodTypeEnum.WEEK
        if current_value := self._period_type_selector.values:
            default = ActivityPeriodTypeEnum(current_value[0])

        return [
            discord.SelectOption(
                label=self._period_type_translator[period_type],
                value=period_type.value,
                default=period_type == default,
            )
            for period_type in ActivityPeriodTypeEnum
        ]
