import os, re

class Archives():
    """Represents all existing archive maff files.

    """

    def __init__(self):
        self._files = [file for file in os.listdir() if file.endswith(".maff")]
        
    def details(self):
        file_details = []
        for file in self._files:
            m = re.match(r'^([A-Za-z0-9-]+)_([a-z0-9]+)\.maff', file)
            _stats = os.stat(file)
            file_details.append({
                'file' : file,
                'name' : m.group(1),
                'aid' : m.group(2),
                'ctime' : _stats.st_ctime,
                'size' : _stats.st_size,
                'href_download' : '/archives/{}/{}'.format(m.group(2), file),
                'href_detail' : '/archives/{}'.format(m.group(2)),
                'href_detail_api' : '/api/archives/{}'.format(m.group(2)) 
            })
        return file_details

    def searchById(self, search_id):
        for file in self._files:
            m = re.match(r'^([A-Za-z0-9-]+)_([a-z0-9]+)\.maff', file)
            aid = m.group(2)
            if aid == search_id:
                _stats = os.stat(file)
                return {
                    'file' : file,
                    'name' : m.group(1),
                    'aid' : m.group(2),
                    'ctime' : _stats.st_ctime,
                    'size' : _stats.st_size,
                    'href_download' : '/archives/{}/{}'.format(m.group(2), file),
                    'href_detail' : '/archives/{}'.format(m.group(2)),
                    'href_detail_api' : '/api/archives/{}'.format(m.group(2))
                }
        # not found
        return None

    def searchByName(self, search_name):
        details = list()
        for file in self._files:
            m = re.match(r'^([A-Za-z0-9-]+)_([a-z0-9]+)\.maff', file)
            name = m.group(1)
            if search_name in name:
                _stats = os.stat(file)
                details.append({
                    'file' : file,
                    'name' : m.group(1),
                    'aid' : m.group(2),
                    'ctime' : _stats.st_ctime,
                    'size' : _stats.st_size,
                    'href_download' : '/archives/{}/{}'.format(m.group(2), file),
                    'href_detail' : '/archives/{}'.format(m.group(2)),
                    'href_detail_api' : '/api/archives/{}'.format(m.group(2))
                })
        return details


    @property
    def files(self):
        return self._files
    
