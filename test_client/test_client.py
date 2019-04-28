import requests
import json

class TestClient():
    def __init__(self, service_url):
        self.session = requests.Session()
        self.service_url = service_url
        self.test_n = 1

    def get_archive(self, urls):
        r = self.post_req(urls)
        print("  Test number: %d, Status: %d" % (self.test_n, r.status_code))
        self.test_n += 1
        return r
        
    def post_req(self, urls):
        r = self.session.post(self.service_url, json={"urls":urls})
        return r
        
if __name__ == "__main__":

    t = TestClient(service_url="http://0.0.0.0:8080/archive")

    test_files_dict = {
        "Hidden Service lists and search engines" : "test_link_sites.json",
        "Marketplace Financial" : "test_finance.json",
        "Marketplace Commercial Services" : "test_commercial_services.json",
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
                urls = list()
                urls.append(url)
                t.get_archive(urls=urls)

            # Now request all pages from this group into single archive
            


    

