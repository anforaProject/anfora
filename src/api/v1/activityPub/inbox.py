import json
import falcon

from models.user import User
from models.photo import Photo

from activityPub import activities
from activityPub.activities import as_activitystream

from api.v1.activityPub.methods import (deliver, store, handle_follow, handle_note)
from api.v1.activityPub.methods import (get_or_create_remote_user, dereference)

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

        if req.content_length:
            activity = json.loads(req.stream.read().decode("utf-8"), object_hook=as_activitystream)
        else:
            activity = {}

        activity.validate()
        print(activity)
        if activity.type == "Create":
            handle_note(activity)
        elif activity.type == "Follow":
            handle_follow(activity)

        user = get_or_create_remote_user(ap_id=activity.actor)
        store(activity, user, remote = True)
        resp.status= falcon.HTTP_200
