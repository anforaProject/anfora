import json
import os

import falcon
from storage import db, Photo, User
import logging
from falcon_auth import FalconAuthMiddleware, BasicAuthBackend

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
    def on_get(self, req, resp, pid):
        #photo = self.model.get_or_none(identifier=pid)
        photo = Photopac.get_or_none(identifier=pid)
        
        if photo != None:
            result = json.dumps(photo.json(), default=str)
        else:
            result = json.dumps({"Error": 'Not found'})

        resp.body = result
        resp.set_header('Response by:', 'zinat')
        resp.status = falcon.HTTP_200

class addPhoto(object):

    def __init__(self, uploads):
        self.uploads = uploads

    @falcon.before(max_body(MAX_SIZE))
    def on_post(self, req, resp):
        image = req.get_param('image')

        if image.filename:
            yab = User.get_or_none(username='yab')
            
            filename = image.filename

            photo = Photo.create(title=filename, public=False, user=yab)
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
                
