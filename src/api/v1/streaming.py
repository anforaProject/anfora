import signal
import os
import logging
import redis
import asyncio
from asyncio import Queue
from tornado import web, gen
from tornado.options import options
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.iostream import StreamClosedError

from auth.token_auth import bearerAuth

from api.v1.base_handler import BaseHandler

import aioredis

# THis code is based on https://github.com/mivade/streamis/blob/master/streamis.py

redis_host = 'localhost'
redis_port = 6379

class Connection:
    _redis = None

    @classmethod
    async def redis(cls, force_reconnect=False):
        if cls._redis is None or force_reconnect:
            settings = (redis_host, redis_port)
            cls._redis = await aioredis.create_redis(settings)
        return cls._redis


class Subscription:
    """Handles subscriptions to Redis PUB/SUB channels."""
    def __init__(self, redis, channel: str):
        self._redis = redis
        self.name = channel
        self.listeners = set()

    async def subscribe(self):
        res = await self._redis.subscribe(self.name)
        self.channel = res[0]

    def __str__(self):
        return self.name

    def add_listener(self, listener):
        self.listeners.add(listener)

    async def broadcast(self):
        """Listen for new messages on Redis and broadcast to all
        HTTP listeners.
        """
        while len(self.listeners) > 0:
            msg = await self.channel.get()
            logging.debug("Got message: %s" % msg)
            closed = []
            for listener in self.listeners:
                try:
                    listener.queue.put_nowait(msg)
                except:
                    logging.warning('Message delivery failed. Client disconnection?')
                    closed.append(listener)
            if len(closed) > 0:
                [self.listeners.remove(listener) for listener in closed]


class SubscriptionManager:
    """Manages all subscriptions."""
    def __init__(self, loop=None):
        self.redis = None
        self.subscriptions = dict()
        self.loop = loop or asyncio.get_event_loop()

    async def connect(self):
        self.redis = await Connection.redis()

    async def subscribe(self, listener, channel: str):
        """Subscribe to a new channel."""
        if channel in self.subscriptions:
            subscription = self.subscriptions[channel]
        else:
            subscription = Subscription(self.redis, channel)
            await subscription.subscribe()
            self.subscriptions[channel] = subscription
            self.loop.call_soon(lambda: asyncio.Task(subscription.broadcast()))
        subscription.add_listener(listener)

    def unsubscribe(self, channel: str):
        """Unsubscribe from a channel."""
        if channel not in self.subscriptions:
            logging.warning("Not subscribed to channel '%s'" % channel)
            return
        sub = self.subscriptions.pop(channel)
        del sub


class SSEHandler(BaseHandler):
    def initialize(self, manager: SubscriptionManager):
        self.queue = Queue()
        self.manager = manager
        self.set_header('content-type', 'text/event-stream')
        self.set_header('cache-control', 'no-cache')
    
    @bearerAuth
    async def get(self, user):
        channel = f'timeline:{user.id}'
        logging.debug(f'SSE Connecting to channel: {channel}')
        await self.manager.connect()
        await self.manager.subscribe(self, channel)
        while True:
            message = await self.queue.get()
            print(message)
            try:
                event, data = message.decode('utf-8').split(' ', 1)
                logging.debug(f'SSE message sent: event: {event}\ndata: {data}\n\n')
                self.write(f"event: {event}\ndata: {data}\n\n")
                self.flush()
            except StreamClosedError:
                logging.debug(f'Event closed')
                break