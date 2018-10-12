import redis
import os
import json

from models.status import Status
from models.user import UserProfile
from models.notification import Notification, notification_types

from tasks.config import huey

from managers.timeline_manager import TimelineManager

@huey.task()
def remove_status(status):
    r = redis.StrictRedis(host=os.environ.get('REDIS_HOST', 'localhost'))

    # Remove it from the own timeline
    TimelineManager(status.user).remove_from_home(status)
    # Remove it from the followers timeline
    for follower in status.user.followers():
        TimelineManager(follower).remove_from_home(status)
    
    #Update the user posts count

    UserProfile.update({UserProfile.statuses_count: UserProfile.statuses_count - 1}).where(UserProfile.id == status.user.id).execute()

    # Remove the status
    status.delete_instance().execute()