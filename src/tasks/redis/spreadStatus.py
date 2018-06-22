import redis

from models.photo import Photo
from models.user import User

from tasks.config import huey

@huey.task()
def spreadStatus(photo):
    r = redis.StrictRedis(host='localhost', port=6379)
    time = photo.created_at.timestamp()
    for follower in photo.user.followers():
        tagName = "{}:hometimeline".format(follower.username)
        r.zadd(tagName, time, photo.id)
