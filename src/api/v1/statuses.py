import json
import os
import logging
import uuid
import io
import sys

import falcon

from models.user import UserProfile
from models.status import Status
from models.album import Album
from models.media import Media

from pipelines.upload_media import upload_image

from tasks.redis.spreadStatus import spread_status
from tasks.tasks import create_image
from auth import (loadUser, auth_backend, try_logged_jwt)

from api.v1.helpers import (max_body, its_me)

from managers.user_manager import UserManager

#Get max size for uploads
MAX_SIZE = os.getenv('MAX_SIZE', 1024*1024)


class getStatus:

    auth = {
        'auth_disabled': True
    }

    def on_get(self, req, resp, pid):
        #photo = self.model.get_or_none(identifier=pid)
        photo = Status.get_or_none(identifier=pid)

        if photo != None:
            result = photo.json()
        else:
            result = json.dumps({"Error": 'Not found'})

        resp.body = result
        resp.set_header('Response by:', 'zinat')
        resp.status = falcon.HTTP_200


class favouriteStatus:

    def on_post(self, req, resp, id):
        status = Status.get_or_none(id=id)
        if status:
            user = req.context['user']
            UserManager(user).like(status)
            resp.body = json.dumps(status, default=str)
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_404

class unfavouriteStatus:

    def on_post(self, req, resp, id):
        status = Status.get_or_none(id=id)
        if status:
            user = req.context['user']
            UserManager(user).dislike(status.id)
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_404

class manageUserStatuses:

    auth = {
        'exempt_methods': ['GET','OPTIONS']
    }

    def _strip_message(self, text):
        return text

    def on_get(self, req, resp, user):

        auth_user = try_logged_jwt(auth_backend, req, resp)

        if auth_user and auth_user.id == user:
            photos = Status.select().join(User).where(UserProfile.username == auth_user.username).order_by(Status.created_at.desc())
        #Must to considerer the case of friends relation
        else:
            photos = Status.select().join(User).where(UserProfile.username == user).where(Status.public == True).order_by(Status.created_at.desc())

        query = [photo.to_model() for photo in photos]
        resp.body = json.dumps(query, default=str)
        resp.status = falcon.HTTP_200

    @falcon.before(max_body(MAX_SIZE))
    def on_post(self, req, resp):

        if req.get_param('media_ids'):
            user = req.context['user']

            status = Status(
                caption=req.get_param('status') or '',
                visibility=bool(req.get_param('visibility')), #False if None
                user=user,
                sensitive=bool(req.get_param('sensitive')),
                remote=False,
                story=bool(req.get_param('is_story'))
            )

            if status.sensitive:
                status.spoliet_text=req.get_param('spoiler_text')

            status.save()

            if  req.get_param('media_ids') != None:
                    for image in req.get_param('media_ids').split(','):
                        m = Media.get_or_none(media_name=image)
                        m.status = status
                        m.save()

            #Increment the number of posts uploaded
            UserProfile.update({UserProfile.statuses_count: UserProfile.statuses_count + 1}).where(UserProfile.id == user.id).execute()
            spread_status(status)
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(status.to_json(),default=str)

        elif req.get_param('in_reply_to_id'):

            replying_to = Status.get_or_none(id=req.get_param('in_reply_to_id'))
            if replying_to:
                status = Status(
                    caption = req.get_param('status'),
                    user = user,
                    remote = False,
                    story = False,
                    in_reply_to = replying_to,
                    sensitive = replying_to.sensitive,
                    spoiler_text = req.get_param('spoiler_text') or replying_to.spoiler_text
                )
            else:
                resp.status = falcon.HTTP_500
                resp.body = json.dumps({"Error": "Replying to bad ID"})
        else:
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({"Error": "No photo attached"})
