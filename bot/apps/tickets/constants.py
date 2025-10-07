from typing import Final

TICKET_COUNTER_KEY: Final[str] = 'ticket_counter'
OPENED_TICKETS_NAMESPACE: Final[str] = 'opened_tickets'
USER_TICKET_CHANNEL_NAMESPACE: Final[str] = 'user_ticket_channel'
MINUTES_TO_CLOSE_TICKET_MARKED_AS_RESOLVED: Final[int] = 20


# ------------------ REVIEW AWAITING ------------------
REVIEW_AWAITING_NAMESPACE: Final[str] = 'review_awaiting'
REVIEW_AWAITING_HOURS: Final[int] = 24  # нужно учитывать время запуска таски
