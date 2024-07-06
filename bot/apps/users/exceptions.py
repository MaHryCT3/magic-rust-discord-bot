from discord.ext.commands.errors import CommandError


class UserError(CommandError):
    message: str


class UserHasNotRoleError(UserError):
    message: str = 'Выберите язык в канале для выбора языка'
