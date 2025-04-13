import discord

from bot.dynamic_settings import dynamic_settings


def get_channel_ticket_moderators(channel: discord.TextChannel):
    moderators_roles_ids = dynamic_settings.ticket_roles_ids
    moderators = []

    for member in channel.members:
        for role in member.roles:
            if role and role.id in moderators_roles_ids:
                moderators.append(member)
    return moderators
