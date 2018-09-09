import redis
import os
import json

from models.status import Status
from models.user import UserProfile
from models.notification import Notification, notification_types

from tasks.config import huey

from managers.timeline_manager import TimelineManager

@huey.task()
def spread_status(status):
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

@huey.task()
def like_status(status, user):

    """
        status - the status target of the like - Status
        user - the user liking the post - UserProfile
    """

    r = redis.StrictRedis(host=os.environ.get('REDIS_HOST', 'localhost'))
    
    #Add id to the like timeline
    TimelineManager(status.user).push_likes(status)
    
    notification = Notification.create(
        user = user,
        target = status.user,
        status = status,
        notification_type = notification_types['like']
    )

    json_file = json.dumps(status.json(), default=str)

    r.publish(f'timeline:{status.user.id}', f'notification {json_file}')
