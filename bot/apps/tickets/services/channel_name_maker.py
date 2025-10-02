_ticket_channel_prefix = 'ticket-'


def make_ticket_channel_name(ticket_number: int) -> str:
    ticket_name = f'{_ticket_channel_prefix}{ticket_number}'
    return ticket_name
