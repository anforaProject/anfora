import json
import re
import hashlib # Used to create sha256 hash of the request body
from urllib.parse import urlparse

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

    def __init__(self,headers, method, path):
        self.signature_fail_reason = None
        self.signed_request_account = None
        self.REQUEST_TARGET = '(request-target)'
        self.method = method.lower()
        self.path = path
        self.headers = headers

        
    def verify(self):

        headers = self.headers

        #Check if the "Signature header is present"
        if 'signature' not in list(map(str.lower,a.keys())):
            signature_fail_reason = "Request is not signed"
            return

        raw_signature = headers['signature']

        signature_params = {}

        #Work with the header string to extract the information
        regex = r'([A-Za-z]+)=\"([^\"]+)\"'
        for element in raw_signature.split(','):
            match = re.match(regex, element)
            if match and len(match.groups()) == 2:
                key, value = mathc.groups()
                signature_params[key] = value
        
        ## Check if the params are valid

        if None in [signature_params.get('keyId'), signature_params.get('signature')]:
            self.signature_fail_reason = "Incompatible request signature"
            return 

        account = ActivityPubId(signature_params['keyId']).uri_to_resource(User)

        if not account:
            self.signature_fail_reason = "Could not retrive account using keyId"
            return
        
        signature = b64decode(signature_params['signature'])
        compare_signed_string = self.build_signed_string(signature_params['headers'], headers)
        #Verify using the public key
        signer = PKCS1_v1_5.new(accoutn.public_key)
        digest = SHA256.new()
        digest.update(compare_signed_string)

        if signer.verify(digest, signature):
            self.signed_request_account = account
            return self.signed_request_account
        else:
            self.signature_fail_reason = "Verification failed for {account.preferredUsername}:{account.uris.id}"
            return


    def build_signed_string(self,signed_headers):

        headers = self.headers
        
        if not signed_headers:
            signed_headers = 'date'    

        headers = []
        for header in signed_headers.split(" "):
            string = ""
            if header == self.REQUEST_TARGET:
                string = f'{self.REQUEST_TARGET}: {self.method} {self.path}'
            elif header == 'digest':
                string = f'digest: {self.digest_body(req.body)}'
            else:
                f'{header}: #{headers.get(header)}'
            headers.append(string)

        return '\n'.join(headers)

    def digest_body(self, body):
        m = hashlib.sha256()
        m.update(body.encode())
        
        sha_value = b64encode(m.digest())

        return f'SHA-256={sha_value}'
