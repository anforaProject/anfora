import json

import falcon
from storage import db, Photo, User
import logging
from falcon_auth import FalconAuthMiddleware, BasicAuthBackend

class PhotoResource(object):

    def __init__(self):
        self.model = Photo

    def on_get(self, req, resp, pid):
        #photo = self.model.get_or_none(identifier=pid)
        photo = Photo.select().join(User).where(User.username == pid)[0]
        
        if photo != None:
            result = json.dumps(photo.json(), default=str)
        else:
            result = "{Error: 'Not found'}"

        resp.body = result
        resp.set_header('Response by:', 'zinat')
        resp.status = falcon.HTTP_200
