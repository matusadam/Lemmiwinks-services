import aiohttp
from aiohttp_socks import SocksConnector

class DownloaderClient():
    def __init__(self, pool_limit=30, timeout=60,
                 proxy=None, headers=None, cookies=None):

        self.timeout = timeout
        self.proxy = proxy
        self.headers = headers
        self.cookies = cookies

        connector = aiohttp.TCPConnector(limit=pool_limit)
        self.__session = aiohttp.ClientSession(connector=connector,
                                               cookies=cookies)

    def __del__(self):
        self.__session.close()

    async def get_request(self, url):
        content, url_and_status = await self.__get_response_from(url)
        return (content, url_and_status)

    async def __get_response_from(self, url):
        async with self.__session.get(url, timeout=self.timeout) as response:
            url_and_status = self.__get_url_and_status_from(response)
            content = await response.content.read()
        return (content, url_and_status)

    @staticmethod
    def __get_url_and_status_from(response):
        url_and_status = [(str(record.url), record.status) for record in response.history]
        url_and_status.append((str(response.url), response.status))
        return url_and_status

class TorDownloaderClient():
    def __init__(self, timeout=60, connector_url="socks5://localhost:9050"):

        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; rv:31.0) Gecko/20100101 Firefox/31.0'}
        self.timeout = timeout
        self.connector_url = connector_url
        connector = SocksConnector.from_url(self.connector_url, rdns=True)
        self.__session = aiohttp.ClientSession(connector=connector)

    async def get_request(self, url):
        content, url_and_status = await self.__get_response_from(url)
        return (content, url_and_status)

    async def __get_response_from(self, url):
        async with self.__session.get(url, timeout=self.timeout, headers=self.headers) as response:
            url_and_status = self.__get_url_and_status_from(response)
            content = await response.content.read()
        return (content, url_and_status)

    @staticmethod
    def __get_url_and_status_from(response):
        url_and_status = [(str(record.url), record.status) for record in response.history]
        url_and_status.append((str(response.url), response.status))
        return url_and_status