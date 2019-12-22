import aiohttp

conn = aiohttp.TCPConnector(limit=0)
aio = aiohttp.ClientSession(connector=conn)
