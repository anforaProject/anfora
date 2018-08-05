import json

import falcon

from models.user import UserProfile 
from models.followers import FollowerRelation
from activityPub import activities


class Followers():

    auth = {
        'exempt_methods':['GET']
    }

    def on_get(self, req, resp, username):
        user = UserProfile.get_or_none(username=username)
        if user:
            followers = [follower.uris.id for follower in user.followers()]
            resp.body=json.dumps(activities.OrderedCollection(followers).to_json(), default=str)
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_404
