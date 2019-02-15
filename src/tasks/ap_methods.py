import requests
import logging 
import uuid

from settings import DOMAIN

from models.status import Status
from models.user import UserProfile


from activityPub import activities
from activityPub.data_signature import *
from activityPub.activities import as_activitystream, Activity
from activityPub.activitypub import push_to_remote_actor
from activityPub.identity_manager import ActivityPubId

from api.v1.helpers import sign_data

from tasks.config import huey # import the huey we instantiated in config.py

logger = logging.getLogger(__name__)

@huey.task()
def handle_follow(activity):
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
                    "id": activity.id,
                    "object": activity.object,
                    "actor": follower.ap_id
                },

                "id": "https://{}/activities/{}".format('anfora.test', uuid.uuid4()),
            }


            response = push_to_remote_actor(follower, message)
            
            return response
    else:
        logging.error(f"User not found: {activity.object}")
        return False

    
    