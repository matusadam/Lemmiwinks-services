import aiohttp

class DownloaderClient():
    def __init__(self, pool_limit=30, timeout=None,
                 proxy=None, headers=None, cookies=None):

        self.timeout = timeout
        self.proxy = proxy
        self.headers = headers
        self.cookies = cookies
        self.__chunk_size = 4096

        connector = aiohttp.TCPConnector(limit=pool_limit)
        self.__session = aiohttp.ClientSession(connector=connector,
                                               cookies=cookies)

    def __del__(self):
        self.__session.close()

    async def get_request(self, url):
        content, url_and_status = await self.__get_response_from(url)
        return (content, url_and_status)

    async def __get_response_from(self, url):
        async with self.__session.get(url) as response:
            url_and_status = self.__get_url_and_status_from(response)
            content = await response.content.read()
        return (content, url_and_status)

    @staticmethod
    def __get_url_and_status_from(response):
        url_and_status = [(str(record.url), record.status) for record in response.history]
        url_and_status.append((str(response.url), response.status))
        return url_and_status