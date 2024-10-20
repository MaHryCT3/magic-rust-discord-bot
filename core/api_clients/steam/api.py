from typing import Final

from core.clients.http import HTTPClient


class SteamAPI:
    GET_PLAYER_INFO_URL: Final[str] = 'ISteamUser/GetPlayerSummaries/v0002'
    RESOLVE_STEAM_VANITY_URL: Final[str] = 'ISteamUser/ResolveVanityURL/v1/'

    def __init__(self, api_key: str, http_client: HTTPClient | None = None):
        self.http_client = http_client or HTTPClient(base_url='https://api.steampowered.com/')
        self.api_key = api_key

    async def is_profile_exists(self, steam_id: str) -> bool:
        response = await self.http_client.get(
            self.GET_PLAYER_INFO_URL,
            query=self._get_query(steamids=steam_id),
        )

        try:
            players = list(response.json()['response']['players'])
        except (AttributeError, KeyError):
            players = []

        return bool(players)

    async def resolve_steam_url(self, vanity_url: str) -> str | None:
        response = await self.http_client.get(
            url=self.RESOLVE_STEAM_VANITY_URL,
            query=self._get_query(vanityurl=vanity_url),
        )
        response_json = response.json()

        try:
            steamid = response_json['response']['steamid']
        except (AttributeError, KeyError):
            return

        return steamid

    def _get_query(self, **kwargs) -> dict:
        return {'key': self.api_key, **kwargs}
