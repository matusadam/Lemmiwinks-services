import base64

from sanic import Sanic
from sanic import response

from aiohttp import ClientConnectionError, InvalidURL

# local imports
from schema import DownloadPostSchema
from client import DownloaderClient

# Sanic init
app = Sanic()


@app.route('/api/download', methods=['POST'])
async def api_post_download(request):
    if DownloadPostSchema(request.json).is_valid():
        resourceURL = request.json.get('resourceURL')
        headers = request.json.get('headers')
        useTor = request.json.get('useTor')

        client = DownloaderClient(timeout=60, headers=headers, useTor=useTor)

        try:
            content_type, url_and_status, data = await client.get_request(resourceURL)
        except InvalidURL as e:
            # cannot resolve resourceURL
            print(e)
            return response.json(None, status=400)
        except ClientConnectionError as e:
            # timeout or refused connection
            print(e)
            return response.json(None, status=204)
        else:
            # OK
            return response.json(
                {
                    "content-type" : content_type,
                    "url_and_status" : url_and_status,
                    "data" : base64.b64encode(bytes(data)).decode('utf-8')
                }, 
                status=200
            )  
    else:
        # bad JSON schema
        return response.json(None, status=400)


@app.route('/', methods=['GET'])
async def get_index(request):
    with open("www/index.html", "r", encoding='utf-8') as f:
        html = f.read()
    html = html.format(request.ip)
    return response.html(html)

if __name__ == "__main__":
  app.run(host="0.0.0.0", port="8081")


