import redis
import peewee
import os

from models.base import db as database
from models.user import UserProfile
from models.status import Status

def build_all_timelines():
    r = redis.StrictRedis(host=os.environ.get('REDIS_HOST', 'localhost'))
    database.connect()
    users = UserProfile.select()
    total = users.count()
    for index,user in enumerate(users):
        print("Distributing {}'s timeline. {} of {}".format(user.username, index, total))

        #This can be done using a zip function and 2 generators but I have more
        #access to the db. This way I'm using more memory
        pairs = ((photo.id,photo.id) for photo in user.statuses)
        pairs = [item for pair in pairs for item in pair]
        for follower in user.followers():
            if pairs:
                tagName = "feed:home:{}".format(follower.id)
                r.zadd(tagName, *pairs)
        
        if pairs:
            tagName = "feed:home:{}".format(user.id)
            r.zadd(tagName, *pairs)

    if not database.is_closed():
        database.close()

def showTimelines():
    r = redis.StrictRedis(host=os.environ.get('REDIS_HOST', 'localhost'))
    print(r.zrange('feed:home:test0', 0, -1, withscores=True))
