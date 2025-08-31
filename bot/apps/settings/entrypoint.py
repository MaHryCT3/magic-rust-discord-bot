import discord
from discord import SlashCommandGroup

settings_group = SlashCommandGroup(
    name='settings',
    description='Настройка бота',
    default_member_permissions=discord.Permissions(
        administrator=True,
        ban_members=True,
    ),
    contexts={discord.InteractionContextType.guild},
)
