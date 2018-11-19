import aiohttp

class ArchiveClient():

	def __init__(self):
		self.session = aiohttp.ClientSession()

	async def post(self, data):
		try:
			async with self.session.post(downloader, json=data) as resp:
				responseData = await resp.json()
				return responseData
		except Exception as e:
			return {
				'error' : str(e),
				'url' : data.get("url"),
			}

		