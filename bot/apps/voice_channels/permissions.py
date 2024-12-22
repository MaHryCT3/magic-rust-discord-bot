import discord

opened_room_permission = discord.PermissionOverwrite(
    connect=True,
    view_channel=True,
    send_messages=False,
)
closed_room_permission = discord.PermissionOverwrite(
    connect=False,
    view_channel=True,
    send_messages=False,
)


creator_room_permission = discord.PermissionOverwrite(
    manage_channels=True,
    move_members=True,
    set_voice_channel_status=True,
    send_messages=False,
    connect=True,
)
member_room_permission = discord.PermissionOverwrite()
