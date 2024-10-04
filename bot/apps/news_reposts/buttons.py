import discord

from bot.bot import MagicRustBot
from bot.dynamic_settings import dynamic_settings


class PublishNewsButton(discord.ui.Button):
    def __init__(self, *args, bot: MagicRustBot, **kwargs):
        self.bot = bot
        super().__init__(*args, label='Опубликовать', style=discord.ButtonStyle.green, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        channel: discord.TextChannel = await self.bot.fetch_channel(dynamic_settings.repost_channel)
        view = discord.ui.View(discord.ui.Button(label='Перейти к посту', url=interaction.message.content))
        await channel.send(embeds=interaction.message.embeds, view=view)
        if interaction.message.poll or interaction.message.attachments:
            await channel.send(poll=interaction.message.poll, files=interaction.message.attachments)
        content = f'{interaction.message.content}\nНовость опубликована {interaction.user.display_name}'
        await interaction.message.edit(content=content, poll=None, files=[], embeds=[], view=None)
        await interaction.message.channel.send('Новость успешно опубликована', delete_after=10, ephemeral=True)
        return super().callback(interaction)


class DeclineNewsButton(discord.ui.Button):
    def __init__(self, *args, bot: MagicRustBot, **kwargs):
        self.bot = bot
        super().__init__(*args, label='Скрыть', style=discord.ButtonStyle.red, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        content = f'{interaction.message.content}\nНовость отклонена {interaction.user.display_name}'
        await interaction.message.edit(content=content, poll=None, files=[], embeds=[], view=None)
        await interaction.message.channel.send('Новость скрыта', delete_after=10, ephemeral=True)
        return super().callback(interaction)
