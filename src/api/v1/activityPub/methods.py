import json
import re
from urllib.parse import urlparse

import requests

from models.activity import Activity
from activityPub import activities
from activityPub.activities import as_activitystream

from models.user import User
from models.followers import FollowerRelation

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

        response = {"Type": "Accept", "Object":activity}


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

    def __init__(self):
        self.signature_fail_reason = None
        self.signed_request_account = None
        
    def verify(self, headers):

        #Check if the "Signature header is present"
        if 'signature' not in list(map(str.lower,a.keys())):
            signature_fail_reason = "Request is not signed"
            return signature_fail_reason

        raw_signature = headers['signature']

        signature_params = {}
        regex = r'([A-Za-z]+)=\"([^\"]+)\"'
        for element in raw_signature.split(','):
            match = re.match(regex, element)
            if match and len(match.groups()) == 2:
                key, value = mathc.groups()
                signature_params[key] = value
        
        ## Check if the params are valid

        if not signature_params["keyId"] or not signature_params["signature"]:
            pass