# import asyncio
# import aiohttp

# import lemmiwinks
# import lemmiwinks.taskwrapper as taskwrapper
# import lemmiwinks.archive.migration as migration
# import lemmiwinks.httplib as httplib
# import lemmiwinks.pathgen as pathgen
# import lemmiwinks.parslib as parslib
# import lemmiwinks.archive as archive

from schema import ArchiveJsonSchema
from name_generator import ArchiveName
from lemmiwinks_top import ArchiveServiceLemmiwinks
from responses import archive_post_response
from responses import archive_get_response
from responses import info_page_response

# Sanic imports
from sanic import Sanic
from sanic import response
# Sanic Authentication
from sanic_auth import Auth

app = Sanic()

@app.route('/archive', methods=['POST'])
async def post_archive_handler(request):
    return response.json(await archive_post_response(request))

@app.route('/archive', methods=['GET'])
async def get_archive_handler(request):
    return response.html(await archive_get_response(request))

@app.route('/', methods=['GET'])
async def get_root_handler(request):
    return response.html(await info_page_response(request))

if __name__ == "__main__":
  app.run(host="0.0.0.0", port="8080")


