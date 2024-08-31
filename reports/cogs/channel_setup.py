import discord
from discord import SlashCommandGroup
from discord.ext import commands

from core.checks import is_owner
from core.localization import LocaleEnum
from core.utils.format_strings import framing_message
from reports.bot import MagicRustReportBot
from reports.config import settings
from reports.constants import MAIN_COLOR
from reports.ui.report_view import ReportView


class ChannelSetupCog(commands.Cog):
    reports_group = SlashCommandGroup(
        name='reports',
        description='Управление репортами',
        default_member_permissions=discord.Permissions(
            administrator=True,
            ban_members=True,
        ),
        checks=[is_owner(settings.DISCORD_OWNER_IDS)],
        contexts={discord.InteractionContextType.guild},
    )

    image_embed_localization: dict[LocaleEnum, discord.Embed] = {
        LocaleEnum.ru: discord.Embed(
            image='https://i.imgur.com/A9iqjxG.jpeg',
            colour=MAIN_COLOR,
        ),
        LocaleEnum.en: discord.Embed(
            image='https://i.imgur.com/6tyie7P.jpeg',
            colour=MAIN_COLOR,
        ),
    }
    report_content_embed_localization: dict[LocaleEnum, discord.Embed] = {
        LocaleEnum.ru: discord.Embed(
            fields=[
                discord.EmbedField(
                    name='🟣 Magic Rust | Жалобы',
                    value=framing_message(
                        'В создавшемся обращении, '
                        'как можно точнее опишите его суть и по '
                        'возможности прикрепите фото и/или видео для дальнейшего ознакомления.',
                    ),
                )
            ],
            colour=MAIN_COLOR,
        ),
        LocaleEnum.en: discord.Embed(
            fields=[
                discord.EmbedField(
                    name='🟣 Magic Rust | Reports',
                    value=framing_message(
                        'In the created request,'
                        ' describe its essence as accurately as possible and, '
                        'if possible, attach a photo and/or video for further reference.',
                    ),
                )
            ],
            colour=MAIN_COLOR,
        ),
    }

    def __init__(self, bot: MagicRustReportBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        for view in ReportView.all_locales_init():
            self.bot.add_view(view)

    @reports_group.command(description='Установить канал для жалоб')
    async def set_channel(
        self,
        ctx: discord.ApplicationContext,
        locale: discord.Option(LocaleEnum),
    ):

        image_embed = self.image_embed_localization[locale]
        text_embed = self.report_content_embed_localization[locale]
        view = ReportView(locale=locale)
        await ctx.send(
            embeds=[image_embed, text_embed],
            view=view,
        )
        await ctx.respond('Создано', ephemeral=True, delete_after=10)
