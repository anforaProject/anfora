import json
import os
import logging

import falcon

from storage import (db, Photo, User, Album)
from auth import (loadUser, auth_backend)

class getAlbum(object):
    
    auth = {
        'auth_disabled': True
    }
    
    def on_get(self, req, resp, pid):
        #photo = self.model.get_or_none(identifier=pid)
        album = Album.get_or_none(identifier=pid)
        
        if album != None:
            if album.public or ( album.private and album.user == req.context['user']):
                result = json.dumps(album.json(), default=str)
            else:
                raise falcon.HTTPUnauthorized(
                title='401 Unauthorized',
                description='Invalid user or token missing',
                    challenges=None)
                
        else:
            result = json.dumps({"Error": 'Not found'})

        resp.body = result
        resp.set_header('Response by:', 'zinat')
        resp.status = falcon.HTTP_200


        
class createAlbum(object):

    def on_post(self, req, resp):
        name = req.get_param('name')
        public = req.get_param('public')

        if name:
            user = req.context['user']
            album = Album.create(name=filename, public=public, user=user)
            
            resp.status = falcon.HTTP_201
            resp.body = json.dumps(album.json(), default=str)
        
class addToAlbum(object):
    def on_post(self, req, resp, album):
        photo = req.get_param('photo')
        album = Album.get_or_none(album)

        if album and photo:
            
