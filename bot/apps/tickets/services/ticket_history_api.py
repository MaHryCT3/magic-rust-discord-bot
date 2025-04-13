import datetime
from typing import Final

from bot.config import settings
from core.clients.http import HTTPClient


class TicketHistoryAPI:
    CREATE_HISTORY_URI: Final[str] = 'api/v1/tickets/history'
    UPDATE_HISTORY_REVIEW_URI: Final[str] = '/api/v1/tickets/history/{ticket_number}/review'
    GET_TICKET_LOGS_URL: Final[str] = '/api/v1/tickets/history/{ticket_number}/logs/url'

    def __init__(
        self,
        backend_url: str = settings.TICKETS_BACKEND_URL,
        api_token: str = settings.TICKETS_BACKEND_API_TOKEN,
    ):
        self.http_client = HTTPClient(
            base_url=backend_url,
            headers={'X-API-Key': api_token},
        )

    async def create_ticket_history(
        self,
        author_discord_id: int,
        moderators_discord_ids: list[int],
        last_moderator_answer_id: int | None,
        start_datetime: datetime.datetime,
        end_datetime: datetime.datetime,
        ticket_number: int,
        html_logs: str,
        score: int | None = None,
        comment: int | None = None,
    ) -> str:
        data = {
            'author_discord_id': author_discord_id,
            'moderators_discord_ids': moderators_discord_ids,
            'last_moderator_answer_id': last_moderator_answer_id,
            'start_datetime': start_datetime.isoformat(),
            'end_datetime': end_datetime.isoformat(),
            'ticket_number': ticket_number,
            'html_logs': html_logs,
            'score': score,
            'comment': comment,
        }

        response = await self.http_client.post(
            self.CREATE_HISTORY_URI,
            body=data,
        )

        return response.json()['id']

    async def update_ticket_review(
        self,
        ticket_number: int,
        score: int | None = None,
        comment: str | None = None,
    ):
        body = {
            'score': score,
            'comment': comment,
        }

        return await self.http_client.patch(
            self.UPDATE_HISTORY_REVIEW_URI.format(ticket_number=ticket_number),
            body=body,
        )

    async def get_ticket_history_logs_file_url(self, ticket_number: int) -> str:
        result = await self.http_client.get(
            self.GET_TICKET_LOGS_URL.format(ticket_number=ticket_number),
        )
        return result.text.removeprefix('"').removesuffix('"')
