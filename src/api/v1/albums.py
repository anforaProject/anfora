import json
import os
import logging

import falcon

from models.status import Status
from models.user import UserProfile
from models.album import Album
from models.albumRelation import RelationAlbumStatus
from auth.token_auth import (bearerAuth, is_authenticated)

class getAlbum:
    
    auth = {
        'auth_disabled': True
    }
    
    def on_get(self, req, resp, pid):
        #photo = self.model.get_or_none(identifier=pid)
        album = Album.get_or_none(Album_id==pid)
        
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


        
class createAlbum:

    def on_post(self, req, resp, user):
        user = req.context['user'] 
        name = req.get_param('name')
        public = bool(req.get_param('public'))
        print(name, public, user)
        if name:
            user = req.context['user']
            album = Album.create(name=name, public=public, user=user)
            
            resp.status = falcon.HTTP_201
            resp.body = json.dumps(album.json(), default=str)
        else:
            resp.status = falcon.HTTP_500
            resp.boyd = json.dumps({"Error": "Error creating the album"})
        
class addToAlbum:
    def on_post(self, req, resp, album, user):
        photo = Status.get_or_none(Status.id == req.get_param('photo'))
        album = Album.get_or_none(Album.id == album)

        print(album, photo)

        if album and photo:
            RelationAlbumStatus.create(album=album, photo=photo)

            resp.body = json.dumps({"Result": "Status successfully modified"})
            resp.status = falcon.HTTP_200
        else:
            resp.body = json.dumps({"Error": "Error creating relation"})
            resp.status = falcon.HTTP_500
