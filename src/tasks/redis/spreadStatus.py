import redis
import os
import json
from typing import List 

from models.status import Status
from models.user import (User, UserProfile)
from models.notification import Notification, notification_types
from models.followers import FollowerRelation

from tasks.config import huey

from managers.timeline_manager import TimelineManager
from managers.notification_manager import NotificationManager

from activityPub.create_activities import generate_create_note
from activityPub.identity_manager import ActivityPubId
from activityPub.activitypub import push_to_remote_actor

@huey.task(retries=3, retry_delay=5)
def spread_status(status: Status, mentions: List[str], ap_spread: bool = False) -> None:
    """
    Given a status we have to: 

    - Populate users timelines
    - Notifiy mentions
    - Send via AP TODO

    if we are spreading to local follers (for example from a external
    request) the ap_spread should be false but if the local user is the
    one creating the spread tag we should use ap_spread = true

    """
    r = redis.StrictRedis(host=os.environ.get('REDIS_HOST', 'localhost'))
    time = status.created_at.timestamp()

    #Populate all the followers timelines
    json_file = json.dumps(status.to_json(), default=str)
    for follower in status.user.followers():
        TimelineManager(follower).push_home(status)
        # Add it to notifications
        r.publish(f'timeline:{follower.id}', f'update {json_file}')

    #Add id to the own timeline
    TimelineManager(status.user).push_home(status)
    r.publish(f'timeline:{status.user.id}', f'update {json_file}')

    # Notify mentioned people 
    
    remote = []

    # Notify mentions
    for user in mentions:
        # We have two formats: local user and remote user 
        # if the user is local the user string is of the from 
        # 'username' otherwise is 'username@instance.ltd' 

        #target_user = User.get_or_none(User.username==user)
        target_user = ActivityPubId(user).get_or_create_remote_user()
        if target_user:
            # First we check that there is an user with this username
            # and then we get it's profile 
            if not target_user.is_remote:
                NotificationManager(status.user).create_mention_notification(target_user)
            else:
                remote.append(target_user)

    # Spread via AP 
    if ap_spread:
        create = generate_create_note(status, remote)
        
        # Can this be the coolest var in the project?
        # it's just a set of addresses. Here I'm taking care
        # to minimize the number of requests to external actors
        # targeting shared inboxes (like a pro, look at me mom)

        targets_spotted = set()

        remote_followers = (UserProfile
                            .select()
                            .join(FollowerRelation, on=FollowerRelation.user)
                            .where( (UserProfile.is_remote == True) & (FollowerRelation.follows == status.user) ))

        for follower in remote_followers:
            if follower.public_inbox:
                targets_spotted.add(follower.public_inbox)
            else:
                targets_spotted.add(follower.uris.inbox)

        # We're ready mike, drop cargo to the target
        print(targets_spotted)
        for inbox in targets_spotted:
            push_to_remote_actor(inbox, create.to_json())
    
    
@huey.task()
def like_status(status: Status, user: UserProfile) -> None:

    """
        status - the status target of the like - Status
        user - the user liking the post - UserProfile
    """

    r = redis.StrictRedis(host=os.environ.get('REDIS_HOST', 'localhost'))
    
    NotificationManager(user).create_like_notification(status)

    json_file = json.dumps(status.to_json(), default=str)

    r.publish(f'timeline:{status.user.id}', f'notification {json_file}')
