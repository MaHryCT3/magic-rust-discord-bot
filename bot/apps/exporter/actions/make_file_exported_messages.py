import io
import json
from dataclasses import dataclass

import discord

from core.actions.abstract import AbstractAction


@dataclass
class MakeExportFile(AbstractAction[discord.File]):
    exported_chats: dict[discord.Thread | discord.TextChannel, list[discord.Message]]
    file_name: str

    async def action(self) -> discord.File:
        result_data = {}
        for channel, messages in self.exported_chats.items():
            result_data[channel.name] = self._make_list_dict_of_messages(messages)
        return self._make_response_file(result_data, self.file_name)

    def _make_list_dict_of_messages(
        self,
        messages: list[discord.Message],
    ) -> list[dict]:
        return [
            {
                'id': message.id,
                'message': message.content,
                'time': int(message.created_at.timestamp()),
                'room': message.channel.name,
                'user': {
                    'id': message.author.id,
                    'username': message.author.name,
                },
            }
            for message in messages
        ]

    def _make_response_file(
        self,
        result_data: dict[str, list[dict]],
        file_name: str,
    ) -> discord.File:
        json_data = json.dumps(
            result_data,
            indent=2,
            ensure_ascii=False,
        )

        file = io.BytesIO(json_data.encode('utf-8'))

        return discord.File(file, filename=file_name)
