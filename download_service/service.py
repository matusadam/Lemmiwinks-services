from sanic import Sanic
from sanic import response



import aiohttp

app = Sanic()

async def get(session, url):
	try:
		async with session.get(url) as resp:
			responseData = await resp.text()
			return {
				'index': {
					"data": responseData,
					"type": resp.content_type,
				},
			}
	except Exception as e:
		return {
			'error' : str(e),
			'url' : url,
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


