import os, re
import zipfile
from datetime import datetime

class Archives():
    """Represents all existing archive maff files.

    """

    def __init__(self):
        self._files = [file for file in os.listdir() if file.endswith(".maff")]
        
    def details(self):
        archive_details = []
        for file in self._files:
            archive_details.append(self.detail(file))
        return archive_details

    def detail(self, file):
        m = re.match(r'^([A-Za-z0-9-]+)_([a-z0-9]+)\.maff', file)
        _stats = os.stat(file)
        return {
            'file' : file,
            'name' : m.group(1),
            'aid' : m.group(2),
            'ctime' : datetime.fromtimestamp(_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
            'size' : _stats.st_size,
            'href_download' : '/archives/{}/{}'.format(m.group(2), file),
            'href_download_api' : '/api/archives/{}/{}'.format(m.group(2), file),
            'href_detail' : '/archives/{}'.format(m.group(2)),
            'href_detail_api' : '/api/archives/{}'.format(m.group(2)) 
        }

    def searchById(self, search_id):
        for file in self._files:
            m = re.match(r'^([A-Za-z0-9-]+)_([a-z0-9]+)\.maff', file)
            aid = m.group(2)
            if aid == search_id:
                return self.detail(file)
        # not found
        return None

    def searchByName(self, search_name):
        archive_details = []
        for file in self._files:
            m = re.match(r'^([A-Za-z0-9-]+)_([a-z0-9]+)\.maff', file)
            name = m.group(1)
            if search_name in name:
                archive_details.append( self.detail(file) )
        return archive_details


    @property
    def files(self):
        return self._files
    
