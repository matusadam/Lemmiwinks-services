from sanic import Sanic
from sanic import response
import asyncio

import aiohttp

from itertools import count

app = Sanic()

async def post(session, downloader, data):
	
	try:
		async with session.post(downloader, json=data) as resp:
			responseData = await resp.json()
			return responseData
	except Exception as e:
		return {
			'error' : str(e),
			'url' : data.get("url"),
		}

async def make_response(request):
	urls = request.json.get("urls")
	# TODO: sanitise request
	if not urls:
		return response.json(dict())
	tasks = list()
	async with aiohttp.ClientSession() as session:
		for url in urls:
			tasks.append(asyncio.ensure_future(post(
				session, 
				downloader="http://0.0.0.0:8081", 
				data=url
				)))
		downloader_responses = await asyncio.gather(*tasks) 

		# TODO: process responses

	resp = {"download_url": "/archive/abcdefgh"}
	return resp

@app.route('/', methods=['POST'])
async def post_handler(request):
	return response.json(await make_response(request))

if __name__ == "__main__":
  app.run(host="0.0.0.0", port="8080")


