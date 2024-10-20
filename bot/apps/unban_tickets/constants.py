from typing import Final

import discord

from core.localization import LocaleEnum

UNBAN_TICKET_COOLDOWN_SECONDS: Final[int] = 60 * 60 * 24 * 30  # 30 дней
UNBAN_TICKET_COLOR = discord.Color.red()


UNBAN_TICKET_EMBED_TEXT = {
    LocaleEnum.ru: """- Ваш профиль Steam должен быть открытым.
- За предоставление недостоверной информации ваша заявка будет отклонена.

⚠Подача заявки не гарантирует снятия блокировки с Вашего аккаунта. 
При её рассмотрении модератор учитывает множество факторов 
(например, срок, прошедший с момента бана, серьезность нарушения и т.п.), после чего выносит свой вердикт.

Заявки рассматриваются преимущественно по четвергам и в порядке очереди.

Обратите внимание на то, что нет какого-то определенного времени, которое должно пройти, чтобы получить разбан.""",
    LocaleEnum.en: """- Your Steam profile must be open.
- If you provide false information, your application will be rejected.

Submitting a request does not guarantee that your account will be unban. 
The moderator will consider many factors 
(e.g. time since the ban, severity of the offense, etc.) and then make a verdict.

Applications are reviewed primarily on Thursdays and on a first-come, first-served basis.

Please note that there is no specific amount of time that must pass before you can be unbanned.
""",
}
