from sanic import Sanic
from sanic import response

import aiohttp

app = Sanic()

async def get(session, url):
	
	try:
		async with session.get(url) as resp:
			responseData = await resp.text()
			return {
				'data': responseData,
				'url' : url,
				'content_type' : resp.content_type,
				'headers' : resp.headers,
				'ok' : True
			}
	except Exception as e:
		return {
			'error' : str(e),
			'url' : url,
			'ok' : False
		}



@app.route('/', methods=['POST'])
async def post_handler(request):
	url = request.json.get("url")
	if url:
		async with aiohttp.ClientSession() as session:
			resp = await get(session, url=url)
			return response.json(resp)
	else:
		return response.json(dict())

if __name__ == "__main__":
  app.run(host="0.0.0.0", port="8081")


