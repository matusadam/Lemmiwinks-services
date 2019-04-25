from sanic import Sanic
from sanic import response

from responses import downloader_post_response
from responses import info_page_response

app = Sanic()

@app.route('/download', methods=['POST'])
async def post_handler(request):
    return response.json(await downloader_post_response(request))

@app.route('/', methods=['GET'])
async def get_handler(request):
    return response.html(await info_page_response(request))

if __name__ == "__main__":
  app.run(host="0.0.0.0", port="8081")


