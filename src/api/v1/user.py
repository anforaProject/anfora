import json
import os
import logging
from datetime import datetime, timedelta, date

import falcon
import redis
from falcon_auth import BasicAuthBackend

from models.user import User
from models.photo import Photo
from models.token import Token

from auth import (auth_backend,loadUserToken,loadUserPass)

from activityPub import activities

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

class authUser(object):

    auth = {
        'backend': BasicAuthBackend(user_loader=loadUserPass)
    }

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

class getFollowers():

    auth = {
        'exempt_methods':['GET']
    }

    def on_get(self, req, resp, username):
        user = User.get_or_none(username=username)
        if user:
            followers = [follower.to_activitystream() for follower in user.followers()]
            f = activities.Collection(followers)
            print(f.to_json(context=True))
            resp.body=json.dumps(f.to_json(context=True))
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_404


class getUser():
    auth = {
        'exempt_methods': ['GET']
    }

    def on_get(self, req, resp, username):
        person = User.get_or_none(username=username)
        if person:
            resp.body = json.dumps(person.to_api(), default=json_serial)
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

    auth = {
        'exempt_methods': ['GET']
    }

    def on_get(self, req, resp, username):

        user = User.get_or_none(username=username)
        if user:
            statuses = [x.to_json() for x in user.statuses()]

            resp.body = json.dumps(statuses, default=str)
            resp.status = falcon.HTTP_200

        else:

            resp.body = json.dumps({"Error: No such user"})
            resp.status = falcon.HTTP_404

class homeTimeline(object):

    def on_get(self, req, resp):
        username = req.context['user'].username
        r = redis.StrictRedis(host='localhost', port=6379)

        local = req.get_param('local') or False
        max_id = req.get_param('max_id') or None
        since_id = req.get_param('since_id') or None
        limit = req.get_param('limit') or 40
        statuses = []
        for post in r.zrange('{}:hometimeline'.format(username), 0, min(limit-1, 40), withscores=False):
            statuses.append(Photo.get(id=post).to_json())

        print(statuses)
        resp.body=json.dumps(statuses, default=str)
        resp.status=falcon.HTTP_200
