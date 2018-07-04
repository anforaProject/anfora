import json
import os, sys, io
import uuid

from PIL import Image
import falcon

from models.user import User
from models.photo import Photo
from models.followers import FollowerRelation
from models.activity import Activity

from activityPub import activities
from activityPub.activities import as_activitystream

from api.v1.activityPub.methods import  store
from tasks.tasks import deliver
from tasks.tasks import create_image

from activityPub.identity_manager import ActivityPubId


class Outbox():

    def __init__(self):
        self.uploads = os.getenv('UPLOADS', '/home/yabir/killMe/uploads')

    auth = {
        'exempt_methods': ['GET']
    }

    def on_get(self, req, resp, username):
        user = User.get_or_none(username==username)
        objects = user.photos.select().order_by(Photo.created_at.desc())

        collectionPage = activities.OrderedCollectionPage(map(activities.Note, objects))
        collection = activities.OrderedCollection([collectionPage])
        resp.body = json.dumps(collection.to_json(context=True))
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp, username):
        user = User.get_or_none(username==username)

        if req.context['user'].username != username:
            resp.status = falcon.HTTP_401
            resp.body = json.dumps({"Error": "Access denied"})

        payload = req.get_param('data')
        activity = json.loads(payload, object_hook=as_activitystream)

        if activity.object.type == "Note":
            obj = activity.object
            activity = activities.Create(
                to=user.uris.followers,
                actor=user.uris.id,
                object=obj
            )

        activity.validate()

        if activity.type == "Create":
            if activity.object.type != "Note":
                resp.status = falcon.HTTP_500
                resp.body = json.dumps({"Error": "You only can create notes"})


                activity.object.id = photo.uris.id
                activity.id = store(activity, user)
                #deliver(activity)
                resp.body = json.dumps({"Success": "Delivered successfully"})
                resp.status = falcon.HTTP_200

                #Convert to jpeg

            else:
                resp.status = falcon.HTTP_500
                resp.body = json.dumps({"Error": "No photo attached"})




        if activity.type == "Follow":

            followed = ActivityPubId(activity.object).get_or_create_remote_user()
            user = req.context["user"]
            #print(followed.ap_id, user.username, followed.username)
            f = FollowerRelation.create(user = user, follows=followed)

            activity.actor = user.uris.id
            activity.to = followed.uris.id
            #activity.id = store(activity, user)
            deliver(activity)

            resp.body = json.dumps({"Success": "Delivered successfully"})
            resp.status = falcon.HTTP_200
