import datetime

import discord
from discord import SlashCommandGroup
from discord.ext import commands
from discord.ext.commands import CommandError

from bot import MagicRustBot
from bot.apps.exporter.actions.export_pipeline import ExportChatsPipeline
from bot.apps.exporter.constants import DEFAULT_TIME_MOVING_FOR_DATE_START
from bot.apps.exporter.exceptions import (
    DateToLessThanDateFrom,
    ExporterDateInvalidFormat,
    ExporterError,
)
from bot.config import settings
from bot.constants import DATE_FORMAT
from bot.dynamic_settings import dynamic_settings
from core.autocompletes.dates import (
    DatePredictionAutocomplete,
    get_default_prediction_date_getter,
)
from core.logger import logger
from core.shortcuts import get_or_fetch_channel
from core.utils.date_time import add_timezone


class ExporterCommandCog(commands.Cog):
    export_group = SlashCommandGroup(
        name='export',
        default_member_permissions=discord.Permissions(
            ban_members=True,
        ),
        contexts={discord.InteractionContextType.guild},
    )

    def __init__(self, bot: MagicRustBot) -> None:
        self.bot = bot

    @export_group.command(
        description='Выгрузка чатов и форумов',
    )
    async def chats(
        self,
        ctx: discord.ApplicationContext,
        date_from: discord.Option(
            str,
            description='Дата начала периода. Формат: ДД.ММ.ГГГГ. Пример: 01.05.2025',
            autocomplete=DatePredictionAutocomplete(
                get_default_prediction_date_getter(DEFAULT_TIME_MOVING_FOR_DATE_START)
            ),
        ),
        date_to: discord.Option(
            str,
            description='Дата конца периода (не включительно). Формат: ДД.ММ.ГГГГ. Пример 07.05.2025. Дефолт: сегодня',
            autocomplete=DatePredictionAutocomplete(get_default_prediction_date_getter()),
            required=False,
        ) = None,
    ):
        date_from = self._parse_input_date(date_from)
        if date_to:
            date_to = self._parse_input_date(date_to)
        else:
            date_to = datetime.datetime.combine(
                datetime.date.today(),
                datetime.time.min,
                tzinfo=settings.TIMEZONE,
            )
        if date_from > date_to:
            raise DateToLessThanDateFrom(date_from, date_to)

        await ctx.respond(
            'Выгрузка в скором времени будет направлена в личные сообщения',
            ephemeral=True,
            delete_after=15,
        )
        logger.info(
            f'({ctx.author.name}:{ctx.author.id}) запустил выгрузку чатов {date_from.date()} - {date_to.date()}'
        )
        action = ExportChatsPipeline(
            date_from=date_from,
            date_to=date_to,
            channels=[
                await get_or_fetch_channel(ctx.guild, channel_id)
                for channel_id in dynamic_settings.default_export_channels
            ],
        )

        try:
            files = await action.execute()
        except Exception as ex:
            await ctx.author.send('Произошла непредвиденная ошибка при выгрузке чатов :(')
            raise ex

        await ctx.author.send(
            f'Выгрузка чатов и форумов {date_from.strftime(DATE_FORMAT)} - {date_to.strftime(DATE_FORMAT)}',
            files=files,
        )

    def _parse_input_date(self, raw_date: str) -> datetime.datetime:
        try:
            return add_timezone(datetime.datetime.strptime(raw_date, DATE_FORMAT), tz=settings.TIMEZONE)
        except ValueError as ex:
            raise ExporterDateInvalidFormat(DATE_FORMAT) from ex

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: CommandError):
        if isinstance(error, ExporterError):
            return await ctx.respond(
                str(error),
                ephemeral=True,
                delete_after=15,
            )
        raise error
