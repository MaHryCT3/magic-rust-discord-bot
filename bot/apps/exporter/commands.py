import datetime

import discord
from discord import SlashCommandGroup
from discord.ext import commands

from bot import MagicRustBot
from bot.apps.exporter.actions.export_pipeline import ExportChatsPipeline
from bot.config import settings
from bot.constants import DATE_FORMAT
from core.utils.date_time import add_timezone


class ExporterCommandCog(commands.Cog):
    export_group = SlashCommandGroup(
        name='export',
        default_member_permissions=discord.Permissions(
            administrator=True,
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
        date_from: discord.Option(str),
        date_to: discord.Option(str, required=False) = None,
    ):
        date_from = add_timezone(datetime.datetime.strptime(date_from, DATE_FORMAT), tz=settings.TIMEZONE)
        if not date_to:
            date_to = datetime.datetime.now(tz=settings.TIMEZONE)

        action = ExportChatsPipeline(
            guild=ctx.guild,
            date_from=date_from,
            date_to=date_to,
        )
        files = await action.execute()

        await ctx.followup.send(
            f'Выгрузка чатов и форумов {date_from.strftime(DATE_FORMAT)} - {date_to.strftime(DATE_FORMAT)}',
            files=files,
        )
