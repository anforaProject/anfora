import json
import falcon

from models.user import User
from models.photo import Photo

from activityPub import activities
from activityPub.activities import as_activitystream

from api.v1.activityPub.methods import (deliver, store, handle_follow)

class Inbox():

    auth = {
        'exempt_methods': ['POST']
    }

    def on_get(self, req, resp, username):

        user = req.context['user']
        objects = user.activities.select().where(remote==True).order_by(created_at.desc())
        collection = activities.OrderedCollection(objects)

        resp.body = collection.to_json(context=True)
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp, username):

        payload = req.get_param('payload')
        activity = json.loads(payload, object_hook=as_activitystream)
        activity.validate()

        if activity.type == "Create":
            #handle_note(activity)
            pass
        elif activity.type == "Follow":
            handle_follow(activity)

        store(activity, user, remote = True)
        resp.status= falcon.HTTP_200
