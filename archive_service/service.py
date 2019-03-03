
import asyncio
import aiohttp


import lemmiwinks
import lemmiwinks.httplib as httplib

from itertools import count
import re

# Sanic imports
from sanic import Sanic
from sanic import response

app = Sanic()

class ArchiveSettings(migration.MigrationSettings):
    http_client = httplib.provider.ClientFactoryProvider.aio_factory.singleton_client
    css_parser = parslib.provider.CSSParserProvider.tinycss_parser
    html_parser = parslib.provider.HTMLParserProvider.bs_parser
    resolver = httplib.resolver.URLResolver
    path_gen = pathgen.FilePathProvider.filepath_generator
    http_js_pool = httplib.ClientPool

class ArchiveServiceLemmiwinks(lemmiwinks.Lemmiwinks):
    def __init__(self, url, archive_name):

        self.__client = httplib.ClientFactoryProvider.aio_factory.singleton_client(pool_limit=500,timeout=10)
        self.__settings = ArchiveSettings()
        self.__envelop = archive.Envelop()
        self.__archive_name = archive_name
        self.__url = url

    async def task_executor(self):
        task = self.__archive_task(self.__url, self.__archive_name)
        await asyncio.gather(task)

    @taskwrapper.task
    async def __archive_task(self, url, archive_name):
        response = await self.__get_request(url)
        await self.__archive_response(response, archive_name)

    async def __get_request(self, url):   
        response = await self.__client.get_request(url)
        return response

    async def __archive_response(self, response, archive_name):
        self.__add_save_response_to_envelop(response)
        await archive.Archive.archive_as_maff(self.__envelop, archive_name)

    def __add_save_response_to_envelop(self, response):
        letter = archive.SaveResponseLetter(response, self.__settings, archive.Mode.NO_JS_EXECUTION)
        self.__envelop.append(letter)


async def make_response(request):
	urls = request.json.get("urls")
	# TODO: sanitise request
	if not urls:
		return response.json(dict())

    # test: 1 url
    url = next(urls)
    archive_name_re = re.compile(r"https?://")
    archive_name = archive_name_re.sub('', url).strip().strip('/').replace('.','_') + "__archive"

    aio_archive = ArchiveServiceLemmiwinks(url, archive_name)
    aio_archive.run()

	return resp

@app.route('/', methods=['POST'])
async def post_handler(request):
	return response.json(await make_response(request))

if __name__ == "__main__":
  app.run(host="0.0.0.0", port="8080")


