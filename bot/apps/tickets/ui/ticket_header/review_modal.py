import discord
from discord import Interaction

from bot.apps.tickets.actions.confirm_review import ConfirmReviewAction
from core.localization import LocaleEnum
from core.ui.modals import BaseLocalizationModal, InputText


class SendReviewModal(BaseLocalizationModal):
    title_localization_map = {
        LocaleEnum.ru: 'Отправить отзыв',
        LocaleEnum.en: 'Sent feedback',
    }

    review = InputText(
        style=discord.InputTextStyle.long,
        required=False,
        max_length=512,
    )

    inputs_localization_map = {
        review: {
            LocaleEnum.ru: dict(label='Отзыв'),
            LocaleEnum.en: dict(label='Feedback'),
        },
    }

    respond_localization = {
        LocaleEnum.ru: 'Ваш отзыв отправлен. Спасибо!',
        LocaleEnum.en: 'Your feedback has been sent. Thank you!',
    }

    def __init__(
        self,
        ticket_history_message: discord.Message,
        ticket_number: int,
        score: int | None = None,
        **kwargs,
    ):
        self.ticket_history_message = ticket_history_message
        self.ticket_number = ticket_number
        self.score = score
        super().__init__(**kwargs)

    async def callback(self, interaction: Interaction):
        if self.review:
            await ConfirmReviewAction(
                locale=self.locale,
                ticket_history_message=self.ticket_history_message,
                ticket_number=self.ticket_number,
                score=self.score,
                review=self.review,
            ).execute()

        await interaction.respond(
            self.respond_localization[self.locale],
            ephemeral=True,
            delete_after=15,
        )
