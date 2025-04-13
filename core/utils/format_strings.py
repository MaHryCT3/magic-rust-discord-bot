import datetime


def framing_message(message: str) -> str:
    return f'```\n{message}\n```'


def bold_message(message: str) -> str:
    return f'**{message}**'


def mention_channel(channel_id: int) -> str:
    return f'<#{channel_id}>'


def mention_user(user_id: int) -> str:
    return f'<@{user_id}>'


def format_default_time(dt: datetime.datetime) -> str:
    """28 November 2018 09:01"""
    return f'<t:{int(dt.timestamp())}>'


def format_relative_time(timestamp: int) -> str:
    """3 years ago"""
    return f'<t:{timestamp}:R>'


def format_link_text(text: str, link: str) -> str:
    return f'[{text}]({link})'
