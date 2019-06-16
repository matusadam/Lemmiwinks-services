
import os
import re

from schema import ArchiveJsonSchema
from name_generator import ArchiveName
from lemmiwinks_top import ArchiveServiceLemmiwinks
from responses import archive_post
from responses import archive_get
from responses import index_get

# Sanic imports
from sanic import Sanic
from sanic import response
# Sanic Authentication
from sanic_auth import Auth

app = Sanic()

@app.route('/archive', methods=['POST'])
async def post_archive_handler(request):
    return response.json(await archive_post(request))

@app.route('/archive', methods=['GET'])
async def get_archive_handler(request):
    return response.html(await archive_get(request))

@app.route('/archive/<name>', methods=['GET'])
async def get_archive_download_handler(request, name):
    # match archive name
    m = re.match(r'[0-9]+T[0-9]+_[0-9A-Z]+\.maff', name)
    if not m:
        return response.json(
            {
                "error": "Bad request: archive name does not match",
                "status" : 400
            },
            status=400
        )

    # return maff if exists
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    for f in files:
        if name in f:
            return await response.file(f)

    # archive doesnt exist
    return response.json(
            {
                "error": "Archive %s not found" % (name,),
                "status" : 404
            },
            status=404
        )


@app.route('/', methods=['GET'])
async def get_root_handler(request):
    return response.html(await index_get(request))

if __name__ == "__main__":
  app.run(host="0.0.0.0", port="8080")


