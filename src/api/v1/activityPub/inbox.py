import json
import tornado
import requests
import logging
import re
import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256 
from base64 import b64encode, b64decode

from models.user import UserProfile, User
from models.status import Status

from activityPub import activities
from activityPub.activities import as_activitystream

from api.v1.activityPub.methods import (store, handle_note)
from tasks.ap_methods import handle_follow, handle_create
from activityPub.activities.verbs import (Accept)

from activityPub.identity_manager import ActivityPubId

from tasks.tasks import deliver

from api.v1.base_handler import BaseHandler

class Inbox(BaseHandler):

    def post(self, username=None):

        #First we check the headers 
        #Lowercase them to ensure all have the same name
        """
        lowered_headers = {key.lower(): req.headers[key] for key in req.headers}
        
        siganture_check = SignatureVerification(lowered_headers, req.method, req.relative_uri).verify()

        if siganture_check == False:
            raise falcon.HTTPBadRequest(description="Error reading signature header")

        #Make a request to get the actor
        """
        data = tornado.escape.json_decode(self.request.body)

        logging.info(f'Received activity {data}')
        logging.info(self.request.headers)

        if data:
            activity = as_activitystream(data)
        else:
            activity = {}

        
        result = False
        if activity.type == 'Follow':
            logging.info(f"Starting follow process for {activity.object}" )
            result = handle_follow(activity)
            print(result)
            self.set_status(201)
        elif activity.type == 'Accept':
            #print(activity.to_json())
            self.write("WHAT?!")
        elif activity.type == 'Create':
            handle_create(activity)
            self.set_status(201)
        elif activity.type == 'Delete':
            self.set_status(201)

        #store(activity, user, remote = True)
        #self.set_status(500)
