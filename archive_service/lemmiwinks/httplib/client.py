import tempfile
import base64
import asyncio

# third party imports
import aiohttp
from selenium import webdriver

# local imports
from . import container
from . import exception
from . import abstract
from urllib.parse import urlparse

class AIOClient(abstract.AsyncClient):
    def __init__(self, pool_limit=30, timeout=None,
                 proxy=None, headers=None, cookies=None):

        super().__init__("{}.{}".format(__name__, self.__class__.__name__))

        self.timeout = timeout
        self.proxy = proxy
        self.headers = headers
        self.cookies = cookies
        self.__chunk_size = 4096

        connector = aiohttp.TCPConnector(limit=pool_limit)
        self.__session = aiohttp.ClientSession(connector=connector,
                                               cookies=cookies)

    async def __del__(self):
        await self.__session.close()

    async def get_request(self, url) -> container.Response:
        try:
            content_descriptor, url_and_status = await self.__get_response_from(url)
        except Exception as e:
            self._logger.error(f"Cannot connect to host {url}")
            raise exception.HTTPClientConnectionFailed(e)
        else:
            return container.Response(content_descriptor, url_and_status)

    async def __get_response_from(self, url):
        async with self.__session.get(url,
                                      headers=self.headers,
                                      timeout=self.timeout,
                                      proxy=self.proxy.url,
                                      proxy_auth=self.proxy.auth) as response:

            url_and_status = self.__get_url_and_status_from(response)
            content_descriptor = await self.__get_content_descriptor_from(response)

        return content_descriptor, url_and_status

    @staticmethod
    def __get_url_and_status_from(response):
        url_and_status = [(str(record.url), record.status) for record in response.history]

        url_and_status.append((str(response.url), response.status))
        return url_and_status

    async def __get_content_descriptor_from(self, response):
        content_descriptor = tempfile.NamedTemporaryFile()

        async for data in response.content.iter_chunked(self.__chunk_size):
            content_descriptor.write(data)

        return content_descriptor

    def post_request(self, url, data):
        pass

    @abstract.AsyncClient.proxy.setter
    def proxy(self, proxy: container.Proxy):
        try:
            auth = aiohttp.BasicAuth(proxy.login, proxy.password)
            self._proxy = container.AIOProxy(proxy.url, auth)
        except AttributeError:
            self._proxy = container.AIOProxy(None, None)

class ServiceClient(abstract.AsyncClient):
    def __init__(self, pool_limit=30, timeout=None,
                 proxy=None, headers=None, cookies=None,
                 api_download_url='http://0.0.0.0:8081/api/download',
                 archive_data=None):

        super().__init__("{}.{}".format(__name__, self.__class__.__name__))

        self.timeout = timeout
        self.proxy = proxy
        self.cookies = cookies

        self.headers = headers
        self.api_download_url = api_download_url
        if archive_data:
        	self.archive_data = archive_data
        else:
        	self.archive_data = {
        		'forceTor' : False,
        		'headers' : {},
        	}
        self.__chunk_size = 4096
        

        connector = aiohttp.TCPConnector(limit=pool_limit)
        self.__session = aiohttp.ClientSession(connector=connector,
                                               cookies=cookies)

    def __del__(self):
        self.__session.close()

    async def get_request(self, url) -> container.Response:
        raise NotImplemented

    async def post_request(self, url, data) -> container.Response:
        # use download service API for all post requests
        data['headers'] = self.archive_data['headers']
        if self.archive_data['forceTor']:
            data['useTor'] = True
        else:
            data['useTor'] = self.__is_onion_address(data['resourceURL'])
        try:
            content_descriptor, url_and_status = await self.__post_response_from(data)
        except Exception as e:
            print(e)
            raise exception.HTTPClientConnectionFailed(e)
        else:
            return container.Response(content_descriptor, url_and_status)

    async def __post_response_from(self, data):
        async with self.__session.post(self.api_download_url,
                                      json=data,
                                      headers=self.headers,
                                      timeout=self.timeout,
                                      proxy=self.proxy.url,
                                      proxy_auth=self.proxy.auth) as response:

            if response.status == 200:
                url_and_status = await self.__get_url_and_status_from(response)
                content_descriptor = await self.__get_content_descriptor_from(response)          
            else:
                # request nefungoval uplne, neco se nestahlo
                url_and_status = [ ( data['resourceURL'], 500) ]
                content_descriptor = tempfile.NamedTemporaryFile()
            return content_descriptor, url_and_status


    async def __get_url_and_status_from(self, response):
        resp_json = await response.json()
        if resp_json and 'url_and_status' in resp_json:
            return resp_json['url_and_status']
    

    async def __get_content_descriptor_from(self, response):
        resp_json = await response.json()
        content_descriptor = tempfile.NamedTemporaryFile()        
        if resp_json and 'data' in resp_json:        
            response_data = base64.b64decode(resp_json['data'])        
            content_descriptor.write(response_data)
        return content_descriptor

    def __is_onion_address(self, url):
        url_netloc = urlparse(url).netloc
        return url_netloc.endswith(".onion")

    @abstract.AsyncClient.proxy.setter
    def proxy(self, proxy: container.Proxy):
        try:
            auth = aiohttp.BasicAuth(proxy.login, proxy.password)
            self._proxy = container.AIOProxy(proxy.url, auth)
        except AttributeError:
            self._proxy = container.AIOProxy(None, None)


class SeleniumClient(abstract.AsyncJsClient):
    def __init__(self, executor_url: str, browser_info, timeout=3, cookies=dict()):
        super().__init__("{}.{}".format(__name__, self.__class__.__name__))
        self.__timeout = timeout
        self.cookies = cookies
        self.__driver = webdriver.Remote(
            command_executor=executor_url,
            desired_capabilities=browser_info)
        self.__driver.set_window_size(1920, 1080)

    def __del__(self):
        self.__driver.close()

    @abstract.AsyncJsClient.cookies.setter
    def cookies(self, cookies: dict):
        self._cookies = cookies

    async def get_request(self, url):
        try:
            await self.__send_request(url)
            content_descriptor, url_and_status = self.__get_response()
        except Exception as e:
            self._logger.error(f"Cannot connect to host {url}")
            raise exception.HTTPClientConnectionFailed(e)
        else:
            return container.Response(content_descriptor, url_and_status)

    async def __send_request(self, url):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.__driver.get, url)
        await asyncio.sleep(self.__timeout)

    def __get_response(self):
        content_descriptor = self.__get_content_descriptor()
        url_and_status = self.__get_url_and_status()

        return content_descriptor, url_and_status

    def __get_url_and_status(self):
        url = self.__driver.current_url
        return [(url, None)]

    def __get_content_descriptor(self):
        content_descriptor = tempfile.NamedTemporaryFile()

        content_descriptor.write(self.__driver.page_source.encode('utf-8'))
        return content_descriptor

    async def save_screenshot_to(self, filepath):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.__driver.save_screenshot, filepath)
