import redis
import peewee

from models.base import db as database
from models.user import User
from models.photo import Photo

def build_all_timelines():
    r = redis.StrictRedis(host='localhost', port=6379)
    database.connect()
    users = User.select()
    total = users.count()
    for index,user in enumerate(users):
        print("Distributing {}'s timeline. {} of {}".format(user.username, index, total))

        #This can be done using a zip function and 2 generators but I have more
        #access to the db. This way I'm using more memory
        pairs = list((photo.created_at.timestamp(),photo.id) for photo in user.photos)
        pairs = [item for pair in pairs for item in pair]
        for follower in user.followers():
            tagName = "{}:hometimeline".format(follower.username)
            r.zadd(tagName, *pairs)

    if not database.is_closed():
        database.close()

def show():
    r = redis.StrictRedis(host='localhost', port=6379)
    print(r.zrange('lol:hometimeline', 0, -1, withscores=True))
#build_all_timelines()
show()
