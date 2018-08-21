import redis
import os
import json

from models.status import Status
from models.user import UserProfile

from tasks.config import huey

from utils.timeline_manager import TimelineManager

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
