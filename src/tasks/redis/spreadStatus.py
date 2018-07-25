import redis
import os

from models.status import Status
from models.user import User

from tasks.config import huey

@huey.task()
def spreadStatus(photo):
    r = redis.StrictRedis(host=os.environ['REDIS_HOST'])
    time = photo.created_at.timestamp()

    #Populate all the followers timelines
    for follower in photo.user.followers():
        tagName = "{}:hometimeline".format(follower.username)
        r.zadd(tagName, time, photo.id)

    #Add id to the own timeline
    r.zadd("{}:hometimeline".format(photo.user.username), time, photo.id)
