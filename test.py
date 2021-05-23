# import aiohttp
# import asyncio
# import urllib.parse

# while True:
# 	x = input("> ")
# 	message = "Hi"
# 	url = "https://api.pgamerx.com/v3/ai/response/"
# 	key = "xMORfA3UQqdL"
# 	header = {"x-api-key": key}
# 	type = "unstable"
# 	params = {'type':type , 'message':message}
# 	async def start():
# 		async with aiohttp.ClientSession(headers=header) as session:
# 			async with session.get(url='https://api.pgamerx.com/v3/ai/response', params=params) as resp:
# 				text = await resp.json()
# 				print(text[0]['message'])

# 	loop = asyncio.get_event_loop()
# 	loop.run_until_complete(start())