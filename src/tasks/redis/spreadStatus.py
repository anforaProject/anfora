import redis
import os

from models.status import Status
from models.user import UserProfile

from tasks.config import huey

@huey.task()
def spreadStatus(photo):
    r = redis.StrictRedis(host=os.environ.get('REDIS_HOST', 'localhost'))
    time = photo.created_at.timestamp()

    #Populate all the followers timelines
    for follower in photo.user.followers():
        tagName = "{}:hometimeline".format(follower.username)
        r.zadd(tagName, time, photo.id)

    #Add id to the own timeline
    r.zadd("{}:hometimeline".format(photo.user.username), time, photo.id)
