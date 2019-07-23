import random
import string
from datetime import datetime

class ArchiveName():

    def __init__(self, name=None, timestamp=None, urls=None):  
        self._name = self.__create_name(name)
        self._timestamp = self.__create_timestamp(timestamp)
        self._urls = urls
        self._id = self.__generate_random_id()

    def __create_name(self, name):
        if name == None or name == '':
            archive_name = "unnamed"
        else:
            archive_name = name
        return archive_name

    def __create_timestamp(self, timestamp):
        # expects datetime object as a timestamp
        if timestamp == None:
            archive_timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")  
        else:
            archive_timestamp = timestamp.strftime("%Y%m%dT%H%M%S")

        return archive_timestamp

    def __generate_random_id(self):
        archive_id = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(8))
        return archive_id

    @property 
    def full_name(self):
        return "{}_{}".format(self._name, self._id)

    @property 
    def filename(self):
        return "{}.maff".format(self.full_name)

    @property
    def id(self):
        return self._id

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def name(self):
        return self._name

    @property
    def href_detail(self):
        return "/archives/{}".format(self._id)

    @property
    def href_download(self):
        return "/archives/{}/{}".format(self._id, self.filename)
    
    @property
    def href_detail_api(self):
        return "/api/archives/{}".format(self._id)

    @property
    def href_download_api(self):
        return "/api/archives/{}/{}".format(self._id, self.filename)