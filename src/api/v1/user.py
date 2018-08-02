import json
import os
import logging
from datetime import datetime, timedelta, date

import falcon
import redis
from falcon_auth import BasicAuthBackend

from models.user import User
from models.status import Status
from models.token import Token
from models.followers import FollowerRelation

from auth import (auth_backend,loadUserToken,loadUserPass)

from activityPub import activities
from activityPub.data_signature import LinkedDataSignature,SignatureVerification

from utils.atomFeed import generate_feed

from api.v1.helpers import get_ap_by_uri
from activityPub.identity_manager import ActivityPubId

from tasks.ap_methods import send_activity

from settings import (DOMAIN, MEDIA_FOLDER)

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

class authUser(object):

    """
    Loggin user
    """

    auth = {
        'backend': BasicAuthBackend(user_loader=loadUserPass)
    }

    cors_enabled = False

    def on_get(self, req, resp):
        user = req.context['user']

        if user.remote:
            resp.status = falcon.HTTP_401
            resp.body = json.dumps({"Error": "Remote user"})

        token = Token.create(user=user)

        payload = {
            "token": token.key
        }


        resp.status = falcon.HTTP_200
        resp.body = json.dumps({"token":auth_backend.get_auth_token(payload)})

class verifyCredentials:

    def on_get(self, req, resp):

        user = req.context['user']

        resp.body = json.dumps(user.to_json(), default=str)
        resp.status = falcon.HTTP_200

class manageCredentials:

    def on_patch(self, req, resp):
        user = req.context['user']

        errors = []

        if 'display_name' in req.params:
            if len(req.get_param('display_name')) <= 31: 
                user.name = req.get_param('display_name')
            else:
                errors.append('display_name length exceeded.')
        
        if 'note' in req.params:
            if len(req.get_param('note')) <= 160:
                user.description = req.get_param('note')
            else:
                errors.append('Note length exceeded.')

        if 'locked' in req.params:
            user.private = bool(req.get_param('locked'))

        if 'bot' in req.params:
            user.bot = bool(req.get_param('bot'))

        if 'avatar' in req.params:
            image = req.get_param('avatar')
            user.avatar_file = user.update_avatar(image.file.read())
        
        if not errors:
            user.save()
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(user.to_json(), default=str)
        else:
            resp.status = falcon.HTTP_UNPROCESSABLE_ENTITY
            resp.body = json.dumps(errors)
            
class getFollowers():

    auth = {
        'exempt_methods':['GET']
    }

    def on_get(self, req, resp, id):
        user = User.get_or_none(id=id)
        if user:
            followers = [follower.to_json() for follower in user.followers()]
            resp.body=json.dumps(followers, default=str)
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_404


class getUser():
    auth = {
        'exempt_methods': ['GET']
    }

    def on_get(self, req, resp, id):
        person = User.get_or_none(id=id)
        if person:
            resp.body = json.dumps(person.to_json(), default=json_serial)
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_404


class logoutUser(object):

    def on_post(self, req, resp):
        user = req.context['user']

        token = req.get_param('token').replace('Bearer','').split(' ')[-1]
        if user.remote:
            resp.status = falcon.HTTP_404
            resp.body = json.dumps({"Error": "Remote user"})

        token = Token.get(Token.key==token)

        if user == token.user:
            token.delete_instance()
            resp.status = falcon.HTTP_200
            resp.body = json.dumps({"Success":"Removed token"})
        else:
            resp.status = falcon.HTTP_401
            resp.body = json.dumps({"Error": "Unauthorized user"})


class getStatuses(object):

    """
    Retrive Statuses for an user
    """

    auth = {
        'exempt_methods': ['GET']
    }

    def on_get(self, req, resp, id):

        user = User.get_or_none(id=id)
        if user:
            statuses = [x.to_json() for x in user.statuses.order_by(Status.created_at.desc())]
            resp.body = json.dumps(statuses, default=str)
            resp.status = falcon.HTTP_200

        else:
            resp.body = json.dumps({"Error: No such user"})
            resp.status = falcon.HTTP_404

class homeTimeline(object):

    def on_get(self, req, resp):
        username = req.context['user'].username
        r = redis.StrictRedis(host=os.environ.get('REDIS_HOST', 'localhost'))

        local = req.get_param('local') or False
        max_id = req.get_param('max_id') or None
        since_id = req.get_param('since_id') or None
        limit = req.get_param('limit') or 40
        statuses = []
        for post in r.zrange('{}:hometimeline'.format(username), 0, min(limit-1, 40), withscores=False):
            statuses.append(Status.get(id=post).to_json())

        print(statuses)
        resp.body=json.dumps(statuses, default=str)
        resp.status=falcon.HTTP_200

class atomFeed(object):
    

    """
    Called when you request the atom feed 
    """

    auth = {
        'exempt_methods': ['GET']
    }

    def on_get(self, req, resp, id):
        user = User.get_or_none(id=id)
        if user:
            if 'max_id' in req.params.keys():
                feed = generate_feed(user, req.params['max_id'])
            else:
                feed = generate_feed(user)

            resp.status = falcon.HTTP_200
            resp.body = feed
            resp.content_type = falcon.MEDIA_XML
        else:

            resp.status = falcon.HTTP_404


class followAction(object):

    """
    Triggered when you want to follow an account in the fediverse
    """

    def on_post(self, req, resp):
        user = req.context['user']

        #FIX: Check if it's uri
        obj_id = get_ap_by_uri(req.params['uri'])
        #print(obj_id)
        follow_object = activities.Follow(actor=user.uris.inbox,
                                    object=obj_id)


        #Follow object that needs to be send
        signed_object = LinkedDataSignature(follow_object.to_json(context=True))

        #Prepare the object that will be send as response
        following = ActivityPubId(obj_id).get_or_create_remote_user()

        #Sign the activity object
        signed_object.sign(user)

        #Create the task to send the petition
        send_activity(signed_object.json, user, obj_id)
        
        resp.body = json.dumps(following.to_json(), default=str)
        #resp.body = json.dumps(signed_object.json, default=str)
        resp.status = falcon.HTTP_200


class followingAccounts:

    auth = {
        'exempt_methos': ['GET']
    }

    def __init__(self):
        self.MAX_ELEMENTS = 40

    def on_get(self, req, resp, id):

        max_id = req.get_param('max_ids')
        since_id = req.get_param('since_id')
        limit = req.get_param('limit') or self.MAX_ELEMENT

        if max_id and since_id:
            follows = User.select().join(FollowerRelation, on=FollowerRelation.follows).where(FollowerRelation.user.id == id, User.id > since_id, User.id < max_id).limit(limit)
        elif max_id:
            follows = User.select().join(FollowerRelation, on=FollowerRelation.follows).where(FollowerRelation.user.id == id, User.id < max_id).limit(limit)
        elif since_id:
            follows = User.select().join(FollowerRelation, on=FollowerRelation.follows).where(FollowerRelation.user.id == id, User.id > since_id).limit(limit)
        else:
            follows = User.select().join(FollowerRelation, on=FollowerRelation.follows).where(FollowerRelation.user.id == id).limit(limit)


