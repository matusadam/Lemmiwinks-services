from sanic.exceptions import InvalidUsage

from schema import DownloaderJsonSchema
from jsonschema import ValidationError
from exception import INVALID_USAGE_MESSAGE

from client import DownloaderClient
from client import TorDownloaderClient

import base64
import json

def __encode_data(content):
    return base64.b64encode(bytes(content)).decode('utf-8')

async def downloader_post_response(request):  

    request_json = DownloaderJsonSchema(instance=request.json)
    try:
        request_json.is_valid()
    except ValidationError as e:
        raise InvalidUsage(message=INVALID_USAGE_MESSAGE)

    url = request.json.get("resourceURL")
    useTor = request.json.get("useTor")

    if useTor:
        client = TorDownloaderClient(timeout=60)
    else:
        client = DownloaderClient(timeout=60)

    try:
        content, url_and_status = await client.get_request(url)
    except Exception as e:
        resp = {
            "errorMessage" : e,
            "url_and_status" : [],
            "data" : "",
        }
    else:
        resp = {
            "url_and_status" : url_and_status,
            "data" : __encode_data(content),
        }

    return resp

async def info_page_response(request):
    with open("index.html", "r", encoding='utf-8') as f:
        info_page = f.read()
    info_page = info_page % request.ip
    return info_page