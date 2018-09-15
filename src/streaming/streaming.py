import asyncio
import peewee
import peewee_async
from aiohttp import web

from settings import (DB_USER, DB_NAME, DB_PORT, DB_HOST)


database = peewee_async.PostgresqlDatabase(
    DB_NAME,
    user=DB_USER,  
    host=DB_HOST,
    port=DB_PORT,
)

loop = asyncio.get_event_loop()

app = web.Application(loop=loop)