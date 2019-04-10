import random
import string
from datetime import datetime

class ArchiveName():

    def __init__(self, timestamp=None, urls=None):
        self._timestamp = self.__create_timestamp(timestamp)
        self._urls = urls
        self._id = self.__generate_random_id()

    def __generate_random_id(self):
        archive_id = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))
        return archive_id

    def __create_timestamp(self, timestamp):
        # expects datetime object as a timestamp
        if timestamp == None:
            archive_timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")  
        else:
            archive_timestamp = timestamp.strftime("%Y%m%dT%H%M%S")

        return archive_timestamp

    def full_name(self):
        return "%s_%s" % (self._timestamp, self._id)

    @property
    def id(self):
        return self._id

    @property
    def timestamp(self):
        return self._timestamp
    
    