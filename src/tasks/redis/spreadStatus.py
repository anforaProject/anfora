import redis
import os

from models.status import Status
from models.user import UserProfile

from tasks.config import huey

@huey.task()
def spread_status(status):
    r = redis.StrictRedis(host=os.environ.get('REDIS_HOST', 'localhost'))
    time = status.created_at.timestamp()

    #Populate all the followers timelines
    for follower in status.user.followers():
        tagName = "feed:home:{}".format(follower.id)
        r.zadd(tagName, status.id, time)
        r.publish(f'timeline:{follower.id}', f'CREATE {status.id}')

    #Add id to the own timeline
    r.zadd("feed:home:{}".format(status.user.id), time, status.id)
