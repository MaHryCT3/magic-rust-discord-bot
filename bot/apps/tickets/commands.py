import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands
from discord.ext.commands import Cog

from bot.apps.tickets.actions.mark_ticket_as_resolved import MarkTicketAsResolvedAction
from bot.apps.tickets.errors import TicketError
from bot.apps.tickets.services.opened_tickets import OpenedTicketsService
from bot.apps.tickets.services.review_awaiting import ReviewAwaitingService
from bot.apps.tickets.ui.make_ticket import MakeTicketView
from bot.apps.tickets.ui.resolve_ticket.views import ResolveTicketView
from bot.apps.tickets.ui.ticket_header.channel_view import TicketHeaderView
from bot.apps.tickets.ui.ticket_header.score_view import TicketScoreView
from bot.bot import MagicRustBot
from bot.constants import MAIN_COLOR
from bot.dynamic_settings import dynamic_settings
from core.checks import DynamicSpecificRoleCheck
from core.localization import LocaleEnum


class CommandsTicketsCog(Cog):
    ticket_group = SlashCommandGroup(
        name='ticket',
        contexts={
            discord.InteractionContextType.guild,
        },
    )
    image_embed_localization: dict[LocaleEnum, discord.Embed] = {
        LocaleEnum.ru: discord.Embed(
            image='https://i.imgur.com/iAWcvWq.jpeg',
            colour=MAIN_COLOR,
        ),
        LocaleEnum.en: discord.Embed(
            image='https://i.imgur.com/rTfX4F6.jpeg',
            colour=MAIN_COLOR,
        ),
    }

    def __init__(self, bot: MagicRustBot):
        self.bot = bot
        self._review_awaiting_service = ReviewAwaitingService()

    @Cog.listener()
    async def on_ready(self):
        for locale in LocaleEnum:
            self.bot.add_view(ResolveTicketView(locale=locale))
            self.bot.add_view(TicketHeaderView(locale=locale))
            self.bot.add_view(MakeTicketView(locale=locale))

        reviews_awaiting = await self._review_awaiting_service.get_all_awaiting_review()
        for review in reviews_awaiting:
            self.bot.add_view(
                TicketScoreView(locale=review.locale, ticket_number=review.ticket_number),
            )

    @ticket_group.command(description='Создать сообщение для создания тикетов')
    @commands.has_permissions(administrator=True)
    async def spawn_ticket(self, ctx: discord.ApplicationContext, locale: discord.Option(LocaleEnum)):
        image_embed = self.image_embed_localization[locale]
        view = MakeTicketView(locale)

        await ctx.send(view=view, embeds=[image_embed])

    @ticket_group.command()
    @commands.has_permissions(administrator=True)
    async def remove_ticket(self, ctx: discord.ApplicationContext, member: discord.Member):
        ticket_service = OpenedTicketsService()
        ticket = await ticket_service.get_user_ticket_by_user_id(member.id)
        if not ticket:
            return await ctx.respond(f'Не найдено тикета у {member.mention}', ephemeral=True)
        await ticket_service.delete_user_ticket(ticket)
        await ctx.respond(f'Запись о тикете удалена для {member.mention}', ephemeral=True)

    @ticket_group.command()
    @commands.check(DynamicSpecificRoleCheck(lambda: dynamic_settings.ticket_roles_ids))
    async def resolve(self, ctx: discord.ApplicationContext):
        action = MarkTicketAsResolvedAction(
            resolved_by=ctx.author,
            channel=ctx.channel,
        )
        await action.execute()
        await ctx.respond(
            'Вопрос помечен как решенный, автор не сможет отправлять сообщения, пока не нажмет "Вопрос не решен"',
            delete_after=20,
            ephemeral=True,
        )

    @ticket_group.command()
    async def test(self, ctx: discord.ApplicationContext):
        from chat_exporter import chat_exporter
        import io

        exported = await chat_exporter.export(
            channel=ctx.channel,
        )
        chat_history_file = discord.File(
            io.BytesIO(exported.encode()),
            filename=f'forum-test.html',
        )

        await ctx.author.send('форум', file=chat_history_file)

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: TicketError):
        if isinstance(error, TicketError):
            return await ctx.respond(error.message, ephemeral=True)
        raise error
