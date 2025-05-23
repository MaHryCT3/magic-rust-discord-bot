import discord
from discord.ext.commands import Cog

from bot import MagicRustBot
from core.logger import logger
from core.shortcuts import get_or_fetch_channel


class ReactionModerationCog(Cog):
    default_blocked_reactions: list[str] = [
        '🏳️‍🌈',
        '🇦',
        '🇧',
        '🇨',
        '🇩',
        '🇪',
        '🇫',
        '🇬',
        '🇭',
        '🇮',
        '🇯',
        '🇰',
        '🇱',
        '🇲',
        '🇳',
        '🇴',
        '🇵',
        '🇶',
        '🇷',
        '🇸',
        '🇹',
        '🇺',
        '🇻',
        '🇼',
        '🇽',
        '🇾',
        '🇿',
    ]

    def __init__(self, bot: MagicRustBot):
        self.bot = bot

        self.guild: discord.Guild = None

    @Cog.listener()
    async def on_ready(self):
        self.guild = await self.bot.get_or_fetch_main_guild()

    @Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        for reactions_pattern in self.default_blocked_reactions:
            if reactions_pattern == payload.emoji.name:
                break
        else:
            return

        channel = await get_or_fetch_channel(self.guild, payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        await message.clear_reaction(payload.emoji)
        logger.info(
            f'Для сообщения {channel.id}:{message.id} удалена реакция {payload.emoji.name}. Автор: {payload.user_id}'
        )
