import datetime


def framing_message(message: str) -> str:
    return f'```\n{message}\n```'


def bold_message(message: str) -> str:
    return f'**{message}**'


def mention_channel(channel_id: int) -> str:
    return f'<#{channel_id}>'


def format_default_time(dt: datetime.datetime) -> str:
    return f'<t:{int(dt.timestamp())}>'
