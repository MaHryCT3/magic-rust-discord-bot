from dataclasses import dataclass

from discord import Intents


@dataclass
class AppConfig:
    intents: Intents


APPS = {
    'auto_moderation': AppConfig(
        intents=Intents.none()
        + Intents.guilds
        + Intents.guild_reactions
        + Intents.emojis_and_stickers
        + Intents.members
    ),
    'banner_updater': AppConfig(
        intents=Intents.none() + Intents.guilds,
    ),
    'bot_messages': AppConfig(
        intents=Intents.none() + Intents.guilds + Intents.members,
    ),
    'find_friends': AppConfig(
        intents=Intents.none() + Intents.guilds + Intents.members + Intents.guild_messages + Intents.message_content,
    ),
    'info_provider': AppConfig(
        intents=Intents.none() + Intents.guilds + Intents.presences,
    ),
    'news_reposts': AppConfig(
        intents=Intents.none() + Intents.guilds,
    ),
    'reports': AppConfig(
        intents=Intents.none() + Intents.guilds,
    ),
    'server_status': AppConfig(
        intents=Intents.none() + Intents.guilds + Intents.guild_messages + Intents.message_content,
    ),
    'servicing_posts': AppConfig(
        intents=Intents.none() + Intents.guilds + Intents.guild_messages + Intents.message_content + Intents.members,
    ),
    'settings': AppConfig(
        intents=Intents.none() + Intents.guilds,
    ),
    'tickets': AppConfig(
        intents=Intents.none() + Intents.guilds + Intents.members,
    ),
    'unban_tickets': AppConfig(
        intents=Intents.none() + Intents.guilds + Intents.guild_messages + Intents.message_content,
    ),
    'users': AppConfig(
        intents=Intents.none() + Intents.guilds + Intents.members + Intents.guild_messages,
    ),
    'voice_activity': AppConfig(
        intents=Intents.none() + Intents.guilds + Intents.members + Intents.voice_states,
    ),
    'voice_channels': AppConfig(
        intents=Intents.none() + Intents.guilds + Intents.members + Intents.voice_states,
    ),
    'voice_records': AppConfig(
        intents=Intents.none(),
    ),
    'exporter': AppConfig(
        Intents.none(),
    ),
}
