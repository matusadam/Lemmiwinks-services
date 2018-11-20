from sanic import Sanic
from sanic import response

import aiohttp

app = Sanic()

async def get(session, url):
    try:
        async with session.get(url) as resp:
            responseData = await resp.text()
            return {
                "status" : 200,
                "data": responseData,
                "type": resp.content_type,
                'url' : url,
            }
    except Exception as e:
        return {
            'status' : 500,
            'error' : str(e),
            'url' : url,
        }

async def make_response(request):
    url = request.json.get("url")
    if url:
        async with aiohttp.ClientSession() as session:
            resp = await get(session, url=url)
            return response.json(resp)
    else:
        return response.json(dict())


@app.route('/', methods=['POST'])
async def post_handler(request):
    return await make_response(request)


if __name__ == "__main__":
  app.run(host="0.0.0.0", port="8081")


