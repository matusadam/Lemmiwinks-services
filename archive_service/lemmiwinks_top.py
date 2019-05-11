import asyncio
import lemmiwinks
import lemmiwinks.taskwrapper as taskwrapper
import lemmiwinks.archive.migration as migration
import lemmiwinks.httplib as httplib
import lemmiwinks.pathgen as pathgen
import lemmiwinks.parslib as parslib
import lemmiwinks.archive as archive

from urllib.parse import urlparse

class ArchiveSettings(migration.MigrationSettings):
    http_client = httplib.provider.ClientFactoryProvider.service_factory.singleton_client
    css_parser = parslib.provider.CSSParserProvider.tinycss_parser
    html_parser = parslib.provider.HTMLParserProvider.bs_parser
    resolver = httplib.resolver.URLResolver
    path_gen = pathgen.FilePathProvider.filepath_generator
    http_js_pool = httplib.ClientPool

class ArchiveServiceLemmiwinks(lemmiwinks.Lemmiwinks):
    def __init__(self, urls, archive_name):

        self.__client = httplib.ClientFactoryProvider.service_factory.singleton_client(pool_limit=500,timeout=60)
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
            useTor = self.__is_onion_address(url)
            task = self.__client.post_request(self.__download_service_url, data=self.__make_data_from(url, useTor)) 
            tasks.append(task)

        #responses = list()
        responses = await asyncio.gather(*tasks)

        return responses

    async def __archive_responses(self, responses, archive_name):
        for response in responses:
            self.__add_save_response_to_envelop(response)
        await archive.Archive.archive_as_maff(self.__envelop, archive_name)

    def __is_onion_address(self, url):
        url_netloc = urlparse(url).netloc
        return url_netloc.endswith(".onion")

    def __make_data_from(self, url, useTor):
        data = {
            "resourceURL" : url,
            "useTor" : useTor
        }
        return data

    def __add_save_response_to_envelop(self, response):
        letter = archive.SaveResponseLetter(response, self.__settings, archive.Mode.NO_JS_EXECUTION)
        self.__envelop.append(letter)