from sanic import Sanic
from sanic import response

import aiohttp

from itertools import count

app = Sanic()
id_generator = count()

async def post(session, downloader, request):
	
	try:
		async with session.post(downloader, json=request) as resp:
			responseData = await resp.json()
			return responseData
	except Exception as e:
		return {
			'error' : str(e),
			'url' : request.get("url"),
			'headers' : resp.headers
		}

def make_response(downloader_response, archiveID):
	resp = dict()
	resp['ok'] = downloader_response.get('ok')
	if resp.get('ok'):
		resp['archive_path'] = f"/archivePath/{archiveID}"
	return resp

@app.route('/', methods=['POST'])
async def post_handler(request):
	url = request.json.get("url")
	if url:
		async with aiohttp.ClientSession() as session:
			downloader_response = await post(
				session, 
				downloader="http://0.0.0.0:8081", 
				request=request.json
				)

			resp = make_response(downloader_response, archiveID=next(id_generator))

			return response.json(resp)
	else:
		return response.json(dict())

if __name__ == "__main__":
  app.run(host="0.0.0.0", port="8080")
