import redis
import os
import json

from models.status import Status
from models.user import UserProfile
from models.notification import Notification, notification_types

from tasks.config import huey

from managers.timeline_manager import TimelineManager

@huey.task()
def add_to_timeline(user, target):
    r = redis.StrictRedis(host=os.environ.get('REDIS_HOST', 'localhost'))
    for status in target.statuses:
        TimelineManager(user).push_home(status)


@huey.task()
def remove_from_timeline(user, target):
    r = redis.StrictRedis(host=os.environ.get('REDIS_HOST', 'localhost'))
    for status in target.statuses:
        TimelineManager(user).remove_from_home(status)

