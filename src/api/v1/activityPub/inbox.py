import json
import falcon
import requests
import logging

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256 
from base64 import b64encode, b64decode

from models.user import User
from models.status import Status

from activityPub import activities
from activityPub.activities import as_activitystream

from api.v1.activityPub.methods import (store, handle_follow, handle_note)
from activityPub.activities.verbs import (Accept)

from activityPub.identity_manager import ActivityPubId

from tasks.tasks import deliver

from activityPub.data_signature import SignatureVerification

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
        #Lowercase them to ensure all have the same name

        lowered_headers = {key.lower(): req.headers[key] for key in req.headers}

        siganture_check = SignatureVerification(lowered_headers, req.method, req.relative_uri).verify()

        if siganture_check == False:
            raise falcon.HTTPBadRequest(description="Error reading signature header")

        #Make a request to get the actor

        if req.content_length:
            activity = json.loads(req.stream.read().decode("utf-8"), object_hook=as_activitystream)
        else:
            activity = {}

        result = False

        if activity.type == 'Create':
            result = handle_note(activity)
        elif activity.type == 'Follow':
            result = handle_follow(activity)
        elif activity.type == 'Accept':
            accept = Accept(activity)
            accept.accept_follow()
            
        if result: 
            pass

            #1. Get the response object if we have to
            #2. Create the activity object
            #3. Decide if we can generate a reponse now 
            #4. Sign the response
            #5. Send the resposnse

        #store(activity, user, remote = True)
        resp.status= falcon.HTTP_202
