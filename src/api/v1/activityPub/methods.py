import json
import requests
import datetime
import logging

from settings import DOMAIN

#Models
from models.user import UserProfile
from models.followers import FollowerRelation
from models.follow_request import FollowRequest

#ActivityPub things
from activityPub import activities
from activityPub.activities import as_activitystream
from activityPub.data_signature import *
from activityPub.activities.verbs import Activity, Accept

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    followed = UserProfile.get_or_none(ap_id=activity.object)
    print(activity.object)
    if followed:
        ap_id = ""
        if isinstance(activity.actor, activities.Actor):
            ap_id = activity.actor.id
        elif isinstance(activity.actor, str):
            ap_id = activity.actor

        follower = ActivityPubId(ap_id).get_or_create_remote_user()

        if followed.is_private:
            FollowRequest.create(
                account = follower,
                target = followed
            )
        else:
            follower.follow(followed, valid=True)
            t = Accept(object=activity,actor=followed.ap_id)
            data = LinkedDataSignature(t.to_json())
            signed = data.sign(followed)

            headers = {
                'date': f'{datetime.datetime.utcnow():%d-%b-%YT%H:%M:%SZ}',
                "(request-target)": follower.uris.inbox,
                "content-type": "application/activity+json",
                "host": DOMAIN,                
            }

            signature = SignatureVerification(headers, method="POST", path=activity.actor + '/inbox').sign(followed)

            
            headers.update({'signature': signature})

            logger.debug('Records: %s', headers)

            r = requests.post(follower.ap_id, data = signed, headers=headers )
            print(r.status_code)
            logger.debug('Records: %s', r.status_code + "\n" + r.json())
            print("sent ", signed, signature)
            return True
    else:
        return False

def handle_note(activity):
    if isinstance(activity.actor, activities.Actor):
        ap_id = activity.actor.id
    elif isinstance(activity.actor, str):
        ap_id = activity.actor

    person = ActivityPubId(ap_id).get_or_create_remote_user()

    note = Status.get_or_none(ap_id=activity.object.id)

    if not note:
        Status.create(
            content=activity.object.content,
            person=person,
            ap_id=activity.object.id,
            remote=True
        )