import signal
import redis
from tornado import web, gen
from tornado.options import options
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.iostream import StreamClosedError

from auth_decorators.token_auth import bearerAuth

from api.v1.base_handler import BaseHandler

import aioredis

class Notification(BaseHandler):

    async def handle_msg(msg):
        event, data = msg.split(" ", 1)
        self.write('event: {}\n data: {}\n\n'.format(event, data))
        self.flush()

    async def reader(ch):
        while (await ch.wait_message()):
            msg = await ch.get_json()
            asyncio.ensure_future(handle_msg(msg))

    @bearerAuth
    async def get(self, user):
        self.set_header('content-type', 'text/event-stream')
        self.set_header('cache-control', 'no-cache')
        mpsc = Receiver(loop=loop)
        asyncio.ensure_future(self.reader(mpsc))
        prefix = "timeline"
        channel = f'{prefix}:{user.id}'

        sub = await aioredis.create_redis(('localhost', 6379))
        res = await sub.subscribe(channel)
        ch1 = res[0]
        tsk = await reader(ch1)

        #831d3b4b6dfac6ff0443b18a805415af845f47ed