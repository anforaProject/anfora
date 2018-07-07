import json
import re
import hashlib # Used to create sha256 hash of the request body
from urllib.parse import urlparse
import logging

import requests

#Manage RSA stuff
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA512, SHA384, SHA256
from base64 import b64encode, b64decode

#Models
from models.activity import Activity
from models.user import User
from models.followers import FollowerRelation

#ActivityPub things
from activityPub import activities
from activityPub.activities import as_activitystream
from activityPub.identity_manager import ActivityPubId


def get_final_audience(audience):
    final_audience = []
    for ap_id in audience:
        print(ap_id)
        obj = dereference(ap_id)
        if isinstance(obj, activities.Collection):
            final_audience += [item.id for item in obj.items]
        elif isinstance(obj, activities.Actor):
            final_audience.append(obj.id)
        else:
            print("ninguno")
    return set(final_audience)

def deliver_to(ap_id, activity):
    obj = dereference(ap_id)
    if not getattr(obj, "inbox", None):
        # XXX: log this
        return
    print(activity.to_json(context=True))
    res = requests.post(obj.inbox, json=activity.to_json(context=True))
    if res.status_code != 200:
        msg = "Failed to deliver activity {0} to {1}"
        msg = msg.format(activity.type, obj.inbox)
        raise Exception(msg)


def store(activity, person, remote=False):
    payload  = bytes(json.dumps(activity.to_json()), "utf-8")
    obj = Activity(payload=payload, person=person, remote=remote)
    obj.save()
    return obj.id

def handle_follow(activity):
    followed = User.get_or_none(ap_id=activity.object)
    print("=> Handling follow")
    if followed:
        if isinstance(activity.actor, activities.Actor):
            ap_id = activity.actor.id
        elif isinstance(activity.actor, str):
            ap_id = activity.actor

        follower = ActivityPubId(ap_id).get_or_create_remote_user()
        FollowerRelation.create(
            user = follower,
            follows = followed
        )

        response = {'Type': 'Accept','Object':activity}


    else:
        print("error handling follow")

def handle_note(activity):
    if isinstance(activity.actor, activities.Actor):
        ap_id = activity.actor.id
    elif isinstance(activity.actor, str):
        ap_id = activity.actor

    person = ActivityPubId(ap_id).get_or_create_remote_user()

    note = Photo.get_or_none(ap_id=activity.object.id)

    if not note:
        Photo.create(
            content=activity.object.content,
            person=person,
            ap_id=activity.object.id,
            remote=True
        )

class SignatureVerification:

    """
    This class objetive is to verify sign of the request following 
    https://tools.ietf.org/html/draft-cavage-http-signatures-08

    Attributes:
        headers: A dict containing the request headers
        path: A str with the path of the request
        method: A str with the request method
    """

    def __init__(self,headers, method, path):
        self.signature_fail_reason = None
        self.signed_request_account = None
        self.REQUEST_TARGET = '(request-target)'

        self.method = method.lower()
        self.path = path
        self.headers = headers 

        self.signature_params=self._check_headers()

    def _split_signature(self):
        raw_signature = self.headers['signature']

        #FIX: add default headers -> date
        signature_params = {}   
        
        #Work with the header string to extract the information
        regex = r'([A-Za-z]+)=\"([^\"]+)\"'

        for element in raw_signature.split(','):
            match = re.match(regex, element)
            if match and len(match.groups()) == 2:
                key, value = match.groups()
                signature_params[key] = value

        return signature_params

    def _check_headers(self):
        #Check if the "Signature header is present"
        if 'signature' not in list(map(str.lower, self.headers.keys())):
            signature_fail_reason = "Request is not signed"
            return False

        signature_params = self._split_signature()
    
        ## Check if the params are valid
        if None in [signature_params.get('keyId'), signature_params.get('signature')]:
            self.signature_fail_reason = "Incompatible request signature"
            return False

        return signature_params

    
    def _build_signed_string(self, headers_list):

        
        headers = []


        hlist = headers_list.split(" ")
        
        for header in hlist:
            string = ""
            if header == self.REQUEST_TARGET:
                string = f'{self.REQUEST_TARGET}: {self.method} {self.path}'
            else:
                string = f'{header}: {self.headers.get(header)}'
            headers.append(string)

            
        return '\n'.join(headers)

    def verify(self):

        account = ActivityPubId(self.signature_params['keyId']).uri_to_resource(User)

        if not account:
            self.signature_fail_reason = "Could not retrive account using keyId"
            return 
            
        if self.verify_public_key(account.public_key):
            self.signed_request_account = account
            return True
        else:
            return False

    def verify_public_key(self, key):
        signature_params = self.signature_params

        #Verify using the public key
        signer = PKCS1_v1_5.new(RSA.importKey(key))
        digest = SHA256.new()

        signature = b64decode(signature_params['signature'])
        compare_signed_string = self._build_signed_string(signature_params['headers'])
        digest.update(compare_signed_string.encode('utf-8'))
        if signer.verify(digest, signature):
            #self.signed_request_account = account
            return True
        else:
            self.signature_fail_reason = "Verification failed"
            return False

