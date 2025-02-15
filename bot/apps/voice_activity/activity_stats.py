import discord
from discord import SlashCommandGroup
from discord.ext.commands import Cog

from bot import MagicRustBot
from bot.apps.users.utils import get_member_locale
from bot.apps.voice_activity.ui.activity_stats import ActivityView
from core.localization import LocaleEnum


class ActivityStatusCog(Cog):
    activity_group = SlashCommandGroup(
        name='activity',
        description='Просмотр статистики голосовой активности',
        contexts={discord.InteractionContextType.guild},
    )

    def __init__(self, bot: MagicRustBot):
        self.bot = bot

    @activity_group.command()
    async def stats(self, ctx: discord.ApplicationContext):
        locale = get_member_locale(ctx.author, default_locale=LocaleEnum.en)

        view = ActivityView(locale=locale)
        embed = await view.get_embed(ctx.guild)
        await ctx.respond(
            embeds=[embed],
            view=view,
            ephemeral=True,
            allowed_mentions=discord.AllowedMentions(users=False),
        )
