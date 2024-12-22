from typing import TypeAlias

from discord import Emoji

EmojiName: TypeAlias = str
EmojiField: TypeAlias = str


class Emojis:
    LIKE = '👍'
    DISLIKE = '👎'
    MESSAGE = '💬'
    TICKET = '🎫'
    PEOPLES = '🧑‍🤝‍🧑'
    DIZZY = '😵'
    ACCEPT = '✅'
    REJECT = '❌'
    AWAITING = '⏳'
    WARNING = '⚠️'


class CustomEmojiDescriptor:
    def __init__(self, emoji_name: str):
        self.emoji_name = emoji_name

    def __set_name__(self, owner, name):
        self.private_name = f'_{name}'
        owner._emoji_field_name_map[self.emoji_name] = self.private_name

    def __get__(self, instance, owner) -> Emoji:
        return getattr(owner, self.private_name)


class BaseCustomEmojis:
    _emoji_field_name_map: dict[EmojiName, EmojiField] = {}
    """Кастомные эмоджи, которые загружены на сервер"""

    @classmethod
    def load_emojis(cls, custom_emojis: list[Emoji]):
        for emoji in custom_emojis:
            field_name = cls._emoji_field_name_map.get(emoji.name)
            if field_name:
                setattr(cls, field_name, emoji)
