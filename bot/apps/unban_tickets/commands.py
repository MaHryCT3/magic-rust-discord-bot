import discord
from discord import SlashCommandGroup
from discord.ext.commands import Cog

from bot import MagicRustBot
from bot.apps.unban_tickets.actions.moderate_ticket import (
    ApproveUnbanTicket,
    RejectUnbanTicket,
)
from bot.apps.unban_tickets.constants import UNBAN_TICKET_EMBED_TEXT
from bot.apps.unban_tickets.cooldowns import unban_ticket_cooldown
from bot.apps.unban_tickets.errors import (
    UnbanTicketError,
    UserDmIsClosed,
    UserDontHaveTicket,
)
from bot.apps.unban_tickets.ui.create_ticket_view import CreateUnbanTicketView
from bot.apps.unban_tickets.ui.moderate_ticket_view import ModerateDiscordView
from bot.constants import MAIN_COLOR
from core.emojis import Emojis
from core.localization import LocaleEnum


class CommandsUnbanTicketsCog(Cog):
    unban_ticket_group = SlashCommandGroup(
        name='unban_ticket',
        default_member_permissions=discord.Permissions(
            administrator=True,
            ban_members=True,
        ),
        contexts={discord.InteractionContextType.guild},
    )

    embed_localization = {
        LocaleEnum.ru: discord.Embed(
            title='Заявка на разбан',
            color=MAIN_COLOR,
        ).add_field(name='', value=UNBAN_TICKET_EMBED_TEXT[LocaleEnum.ru]),
        LocaleEnum.en: discord.Embed(
            title='Unban request',
            color=MAIN_COLOR,
        ).add_field(name='', value=UNBAN_TICKET_EMBED_TEXT[LocaleEnum.en]),
    }

    def __init__(self, bot: MagicRustBot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        self.bot.add_view(ModerateDiscordView.for_persist_init())

        for view in CreateUnbanTicketView.all_locales_init():
            self.bot.add_view(view)

    @unban_ticket_group.command()
    async def spawn_message(self, ctx: discord.ApplicationContext, locale: discord.Option(LocaleEnum)):
        embed = self.embed_localization[locale]
        view = CreateUnbanTicketView(locale=locale)

        await ctx.send(view=view, embeds=[embed])

    @unban_ticket_group.command()
    async def approve(self, ctx: discord.ApplicationContext, user: discord.User):
        action = ApproveUnbanTicket(user_id=user.id, bot=self.bot, initiator_user=ctx.author)
        try:
            await action.execute()
        except UserDontHaveTicket:
            return await ctx.respond(
                f'{Emojis.WARNING}Не найдено заявки для {user.mention}',
                delete_after=20,
                ephemeral=True,
            )
        except UserDmIsClosed:
            return await ctx.respond(
                f'{Emojis.WARNING}Заявка принято, но результат отправить не удалось так как '
                f'у {user.mention} закрыты личные сообщения с ботом',
                delete_after=20,
                ephemeral=True,
            )

        await ctx.respond(
            f'Заявка принята и результат отправлен {user.mention}',
            ephemeral=True,
        )

    @unban_ticket_group.command()
    async def reject(self, ctx: discord.ApplicationContext, user: discord.User):
        action = RejectUnbanTicket(user_id=user.id, bot=self.bot, initiator_user=ctx.author)
        try:
            await action.execute()
        except UserDontHaveTicket:
            return await ctx.respond(
                f'{Emojis.WARNING}Не найдено заявки для {user.mention}',
                delete_after=20,
                ephemeral=True,
            )
        except UserDmIsClosed:
            return await ctx.respond(
                f'{Emojis.WARNING}Заявка отклонена, но результат отправить не удалось так как '
                f'у {user.mention} закрыты личные сообщения с ботом',
                delete_after=20,
                ephemeral=True,
            )

        await ctx.respond(
            f'Заявка отклонена и результат отправлен {user.mention}',
            ephemeral=True,
        )

    @unban_ticket_group.command()
    async def reset_cooldown(self, ctx: discord.ApplicationContext, user: discord.User):
        await unban_ticket_cooldown.reset_cooldown(user_id=user.id)
        await ctx.respond(
            f'Кулдаун на создание заявки для {user.mention} сброшен',
            delete_after=20,
            ephemeral=True,
        )

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: UnbanTicketError):
        if isinstance(error, UnbanTicketError):
            return await ctx.respond(error.message, ephemeral=True)
        raise error
