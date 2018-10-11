import tornado
import asyncio

import peewee_async

from models.base import db

from api.v1.streaming import Notification

def make_app():
    return tornado.web.Application([
        (r"/api/v1/streaming/user", Notification),
    ], debug=True)

if __name__ == "__main__":
    #AsyncIOMainLoop().install()
    app = make_app()

    app.listen(4000)
    app.objects = peewee_async.Manager(db)
    #loop = asyncio.get_event_loop().run_forever()
    tornado.ioloop.IOLoop.current().start()