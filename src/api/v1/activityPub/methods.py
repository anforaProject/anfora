import json
import requests
import datetime
import logger
import os
import aiohttp
import uuid
from settings import DOMAIN, BASE_URL
import socket
import ssl

#Models
from models.user import UserProfile
from models.followers import FollowerRelation
from models.follow_request import FollowRequest

#ActivityPub things
from activityPub import activities
from activityPub.activities import as_activitystream
from activityPub.data_signature import *
from activityPub.activities.verbs import Activity, Accept
from managers.notification_manager import NotificationManager

from activityPub.data_signature import sign_headers
from .http_debug import http_debug
from keys import PRIVKEY, PUBKEY, KEYS

PRIVKEYT = RSA.importKey(KEYS["actorKeys"]["privateKey"])

async def push_to_remote_actor(actor:UserProfile , message: dict, user_key_id:str):

    inbox = actor.uris.inbox
    data = json.dumps(message)
    headers = {
        '(request-target)': 'post {}'.format(inbox),
        'Content-Length': str(len(data)),
        'Content-Type': 'application/activity+json',
        'User-Agent': 'Anfora'
    }

    headers['signature'] = sign_headers(headers, PRIVKEYT, user_key_id)
    headers.pop('(request-target)')
    logging.info('%r >> %r', inbox, message)


    conn = aiohttp.TCPConnector(
        family=socket.AF_INET,
        verify_ssl=False,
        
    )

    try:
        async with aiohttp.ClientSession(connector = conn, trace_configs=[http_debug()]) as session:
            async with session.post(inbox, data=data, headers=headers) as resp:
                if resp.status == 202:
                    return
                resp_payload = await resp.text()
                logging.debug('%r >> resp %r', inbox, resp_payload)
    except Exception as e:
        logging.info('Caught %r while pushing to %r.', e, inbox)


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

async def handle_follow(activity):

    # Find if the target user is in our system
    followed = UserProfile.get_or_none(ap_id=activity.object)
    
    if followed:
        logging.debug(f"Starting follow process for {followed.username}")
        # Get the ap_id for the actor
        ap_id = ""
        if isinstance(activity.actor, activities.Actor):
            ap_id = activity.actor.id
        elif isinstance(activity.actor, str):
            ap_id = activity.actor

        # A representation of the remote user
        follower = ActivityPubId(ap_id).get_or_create_remote_user()
        logging.debug(f"New follower: {follower}")
        # Handle if the user must manually approve request 
        if followed.is_private:
            FollowRequest.create(
                account = follower,
                target = followed
            )
        else:

            # Handle local things
            #follower.follow(followed)
            #NotificationManager(follower).create_follow_notification(followed)

            message = {
                "@context": "https://www.w3.org/ns/activitystreams",
                "type": "Accept",
                "to": follower.uris.inbox,
                "actor": followed.ap_id,

                # this is wrong per litepub, but mastodon < 2.4 is not compliant with that profile.
                "object": {
                    "type": "Follow",
                    "id": followed.ap_id,
                    "object": "https://{}/actor".format('pleroma.test'),
                    "actor": follower.ap_id
                },

                "id": "https://{}/activities/{}".format('anfora.test', uuid.uuid4()),
            }


            await push_to_remote_actor(follower, message , f'{BASE_URL}/actor#main-key')
            return True
    else:
        logging.error(f"User not found: {activity.object}")
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

