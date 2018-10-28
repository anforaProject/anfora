import logging
import os
from logging.config import fileConfig


import tornado.ioloop
import tornado.web 
from tornado.platform.asyncio import AsyncIOMainLoop
import asyncio

import peewee_async
from tornadouvloop import TornadoUvloop

from models.base import db

from api.v1.user import (UserHandler, ProfileManager, RegisterUser, AuthUser,
                        VerifyCredentials, PasswordRecovery, RequestPasswordRecovery, 
                        FollowUser, UnFollowUser, FetchFollowers, FetchFollowing,
                        Relationship)
from api.v1.status import (StatusHandler, UserStatuses, FavouriteStatus,
                            UnFavouriteStatus, FetchUserStatuses  
                        )

from api.v1.server import (WellKnownNodeInfo, WellKnownWebFinger, NodeInfo)
from api.v1.media import UploadMedia
from api.v1.timelines import (HomeTimeline)
from api.v1.streaming import SSEHandler, SubscriptionManager

from api.v1.notifications import NotificationHandler

from api.v1.explore import (ExploreUsers, ExploreServer)

from settings import ROOT_PATH

fileConfig('logging_config.ini')

class MainHandler(tornado.web.RequestHandler):
    def get(self, path):
        try:
            with open(f"{ROOT_PATH}/src/client/dist/index.html") as f:
                self.write(f.read())
        except IOError as e:
            self.write("404: Not Found")

manager = SubscriptionManager()

            
def make_app():
    return tornado.web.Application([
        (r'/api/v1/accounts/(?P<id>[\d+])', UserHandler),
        (r'/api/v1/accounts/(?P<id>[\d+])/followers', FetchFollowers),
        (r'/api/v1/accounts/(?P<id>[\d+])/following', FetchFollowing),
        (r'/api/v1/accounts/(?P<target_id>[\d+])/follow', FollowUser),
        (r'/api/v1/accounts/(?P<target_id>[\d+])/unfollow', UnFollowUser),
        (r'/api/v1/accounts/(?P<id>[\d+])/statuses', FetchUserStatuses),
        (r'/api/v1/accounts/update_credentials', ProfileManager),
        (r'/api/v1/accounts/relationships', Relationship),

        (r'/api/v1/statuses', UserStatuses),
        (r'/api/v1/statuses/(?P<pid>[\d+]+)', StatusHandler),
        (r'/api/v1/statuses/(?P<pid>[\d+]+)/favourite', FavouriteStatus),
        (r'/api/v1/statuses/(?P<pid>[\d+]+)/unfavourite', UnFavouriteStatus),

        (r'/.well-known/nodeinfo', WellKnownNodeInfo),
        (r'/.well-known/webfinger', WellKnownWebFinger),
        (r'/nodeinfo', NodeInfo),

        (r'/api/v1/notifications', NotificationHandler),

        (r'/api/v1/timelines/home', HomeTimeline),

        (r'/api/v1/media', UploadMedia),
        (r'/api/v1/auth', AuthUser),
        (r'/api/v1/accounts/verify_credentials', VerifyCredentials),

        (r'/api/v1/explore', ExploreServer),

        (r'/api/v1/register', RegisterUser),
        (r'/api/v1/reset-password',PasswordRecovery),
        (r'/api/v1/reset-password/request/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,6})', RequestPasswordRecovery),
        (r'/api/v1/streaming/user', SSEHandler, dict(manager=manager)),
        (r'/(.*)', MainHandler),
    ], debug=True)

if __name__ == "__main__":
    #AsyncIOMainLoop().install()
    app = make_app()

    app.listen(3000)
    app.objects = peewee_async.Manager(db)
    
    loop = asyncio.get_event_loop()
    #manager.connect()
    tornado.ioloop.IOLoop.configure(TornadoUvloop)
    tornado.ioloop.IOLoop.current().start()
