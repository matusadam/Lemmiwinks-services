import requests
import aiohttp
import asyncio

class AsyncTestClient():
    def __init__(self, service_host, auth):
        self.service_host = service_host
        self.api_archives_url = service_host + '/api/archives'
        self.auth = aiohttp.BasicAuth(login=auth[0], password=auth[1])

    async def get_requests(self, params, count):
        tasks = []
        async with aiohttp.ClientSession(auth=self.auth) as session:
            for i in range(count):
                task = asyncio.ensure_future(self._fetch_get(params, session))
                tasks.append(task)

            responses = asyncio.gather(*tasks)
            await responses

    async def post_requests(self, data, count):
        tasks = []
        async with aiohttp.ClientSession(auth=self.auth) as session:
            for i in range(count):
                task = asyncio.ensure_future(self._fetch_post(data, session))
                tasks.append(task)

            responses = asyncio.gather(*tasks)
            await responses

    async def _fetch_get(self, params, session):
        async with session.get(self.api_archives_url, params=params) as response:
            return await response.read()

    async def _fetch_post(self, data, session):
        async with session.post(self.api_archives_url, json=data) as response:
            return await response.read()


class TestClient():
    def __init__(self, service_host, auth):
        self.session = requests.Session()
        self.service_host = service_host
        self.api_archives_url = service_host + '/api/archives'
        self._test_number = 1
        self.auth = auth

    def get_archive(self, data):
        r = self.post_request(data)
        print("  #%d, Status: %d" % (self._test_number, r.status_code))
        if r.status_code == 201:
            location = r.headers.get("Location")
            print("  Location: %s" % (location))
        self._test_number += 1
        return r
        
    def post_request(self, data):
        r = self.session.post(self.api_archives_url, json=data, auth=auth)
        return r

    @property
    def test_number(self):
       	return self._test_number