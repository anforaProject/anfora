import json
from urllib.parse import urlparse

import requests

from activityPub import activities
from models.activity import Activity
from activityPub import activities
from activityPub.activities import as_activitystream

from models.user import User
from models.followers import FollowerRelation

def dereference(ap_id, type=None):
    res = requests.get(ap_id)
    if res.status_code != 200:
        raise Exception("Failed to dereference {0}".format(ap_id))

    return json.loads(res.text, object_hook=as_activitystream)


def get_final_audience(audience):
    final_audience = []
    for ap_id in audience:
        obj = dereference(ap_id)
        if isinstance(obj, activities.Collection):
            final_audience += [item.id for item in obj.items]
        elif isinstance(obj, activities.Actor):
            final_audience.append(obj.id)
    return set(final_audience)

def deliver_to(ap_id, activity):
    obj = dereference(ap_id)
    if not getattr(obj, "inbox", None):
        # XXX: log this
        return

    res = requests.post(obj.inbox, json=activity.to_json(context=True))
    if res.status_code != 200:
        msg = "Failed to deliver activity {0} to {1}"
        msg = msg.format(activity.type, obj.inbox)
        raise Exception(msg)


def deliver(activity):
    audience = activity.get_audience()
    activity = activity.strip_audience()
    audiente = get_final_audience(audience)
    for ap_id in audience:
        deliver_to(ap_id, activity)


def store(activity, person, remote=False):
    payload  = bytes(json.dumps(activity.to_json()), "utf-8")
    obj = Activity(payload=payload, person=person, remote=remote)
    if remote:
        obj.ap_id = activity.id
    obj.save()
    return obj.id

def get_or_create_remote_user(ap_id):
    user = User.get_or_none(ap_id=ap_id)
    if not user:
        user = dereference(ap_id)
        hostname = urlparse(user.id).hostname
        username = "{0}@{1}".format(user.preferredUsername, hostname)

        user = User.create(
            username=username,
            name=user.name,
            ap_id=user.id,
            remote=True,
            password = "what"
        )
    print(user)
    return user

def handle_follow(activity):
    followed = User.get_or_none(ap_id=activity.object)
    print("call")
    if followed:
        if isinstance(activity.actor, activities.Actor):
            ap_id = activity.actor.id
        elif isinstance(activity.actor, str):
            ap_id = activity.actor

        follower = get_or_create_remote_user(ap_id)
        FollowerRelation.create(
            user = follower,
            follows = followed
        )
        print("Created")
    else:
        print("error handling follow")
