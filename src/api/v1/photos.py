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

from pipelines.upload_media import upload_image

from tasks.redis.spreadStatus import spreadStatus
from tasks.tasks import create_image
from auth import (loadUser, auth_backend, try_logged_jwt)

from api.v1.helpers import (max_body, its_me)

#Get max size for uploads
MAX_SIZE = os.getenv('MAX_SIZE', 1024*1024)


class getPhoto:

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



class manageUserPhotos:

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
                create_image(io.BytesIO(image.file.read()), ident)

                user = req.context['user']
                filename = image.filename
                dimensions = (1080,1080)

                photo = upload_image(user, req.get_param('message'), req.get_param('description')
                                    ,ident,req.get_param('sensitive'), dimensions, filename )

                photo.save()
                spreadStatus(photo)
                resp.status = falcon.HTTP_200
                resp.body = json.dumps(photo.to_json(),default=str)

            except IOError:
                print(e)
                photo.delete_instance()
                resp.body = json.dumps({"Error": "Couldn't store file"})
                resp.status = falcon.HTTP_500



        else:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({"Error": "No photo attached"})
