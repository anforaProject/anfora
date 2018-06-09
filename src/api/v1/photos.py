import json
import os
import logging
import uuid
import io
import sys

import falcon

from models.user import User
from models.photo import Photo
from models.album import Album

from auth import (loadUser, auth_backend, try_logged_jwt)

from tasks.tasks import create_image


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
            result = photo.json()
        else:
            result = json.dumps({"Error": 'Not found'})

        resp.body = result
        resp.set_header('Response by:', 'zinat')
        resp.status = falcon.HTTP_200



class manageUserPhotos(object):

    def __init__(self, uploads):
        self.uploads = uploads

    auth = {
        'exempt_methods': ['GET','OPTIONS']
    }

    def _strip_message(self, text):
        return text

    def on_get(self, req, resp, user):

        auth_user = try_logged_jwt(auth_backend, req, resp)

        if auth_user and auth_user.username == user:
            photos = Photo.select().join(User).where(User.username == auth_user.username)
        #Must to considerer the case of friends relation
        else:
            photos = Photo.select().where(Photo.public == True).join(User).where(User.username == user)

        query = [photo.to_model() for photo in photos]
        resp.body = json.dumps(query, default=str)
        resp.status = falcon.HTTP_200

    @falcon.before(max_body(MAX_SIZE))
    def on_post(self, req, resp):
        image = req.get_param('image')
        public = bool(req.get_param('public')) #False if None

        user = req.context['user']
        print(image,public)
        if image != None:
            try:

                #Search a valid name

                valid = False
                ident = ""
                while not valid:
                    ident = str(uuid.uuid4())
                    valid = not Photo.select().where(Photo.media_name == ident).exists()


                #temp_file = file_path + '~'
                #open(temp_file, 'wb').write(image.file.read())

                #Create the image and the thumbnail
                create_image(io.BytesIO(image.file.read()),self.uploads, ident)

                user = req.context['user']
                filename = image.filename
                width, height = (1080,1080)

                photo = Photo.create(title=filename,
                                     user=user,
                                     message = req.get_param('message') or '',
                                     description = req.get_param('description') or '',
                                     sensitive = req.get_param('sensitive') or '',
                                     media_type="Image",
                                     width = width,
                                     height=height,
                                     media_name=ident,
                                     )

            except IOError:
                print(e)
                photo.delete_instance()
                resp.body = json.dumps({"Error": "Couldn't store file"})
                resp.status = falcon.HTTP_500

            resp.status = falcon.HTTP_200

        else:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({"Error": "No photo attached"})
