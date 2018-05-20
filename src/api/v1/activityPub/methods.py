import json
from urllib.parse import urlparse

import requests

from models.activity import Activity
from activityPub import activities
from activityPub.activities import as_activitystream

from models.user import User
from models.followers import FollowerRelation

def dereference(ap_id, type=None):
    print("=> dereference {}".format(ap_id))
    res = requests.get(ap_id)
    try:
        if res.status_code != 200:
            raise Exception("Failed to dereference {0}".format(ap_id))

        return json.loads(res.text, object_hook=as_activitystream)
    except:
        raise Exception("Error connecting server")

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

def get_or_create_remote_user(ap_id):
    user = User.get_or_none(ap_id=ap_id)
    if not user:
        user = dereference(ap_id)
        hostname = urlparse(user.id).hostname
        username = "{0}@{1}".format(user.preferredUsername, hostname)
        print(user)
        user = User.create(
            username=username,
            name=user.preferredUsername,
            ap_id=user.id,
            remote=True,
            password = "what"
        )
    #print(user)
    return user

def handle_follow(activity):
    followed = User.get_or_none(ap_id=activity.object)
    print("=> Handling follow")
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

        response = {"Type": "Accept", "Object":activity}


    else:
        print("error handling follow")

def handle_note(activity):
    if isinstance(activity.actor, activities.Actor):
        ap_id = activity.actor.id
    elif isinstance(activity.actor, str):
        ap_id = activity.actor

    person = get_or_create_remote_user(ap_id)

    note = Photo.get_or_none(ap_id=activity.object.id)

    if not note:
        Photo.create(
            content=activity.object.content,
            person=person,
            ap_id=activity.object.id,
            remote=True
        )
