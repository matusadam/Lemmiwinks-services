import base64

from sanic import Sanic
from sanic import response
from sanic_token_auth import SanicTokenAuth

from aiohttp import ClientConnectionError

# local imports
from schema import DownloadPostSchema
from client import DownloaderClient, TorDownloaderClient

# Sanic init
app = Sanic()

# Sanic-Token-Auth for API
token_auth = SanicTokenAuth(app, secret_key='Z0SbdsCkNXgrvQSGXqZWTsd0ylWVJasO')

@app.route('/api/download', methods=['POST'])
@token_auth.auth_required
async def post_handler(request):
    if DownloadPostSchema(request.json).is_valid():
        resourceURL = request.json.get('resourceURL')
        headers = request.json.get('headers')
        useTor = request.json.get('useTor')

        if useTor:
            client = TorDownloaderClient(timeout=60, headers=headers)
        else:
            client = DownloaderClient(timeout=60, headers=headers)

        try:
            content_type, url_and_status, data = await client.get_request(resourceURL)
        except ClientConnectionError as e:
            # cannot resolve URL, timeout or refused connection
            return response.json(None, status=204)
        else:
            return response.json(
                {
                    "content-type" : content_type,
                    "url_and_status" : url_and_status,
                    "data" : base64.b64encode(bytes(data)).decode('utf-8')
                }, 
                status=200
            )  
    else:
        # bad request
        return response.json(None, status=400)


@app.route('/', methods=['GET'])
async def get_handler(request):
    with open("index.html", "r", encoding='utf-8') as f:
        html = f.read()
    html = html.format(request.ip)
    return response.html(html)

if __name__ == "__main__":
  app.run(host="0.0.0.0", port="8081")


