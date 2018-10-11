import tornado
import asyncio

import peewee_async

from models.base import db

from api.v1.streaming import SSEHandler, SubscriptionManager



def make_app():
    loop = asyncio.get_event_loop()
    manager = SubscriptionManager()
    loop.run_until_complete(manager.connect())
    app = tornado.web.Application([
        (r"/api/v1/streaming/user", SSEHandler, dict(manager=manager)),
    ], debug=True)

    # Set database
    app.objects = peewee_async.Manager(db)
    app.listen(4000)
    loop.run_forever()

if __name__ == "__main__":
    make_app()