from sanic import Sanic
from sanic import response
from sanic.exceptions import InvalidUsage

from schema import DownloaderJsonSchema
from exception_messages import INVALID_USAGE_MESSAGE

from client import DownloaderClient

import aiohttp
import base64
import json

app = Sanic()

def __encode_data(content):
    return base64.b64encode(bytes(content)).decode('utf-8')

async def downloader_post_response(request):  

    request_json = DownloaderJsonSchema(instance=request.json)
    try:
        request_json.is_valid()
    except ValidationError as e:
        raise InvalidUsage(message=INVALID_USAGE_MESSAGE)

    url = request.json.get("resourceURL")

    client = DownloaderClient(timeout=10)
    content, url_and_status = await client.get_request(url)
    del client

    resp = {
        "status": "ok",
        "url_and_status" : url_and_status,
        "data" : __encode_data(content),
    }
    return resp

async def info_page_response(request):
    with open("index.html", "r", encoding='utf-8') as f:
        info_page = f.read()
    info_page = info_page % request.ip
    return info_page

@app.route('/download', methods=['POST'])
async def post_handler(request):
    return response.json(await downloader_post_response(request))

@app.route('/', methods=['GET'])
async def get_handler(request):
    return response.html(await info_page_response(request))



if __name__ == "__main__":
  app.run(host="0.0.0.0", port="8081")


