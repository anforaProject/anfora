from huey import RedisHuey
import os

huey = RedisHuey(host=os.environ['REDIS_HOST'])
