from huey import RedisHuey
import os

huey = RedisHuey(host=os.environ.get('REDIS_HOST', 'localhost'))
