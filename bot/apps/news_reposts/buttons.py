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
        news_message = await channel.send(embeds=interaction.message.embeds, view=view)
        if interaction.message.poll or interaction.message.attachments:
            poll = self._copy_poll(interaction.message.poll)
            await channel.send(poll=poll, files=interaction.message.attachments)
        content = f'{news_message.jump_url}\nНовость опубликована {interaction.user.mention}'
        await interaction.message.channel.send(content=content)
        await interaction.message.delete()
        await interaction.respond('Новость успешно опубликована', delete_after=10, ephemeral=True)
        return super().callback(interaction)

    @classmethod
    def _copy_poll(cls, poll: discord.Poll) -> discord.Poll:
        return discord.Poll(
            question=poll.question, answers=poll.answers, duration=poll.duration, layout_type=poll.layout_type
        )


class DeclineNewsButton(discord.ui.Button):
    def __init__(self, *args, bot: MagicRustBot, **kwargs):
        self.bot = bot
        super().__init__(*args, label='Скрыть', style=discord.ButtonStyle.red, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        await interaction.message.delete()
        content = f'{interaction.message.content}\nНовость скрыта {interaction.user.mention}'
        await interaction.message.channel.send(content=content)
        await interaction.message.channel.send('Новость скрыта', delete_after=10, ephemeral=True)
        return await super().callback(interaction)
