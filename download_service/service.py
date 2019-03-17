from sanic import Sanic
from sanic import response

import aiohttp
import base64
import json

app = Sanic()

class AIOClient():
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
        try:
            content, url_and_status = await self.__get_response_from(url)
        except Exception as e:
            self._logger.error(f"Cannot connect to host {url}")
            raise exception.HTTPClientConnectionFailed(e)
        else:
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

def __encode_data(content):
    return base64.b64encode(bytes(content)).decode('utf-8')

async def make_response(request):

    url = request.json.get("resourceURL")

    # TODO: sanitise request
    if not url:
        return response.json(dict())

    client = AIOClient(timeout=10)
    content, url_and_status = await client.get_request(url)
    del client

    resp = {
        "status": "ok",
        "url_and_status" : url_and_status,
        "type" : 'TODO',
        "data" : __encode_data(content),
    }
    return resp

@app.route('/', methods=['POST'])
async def post_handler(request):
    return response.json(await make_response(request))


if __name__ == "__main__":
  app.run(host="0.0.0.0", port="8081")


