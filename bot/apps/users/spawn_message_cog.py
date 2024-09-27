import discord
from discord import SlashCommandGroup
from discord.ext import commands

from bot import MagicRustBot
from bot.apps.users.ui import SelectRoleView
from bot.config import settings
from core.checks import is_owner
from core.utils.format_strings import bold_message
from global_constants import MAGIC_RUST_IMAGE


class SpawnMessageCog(commands.Cog):
    users = SlashCommandGroup(
        name='users',
        default_member_permissions=discord.Permissions(
            administrator=True,
            ban_members=True,
        ),
        checks=[is_owner(settings.DISCORD_OWNER_IDS)],
    )

    message_text = f"""Press the {bold_message('button')} to select your {bold_message('language')}.
Нажмите на {bold_message('кнопку')} для выбора Вашего {bold_message('языка')}.
    """

    def __init__(self, bot: MagicRustBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(SelectRoleView())

    @users.command(desctiption='Создать сообщение для выбора роли и языка')
    async def spawn_select_role_message(self, ctx: discord.ApplicationContext):
        view = SelectRoleView()
        embed = (
            discord.Embed(
                colour=discord.Color.dark_purple(),
            )
            .add_field(name='', value=self.message_text)
            .set_author(name='MAGIC RUST', icon_url=MAGIC_RUST_IMAGE)
        )
        await ctx.send(
            embed=embed,
            view=view,
        )
