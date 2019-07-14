import aiohttp
from aiohttp_socks import SocksConnector

class DownloaderClient():
    def __init__(self, pool_limit=30, timeout=60,
                 proxy=None, headers=None, cookies=None):
        self.pool_limit = pool_limit
        self.timeout = timeout
        self.proxy = proxy
        self.headers = headers
        self.cookies = cookies

    async def get_request(self, url):
        content_type, url_and_status, data = await self._get_response_from(url)
        return (content_type, url_and_status, data)

    async def _get_response_from(self, url):
        connector = await self.__get_connector()
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url, timeout=self.timeout, headers=self.headers) as response:
                content_type = response.headers.get('Content-Type')
                url_and_status = self._get_url_and_status_from(response)
                data = await response.content.read()       
        return (content_type, url_and_status, data)

    async def __get_connector(self):
        return aiohttp.TCPConnector(limit=self.pool_limit)

    @staticmethod
    def _get_url_and_status_from(response):
        url_and_status = [(str(record.url), record.status) for record in response.history]
        url_and_status.append((str(response.url), response.status))
        return url_and_status

class TorDownloaderClient(DownloaderClient):
    """Client with Tor connector

    Uses SocksConnector instead of TCPConnector.
    By default Tor should run on localhost:9050
    """
    def __init__(self, pool_limit=30, timeout=60, 
                 proxy=None, headers=None, cookies=None, 
                 connector_url="socks5://localhost:9050"):

        super().__init__(pool_limit=pool_limit, timeout=timeout, proxy=proxy,
                         headers=headers, cookies=cookies)

        self.connector_url = connector_url

    async def __get_connector(self):
        return SocksConnector.from_url(self.connector_url, rdns=True)