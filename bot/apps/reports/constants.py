from typing import Final

REPORT_COOLDOWN: Final[int] = 30
VK_REPORT_MESSAGE_TEMPLATE: Final[
    str
] = """Номер сервера: {server_name}
Жалоба от пользователя {discord_name} | {discord_id}
Нарушители: {players}
Текст жалобы: {report_text}
"""
