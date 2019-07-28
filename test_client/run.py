import asyncio
import time
import json

from test_client import AsyncTestClient, TestClient

def run_async_get_test():
    t = AsyncTestClient(service_host="http://0.0.0.0:8080", auth=('admin', 'admin'))
    params = [
        {}, 
        {'name': 'RealArchive'},
        {'limit': '10'},
        {'skip': '50'},
    ]
    count = 10000
    loop = asyncio.get_event_loop()

    for p in params:
        future = asyncio.ensure_future(t.get_requests(params=p, count=count))
        timing_start = time.time()
        loop.run_until_complete(future)
        timing_end = time.time()
        timing = timing_end - timing_start
        print("Time: {} for {} async GET requests with params: {}".format(timing, count, p) )


def run_async_post_test():
    t = AsyncTestClient(service_host="http://0.0.0.0:8080", auth=('admin', 'admin'))
    data = {
        'urls' : [ 'http://0.0.0.0:8000/' ],
        'name' : "Test",
        'headers' : {},
        'forceTor' : False,
    }
    count = 200
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(t.post_requests(data, count=count))

    timing_start = time.time()
    loop.run_until_complete(future)
    timing_end = time.time()
    timing = timing_end - timing_start
    print("Time: {} for {} async POST requests".format(timing, count) )


def run_deepweb_test(): 
    t = TestClient(service_host="http://0.0.0.0:8080", auth=('admin', 'admin'))

    test_files_dict = {
        "Hidden Service lists and search engines" : "test_link_sites.json",
        "Marketplace Financial" : "test_finance.json",
        "Marketplace Commercial Services" : "test_commercial_services.json",
        "Blogs and radios" : "test_blogs.json",
        "Politics" : "test_politics.json"
    }

    for tests_name, tests_file in test_files_dict.items():
        print("======================================================================")
        print("Website group: %s from file %s" % (tests_name, tests_file))
        print("======================================================================")
        with open(tests_file) as f:
            tests_json = json.load(f)
            # Get archives for each individual page
            for web_name, url in tests_json.items():
                print("Website: %s, URL: %s" % (web_name, url) )
                data = {
                    'urls' : [ url ],
                    'name' : "DeepWebTest-{}".format(t.test_number),
                    'headers' : {},
                    'forceTor' : True,
                }

                timing_start = time.time()
                t.get_archive(data=data)
                timing_end = time.time()
                print("  archiving request time: %s" % (timing_end - timing_start))


if __name__ == "__main__":
    run_async_get_test()
    run_async_post_test()
    run_deepweb_test()
