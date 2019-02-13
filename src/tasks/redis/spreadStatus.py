import redis
import os
import json
from typing import List 

from models.status import Status
from models.user import (User, UserProfile)
from models.notification import Notification, notification_types

from tasks.config import huey

from managers.timeline_manager import TimelineManager
from managers.notification_manager import NotificationManager

from activityPub.create_activities import generate_create_note
from activityPub.identity_manager import ActivityPubId
@huey.task()
def spread_status(status: Status, mentions: List[str]) -> None:
    """
    Given a status we have to: 

    - Populate users timelines
    - Notifiy mentions
    - Send via AP TODO

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
                NotificationManager(status.user).create_mention_notification(profile)
            else:
                remote.append(target_user)

    # Spread via AP 
    create = generate_create_note(status, remote)
    print(create)
    
    
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
