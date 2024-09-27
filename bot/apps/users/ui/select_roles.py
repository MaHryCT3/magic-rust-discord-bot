import discord
from discord import Interaction

from bot.apps.users.constants import SELECT_ROLE_COOLDOWN_SECOND
from bot.apps.users.cooldown import select_role_cooldown
from bot.apps.users.utils import get_member_locale
from bot.dynamic_settings import dynamic_settings
from core.localization import LocaleEnum, LocalizationDict
from core.logger import logger


class SelectRoleButton(discord.ui.Button):
    answer_localization = LocalizationDict(
        {
            LocaleEnum.ru: 'Роль выдана {role_mention}',
            LocaleEnum.en: 'Role given {role_mention}',
        }
    )

    already_granted_localization = LocalizationDict(
        {
            LocaleEnum.ru: 'Роль уже выдана',
            LocaleEnum.en: 'Role already given',
        }
    )

    def __init__(self, label: str, emoji: str, locale: LocaleEnum):
        self.locale = locale
        super().__init__(
            emoji=emoji,
            label=label,
            custom_id=f'users:{self.locale}:button:role',
        )

    async def callback(self, interaction: Interaction):
        if await self._check_on_cooldown(interaction):
            return

        member = interaction.user

        member_locale_role = get_member_locale(member)
        if member_locale_role == self.locale:
            await interaction.respond(self.already_granted_localization[self.locale], ephemeral=True)
            return

        roles_map: dict[LocaleEnum, int] = dynamic_settings.locale_roles

        # Удаление если выдана какая-то другая роль языка
        if member_locale_role:
            role = interaction.guild.get_role(roles_map[member_locale_role])
            await member.remove_roles(role)
            logger.info(f'Удалена роль {role.name} у {member.name}|{member.id}')

        # Добавление роли
        role_to_add = interaction.guild.get_role(roles_map[self.locale])
        await member.add_roles(role_to_add)
        logger.info(f'Добавлена роль {role_to_add.name} у {member.name}|{member.id}')

        answer = self.answer_localization[self.locale].format(role_mention=role_to_add.mention)
        await interaction.respond(answer, ephemeral=True, delete_after=15)

    async def _check_on_cooldown(self, interaction: Interaction) -> bool:
        if await select_role_cooldown.is_user_on_cooldown(interaction.user.id):
            await interaction.respond(
                "Вы недавно уже выбирали роль, попробуйте позже.\n"
                "You've already selected a role recently, try again later.",
                ephemeral=True,
                delete_after=15,
            )
            return True
        else:
            await select_role_cooldown.set_user_cooldown(
                interaction.user.id,
                cooldown_in_seconds=SELECT_ROLE_COOLDOWN_SECOND,
            )
        return False


class SelectRoleView(discord.ui.View):
    def __init__(self):
        buttons = [
            SelectRoleButton(label='English', emoji='🇺🇸', locale=LocaleEnum.en),
            SelectRoleButton(label='Русский', emoji='🇷🇺', locale=LocaleEnum.ru),
        ]
        super().__init__(*buttons, timeout=None)
