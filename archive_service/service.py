import asyncio
import aiohttp
from itertools import count
import os

import lemmiwinks
import lemmiwinks.taskwrapper as taskwrapper
import lemmiwinks.archive.migration as migration
import lemmiwinks.httplib as httplib
import lemmiwinks.pathgen as pathgen
import lemmiwinks.parslib as parslib
import lemmiwinks.archive as archive

from schema import ArchiveJsonSchema
from name_generator import ArchiveName
from lemmiwinks_top import ArchiveServiceLemmiwinks

# Sanic imports
from sanic import Sanic
from sanic import response
# Sanic Authentication
from sanic_auth import Auth

app = Sanic()

async def archive_post_response(request):
    # TODO: validate request
    request_json = ArchiveJsonSchema(instance=request.json)
    try:
        request_json.is_valid()
    except ValidationError as e:
        resp = {
            "status" : "Bad request",
            "message" : e,
        }
        return resp

    urls = iter(request.json.get('urls'))

    archive_name = ArchiveName().full_name()

    aio_archive = ArchiveServiceLemmiwinks(urls, archive_name)
    await aio_archive.task_executor()

    resp = {
        "status": "ok",
        "arhive_path" : archive_name,
    }
    return resp

async def archive_get_response(request):
    with open("archive.html", "r", encoding='utf-8') as f:
        archive_page = f.read()
    maff_files = [file for file in os.listdir() if file.endswith(".maff")]
    formated = "".join(["<li>%s</li>" % file for file in maff_files])
    archive_page = archive_page % formated
    return archive_page

async def info_page_response(request):
    with open("index.html", "r", encoding='utf-8') as f:
        info_page = f.read()
    info_page = info_page % request.ip
    return info_page

@app.route('/archive', methods=['POST'])
async def post_handler(request):
    return response.json(await archive_post_response(request))

@app.route('/archive', methods=['GET'])
async def post_handler(request):
    return response.html(await archive_get_response(request))

@app.route('/', methods=['GET'])
async def get_handler(request):
    return response.html(await info_page_response(request))

if __name__ == "__main__":
  app.run(host="0.0.0.0", port="8080")


