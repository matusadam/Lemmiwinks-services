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
    def __init__(self, archive_data, archive_name, download_service_url='http://0.0.0.0:8081'):

        api_download_url = download_service_url + '/api/download'
        self.__client = httplib.ClientFactoryProvider.service_factory.singleton_client(timeout=60, 
        	api_download_url=api_download_url, 
        	archive_data=archive_data)
        self.__settings = ArchiveSettings()
        self.__envelop = archive.Envelop()
        self.__archive_name = archive_name
        self.__urls = archive_data['urls']
        self.__download_service_url = download_service_url 


    async def task_executor(self):
        task = self.__archive_task()
        await asyncio.gather(task)

    @taskwrapper.task
    async def __archive_task(self):
        responses = await self.__post_requests()
        await self.__archive_responses(responses, self.__archive_name)

    async def __post_requests(self):
        tasks = list()
        # task for every url
        for url in self.__urls:
            task = self.__client.post_request(url, data=self.__make_data_from(url)) 
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        return responses

    async def __archive_responses(self, responses, archive_name):
        for response in responses:
            self.__add_save_response_to_envelop(response)
        await archive.Archive.archive_as_maff(self.__envelop, archive_name)


    def __make_data_from(self, url):
        return {
            "resourceURL" : url,
            "headers" : {},
            "useTor" : False,
        }

    def __add_save_response_to_envelop(self, response):
        letter = archive.SaveResponseLetter(response, self.__settings, archive.Mode.NO_JS_EXECUTION)
        self.__envelop.append(letter)