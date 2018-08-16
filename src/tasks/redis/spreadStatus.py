import redis
import os

from models.status import Status
from models.user import UserProfile

from tasks.config import huey

from utils.timeline_manager import TimelineManager

@huey.task()
def spread_status(status):
    r = redis.StrictRedis(host=os.environ.get('REDIS_HOST', 'localhost'))
    time = status.created_at.timestamp()

    #Populate all the followers timelines
    for follower in status.user.followers():
        TimelineManager(follower).push_home(status)
        r.publish(f'timeline:{follower.id}', f'CREATE {status.id}')

    #Add id to the own timeline
    TimelineManager(status.user).push_home(status)
