import discord

user_ticket_overwrites = discord.PermissionOverwrite(
    view_channel=True,
    read_message_history=True,
    send_messages=True,
)

user_ticket_overwrites_no_send_message = discord.PermissionOverwrite(
    view_channel=True,
    read_message_history=True,
    send_messages=False,
)
