import requests
import logging 
import uuid
from urllib.parse import urlparse

from settings import DOMAIN

from models.status import Status
from models.user import UserProfile

from managers.notification_manager import NotificationManager

from activityPub import activities
from activityPub.data_signature import *
from activityPub.activities import as_activitystream, Activity
from activityPub.activitypub import push_to_remote_actor
from activityPub.identity_manager import ActivityPubId

from api.v1.helpers import sign_data

from tasks.config import huey # import the huey we instantiated in config.py

from tasks.redis.spreadStatus import spread_status

logger = logging.getLogger(__name__)

@huey.task()
def handle_follow(activity, original=None):
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
            follower.follow(followed)
            NotificationManager(follower).create_follow_notification(followed)
            message = {
                "@context": "https://www.w3.org/ns/activitystreams",
                "type": "Accept",
                "to": follower.ap_id,
                "actor": followed.ap_id,

                "object": original,

                "id": followed.ap_id + '#accepts/follows/' + str(uuid.uuid4()),
            }


            response = push_to_remote_actor(follower, message)
            
            return response
    else:
        logging.error(f"User not found: {activity.object}")
        return False

    
@huey.task()
def handle_create(activity):

    PUBLIC_CONTEXT = "https://www.w3.org/ns/activitystreams#Public"

    # Confirm that the status has images on it. At least one

    attachments =  activity.object.attachment
    valid_atachments = []
    for attachment in attachments:
        if 'image' in attachment.type:
            valid_atachments.append(attachment) 

    # If not end the job
    if not len(valid_atachments):
        return 

    # Check who is the actor
    ap_id = ""
    if isinstance(activity.actor, activities.Actor):
        ap_id = activity.actor.id
    elif isinstance(activity.actor, str):
        ap_id = activity.actor

    # Get the profile of the creator
    actor = ActivityPubId(ap_id).get_or_create_remote_user()

    # Get the targets of the status
    targets = [x for x in activity.get("to", []) + activity.get("cc", []) + activity.get('bcc', [])]

    is_public =  PUBLIC_CONTEXT in targets

    followers_of = [ActivityPubId(x.replace('/followers', '')).get_or_create_remote_user() for x in targets]
    directs = [x.split('/')[-1] for x in targets if urlparse(x).hostname == DOMAIN]
    

    # Data for the new status
    note = activity.object
    data = {
        "caption": note.content,
        "visibility": is_public,
        "user": actor,
        "sensitive": False,
        "remote": True,
        "story": False,
        "ap_id": note.id,
        "identifier": note.id.split('/')[-1]
    }

    try:
        status = Status.create(**data)
        spread_status(status, [], False)
    except:
        return 

    