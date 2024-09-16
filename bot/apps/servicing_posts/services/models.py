import enum
from dataclasses import dataclass

from core.localization import LocaleEnum


class ServicingActionEnum(enum.Enum):
    LIKE = 'Добавить лайк'
    DISLIKE = 'Добавить дизлайк'
    THREADS = 'Добавить комментарии'
    IGNORE_BOT = 'Игнорировать сообщения от бота'
    REMOVE_BOT = 'Удалить сообщение от бота'


_action_to_attr: dict[ServicingActionEnum, str] = {
    ServicingActionEnum.LIKE: 'add_like',
    ServicingActionEnum.DISLIKE: 'add_dislike',
    ServicingActionEnum.THREADS: 'add_threads',
    ServicingActionEnum.IGNORE_BOT: 'ignore_bot',
    ServicingActionEnum.REMOVE_BOT: 'remove_bot_msg',
}


@dataclass(kw_only=True)
class ServicingPostSettings:
    channel_id: int
    channel_name: str
    locale: LocaleEnum
    add_like: bool
    add_dislike: bool
    add_threads: bool
    ignore_bot: bool = False
    remove_bot_msg: bool = False

    def get_actions(self) -> list[ServicingActionEnum]:
        return [action for action in ServicingActionEnum if getattr(self, _action_to_attr[action])]
