import re
from typing import Final

from core.api_clients.steam.api import SteamAPI
from core.clients.http import HTTPClient


class SteamProfileValidator:
    """
    Получает на вход стимайди/ссылку со стимайди/кастомную ссылку
    Проверяет существуют ли такой стим и возвращает стимайди
    """

    STEAM_ID_LENGTH: Final[int] = 17
    STEAM_LINK_WITH_ID_REGEX: Final[str] = r'steamcommunity\.com/profiles/(\d{17})/?'
    STEAM_LINK_WITH_VANITY_URL_REGEX: Final[str] = r'steamcommunity\.com\/id\/([a-zA-Z0-9_-]+)\/?'

    STEAM_PROFILE_DEFAULT_URL: Final[str] = 'https://steamcommunity.com/profiles/{steam_id}'

    STEAM_PROFILE_ERROR_SIGN = 'error_ctn'

    def __init__(
        self,
        steam_api: SteamAPI,
    ):
        self.steam_api = steam_api
        self.http_client = HTTPClient()

    async def validate(
        self,
        steam: str,
        validate_on_exists: bool = False,
    ) -> str | None:
        steam = steam.strip()
        steam_id = None

        # проверяем может у нас уже стимайди
        if self._is_steamid(steam):
            steam_id = steam

        # проверяем если эта ссылка в которой дефолтный стимайди
        elif steam_id := self._get_steam_id_from_url(steam):
            pass
        # если мы уже достали стимайди, то проверяем или возращаем его
        if steam_id:
            if validate_on_exists and not await self._check_profile_is_exists(steam_id):
                return
            return steam_id

        # последний шанс, это если это кастоная ссылка на профиль
        elif custom_id := self._get_steam_custom_id(steam):
            steam_id = await self.steam_api.resolve_steam_url(custom_id)

        return steam_id

    def _is_steamid(self, steam: str) -> bool:
        if steam.isalnum() and len(steam) == self.STEAM_ID_LENGTH:
            return True
        return False

    def _get_steam_id_from_url(self, steam) -> str:
        # проверяем случай что ссылка со стимайди
        matched_steam_with_id = re.findall(self.STEAM_LINK_WITH_ID_REGEX, steam)
        if matched_steam_with_id:
            return matched_steam_with_id[0]

    def _get_steam_custom_id(self, steam: str) -> str | None:
        custom_url_match = re.findall(self.STEAM_LINK_WITH_VANITY_URL_REGEX, steam)
        if custom_url_match:
            return custom_url_match[0]

    async def _check_profile_is_exists(self, steam_id: str) -> bool:
        steam_url = self.STEAM_PROFILE_DEFAULT_URL.format(steam_id=steam_id)
        response = await self.http_client.get(steam_url, follow_redirects=True)
        if self.STEAM_PROFILE_ERROR_SIGN in response.text:
            return False
        return True
