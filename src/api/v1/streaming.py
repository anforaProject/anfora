import signal
import redis
from tornado import web, gen
from tornado.options import options
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.iostream import StreamClosedError

from base_handler import BaseHandler
from auth.token_auth import bearerAuth

from aioredis.pubsub import Receiver

class Notification(BaseHandler):

    self.prefix = 'timeline'

    def initialize(self, source):
        """The ``source`` parameter is a string that is updated with
        new data. The :class:`EventSouce` instance will continuously
        check if it is updated and publish to clients when it is.
        """
        self.source = source
        self._last = None
        self.set_header('content-type', 'text/event-stream')
        self.set_header('cache-control', 'no-cache')

    async def reader(mpsc):
        async for channel, msg in mpsc.iter():
            assert isinstance(channel, AbcChannel)
                print("Got {!r} in channel {!r}".format(msg, channel))

    @bearerAuth
    async def get(self, user):
        
        mpsc = Receiver(loop=loop)
        asyncio.ensure_future(self.reader(mpsc))

        channel = f'{self.prefix}:{user.id}'

        await redis.subscribe(mpsc.channel('channel:1'),