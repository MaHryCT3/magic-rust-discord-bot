from core.emojis import BaseCustomEmojis, CustomEmojiDescriptor


class CustomEmojis(BaseCustomEmojis):
    OPEN_ROOM = CustomEmojiDescriptor('openroom')
    CLOSE_ROOM = CustomEmojiDescriptor('closeroom')
    GRANT = CustomEmojiDescriptor('grant')
    LIMIT = CustomEmojiDescriptor('limit')
    KICK = CustomEmojiDescriptor('kick')
    CHANGE_NAME = CustomEmojiDescriptor('changename')
