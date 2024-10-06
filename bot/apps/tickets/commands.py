import discord
from discord.commands import SlashCommandGroup
from discord.ext.commands import Cog

from bot.apps.tickets.errors import TicketError
from bot.apps.tickets.services.opened_tickets import OpenedTicketsService
from bot.apps.tickets.ui import MakeTicketView
from bot.apps.tickets.ui.ticket_header import TicketHeaderView
from bot.bot import MagicRustBot
from bot.config import settings
from bot.constants import MAIN_COLOR
from core.checks import is_owner
from core.localization import LocaleEnum


class CommandsTicketsCog(Cog):
    ticket_group = SlashCommandGroup(
        name='ticket',
        checks=[is_owner(settings.DISCORD_OWNER_IDS)],
        default_member_permissions=discord.Permissions(
            administrator=True,
            ban_members=True,
        ),
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

    def __init__(self, bot: MagicRustBot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        for view in MakeTicketView.all_locales_init():
            self.bot.add_view(view)
        for view in TicketHeaderView.all_locales_init():
            self.bot.add_view(view)

    @ticket_group.command(description='Создать сообщение для создания тикетов')
    async def spawn_ticket(self, ctx: discord.ApplicationContext, locale: discord.Option(LocaleEnum)):
        image_embed = self.image_embed_localization[locale]
        view = MakeTicketView(locale)

        await ctx.send(view=view, embeds=[image_embed])
        await ctx.interaction.response.pong()

    @ticket_group.command()
    async def remove_ticket(self, ctx: discord.ApplicationContext, member: discord.Member):
        ticket_service = OpenedTicketsService()
        ticket = await ticket_service.get_user_ticket_by_user_id(member.id)
        if not ticket:
            return await ctx.respond(f'Не найдено тикета у {member.mention}', ephemeral=True)
        await ticket_service.delete_user_ticket(ticket)
        await ctx.respond(f'Запись о тикете удалена для {member.mention}', ephemeral=True)

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: TicketError):
        if isinstance(error, TicketError):
            return await ctx.respond(error.message, ephemeral=True)
        raise error
