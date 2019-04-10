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

# Sanic imports
from sanic import Sanic
from sanic import response

app = Sanic()

class ArchiveSettings(migration.MigrationSettings):
    http_client = httplib.provider.ClientFactoryProvider.service_factory.singleton_client
    css_parser = parslib.provider.CSSParserProvider.tinycss_parser
    html_parser = parslib.provider.HTMLParserProvider.bs_parser
    resolver = httplib.resolver.URLResolver
    path_gen = pathgen.FilePathProvider.filepath_generator
    http_js_pool = httplib.ClientPool

class ArchiveServiceLemmiwinks(lemmiwinks.Lemmiwinks):
    def __init__(self, urls, archive_name):

        self.__client = httplib.ClientFactoryProvider.service_factory.singleton_client(pool_limit=500,timeout=10)
        self.__settings = ArchiveSettings()
        self.__envelop = archive.Envelop()
        self.__archive_name = archive_name
        self.__urls = urls
        self.__download_service_url = 'http://0.0.0.0:8081/download'

    async def task_executor(self):
        task = self.__archive_task(self.__urls, self.__archive_name)
        await asyncio.gather(task)

    @taskwrapper.task
    async def __archive_task(self, urls, archive_name):
        responses = await self.__post_requests(urls)
        await self.__archive_responses(responses, archive_name)

    async def __post_requests(self, urls):
        tasks = list()
        # task for every url
        for url in urls:
            task = self.__client.post_request(self.__download_service_url, data=self.__make_data_from(url)) 
            tasks.append(task)

        #responses = list()
        responses = await asyncio.gather(*tasks)

        return responses

    @staticmethod
    def __make_data_from(url):
        data = {
            "mainURL" : url,
            "resourceURL" : url,
        }
        return data

    async def __archive_responses(self, responses, archive_name):
        for response in responses:
            self.__add_save_response_to_envelop(response)
        await archive.Archive.archive_as_maff(self.__envelop, archive_name)

    def __add_save_response_to_envelop(self, response):
        letter = archive.SaveResponseLetter(response, self.__settings, archive.Mode.NO_JS_EXECUTION)
        self.__envelop.append(letter)


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


