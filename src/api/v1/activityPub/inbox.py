import json
import falcon
import requests

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256 
from base64 import b64encode, b64decode

from models.user import User
from models.photo import Photo

from activityPub import activities
from activityPub.activities import as_activitystream

from api.v1.activityPub.methods import (store, handle_follow, handle_note)
from activityPub.identity_manager import ActivityPubId

from tasks.tasks import deliver

from api.v1.activityPub.methods import SignatureVerification

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

        #First we check the headers 
        siganture_check = SignatureVerification(req.headers, req.mehtod, req.relative_uri, req.body).verify()

        if siganture_check == None:
            raise falcon.HTTPBadRequest(description="Error reading signature header")

        #Make a request to get the actor
        actor = as_activitystream(siganture_check)

        if req.content_length:
            activity = json.loads(req.stream.read().decode("utf-8"), object_hook=as_activitystream)
        else:
            activity = {}

        if activity.type == 'Create':
            pass
            handle_note(activity)
        elif activity.type == 'Follow':
            pass
            handle_follow(activity)
        elif activity.type == 'Accept':
            pass
            handle_accept(activity)
            
        store(activity, user, remote = True)
        resp.status= falcon.HTTP_202
