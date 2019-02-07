import asyncio
import logging
import urllib.parse
import json

try:
    with open('data.json') as f:
        DATABASE = json.load(f)
except:
    logging.info('No database was found, making a new one.')
    DATABASE = {}

async def database_save():
    while True:
        with open('data.json', 'w') as f:
            json.dump(DATABASE, f)
        await asyncio.sleep(30)


asyncio.ensure_future(database_save())
