from urllib.parse import urljoin

import aiohttp
from aiohttp.log import client_logger as logger


class HTTPClient:
    def __init__(self, base_url: str = '', headers: dict | None = None) -> None:
        self.client = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60 * 30), headers=headers)
        self.base_url = base_url

    async def request(
        self,
        url: str,
        http_method: str,
        query: dict | None = None,
        payload: dict | None = None,
        body: str | None = None,
        **kwargs,
    ) -> aiohttp.ClientResponse:
        url = urljoin(self.base_url, url)
        logger.debug(f'Make request: {http_method}: {url} | Query: {query} | Payload: {payload} | Body: {body}')
        response = await self.client.request(http_method, url, params=query, data=payload, json=body, **kwargs)
        await response.read()
        logger.debug(
            f'Receive response {response.request_info.method} {response.request_info.real_url}: {await response.text()}'
        )
        response.raise_for_status()
        return response

    async def get(
        self,
        url: str,
        query: dict | None = None,
        headers: dict | None = None,
    ):
        return await self.request(
            url,
            http_method='GET',
            query=query,
            headers=headers,
        )

    async def post(
        self,
        url: str,
        query: dict | None = None,
        payload: dict | None = None,
        body: str | None = None,
        headers: dict | None = None,
    ):
        return await self.request(
            url,
            http_method='POST',
            query=query,
            payload=payload,
            body=body,
            headers=headers,
        )

    def __del__(self):
        if self.client and not self.client.closed:
            if self.client._connector is not None and self.client._connector_owner:
                self.client._connector._close()
            self.client._connector = None
