import requests
import json
import time

class TestClient():
    def __init__(self, service_host, headers):
        self.session = requests.Session()
        self.service_host = service_host
        self.api_archives_url = service_host + '/api/archives'
        self._test_number = 1
        self.headers = headers

    def get_archive(self, data):
        r = self.post_req(data)
        if r.status_code == 201:
            location = r.headers.get("Location")
            print("  Test number: %d, Status: %d, Archive: %s" % (self._test_number, r.status_code, location))
        else:
            print("  Test number: %d, Status: %d" % (self._test_number, r.status_code))
        self._test_number += 1
        return r
        
    def post_req(self, data):
        r = self.session.post(self.api_archives_url, json=data, headers=self.headers)
        return r

    @property
    def test_number(self):
       	return self._test_number
       

        
if __name__ == "__main__":

    auth_headers = {'Authorization': 'Token Z0SbdsCkNXgrvQSGXqZWTsd0ylWVJasO'}
    t = TestClient(service_host="http://0.0.0.0:8080", headers=auth_headers)

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
            


    

