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
from api.v1.activityPub.methods import (get_or_create_remote_user, dereference)

from tasks.tasks import deliver

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

        #Extract the headers
        keyId = req.get_header('keyId')
        headers = req.get_header('headers')
        Signature = req.get_header('signature')
        
        #Make a request to get the actor
        r_to_keyId = requests.get(keyId, headers={'Accept': 'application/json'})
        actor = None
        if(r_to_keyId.status_code == 200):
            actor = r_to_keyId.json()
        else:
            return falcon.HTTP_500

        #Load the public key
        signer = PKCS1_v1_5.new(actor['publicKey']['publicKeyPem'])

        if req.content_length:
            activity = json.loads(req.stream.read().decode("utf-8"), object_hook=as_activitystream)
        else:
            activity = {}

        activity.validate()
        print(activity)
        if activity.type == 'Create':
            handle_note(activity)
        elif activity.type == 'Follow':
            handle_follow(activity)
        elif activity.type == 'Accept':
            handle_accept(activity)
            
        user = get_or_create_remote_user(ap_id=activity.actor)
        store(activity, user, remote = True)
        resp.status= falcon.HTTP_200
