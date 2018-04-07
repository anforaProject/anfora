import json
import os
import logging

import falcon

from storage import db, Photo, User, Album
from auth import loadUser, auth_backend

#Get max size for uploads
MAX_SIZE = os.getenv('MAX_SIZE', 1024*1024)


def max_body(limit):

    def hook(req, resp, resource, params):
        length = req.content_length
        if length is not None and length > limit:
            msg = ('The size of the request is too large. The body must not '
                   'exceed ' + str(limit) + ' bytes in length.')

            raise falcon.HTTPRequestEntityTooLarge(
                'Request body is too large', msg)

    return hook


class getPhoto(object):
    
    auth = {
        'auth_disabled': True
    }
    
    def on_get(self, req, resp, pid):
        #photo = self.model.get_or_none(identifier=pid)
        photo = Photo.get_or_none(identifier=pid)
        
        if photo != None:
            result = json.dumps(photo.json(), default=str)
        else:
            result = json.dumps({"Error": 'Not found'})

        resp.body = result
        resp.set_header('Response by:', 'zinat')
        resp.status = falcon.HTTP_200


        
class manageUserPhotos(object):

    def __init__(self, uploads):
        self.uploads = uploads

    def on_get(self, req, resp, user):

        auth_user = req.context['user']
        if auth_user.username == user:
            photos = Photo.select().join(User).where(User.username == auth_user.username)
        #Must to considerer the case of friends relation
        else:
            photos = Photo.select().where(public = True).join(User).where(User.username == user)

        query = [photo.json() for photo in photos]
        resp.body = json.dumps({"photos": query}, default=str)
        resp.status = falcon.HTTP_200
        

    @falcon.before(max_body(MAX_SIZE))
    def on_post(self, req, resp, user):
        image = req.get_param('image')
        public = req.get_param('public') or False

        if image.filename:
            user = req.context['user']
            
            filename = image.filename

            photo = Photo.create(title=filename, public=public, user=user)
            print(photo, self.uploads)

            try:
                file_path = os.path.join(self.uploads, photo.identify())
                temp_file = file_path + '~'
                open(temp_file, 'wb').write(image.file.read())
                os.rename(temp_file, file_path)
                resp.status = falcon.HTTP_201
                resp.body = json.dumps(photo.json(), default=str)
        
            except Exception as e:
                print(e)
                photo.delete_instance()
                resp.status = falcon.HTTP_500
                
