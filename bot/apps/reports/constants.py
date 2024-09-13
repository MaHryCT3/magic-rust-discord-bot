from typing import Final

import discord

REPORT_COOLDOWN: Final[int] = 30
MAIN_COLOR = discord.Color.dark_purple()
VK_REPORT_MESSAGE_TEMPLATE: Final[
    str
] = """Номер сервера: {server_name}
Жалоба от пользователя {discord_name} | {discord_id}
Нарушители: {players}
Текст жалобы: {report_text}
"""
