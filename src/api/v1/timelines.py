import os
import json 

import redis
import falcon
from models.user import UserProfile
from models.status import Status 

class homeTimeline(object):

    def on_get(self, req, resp):
        id = req.context['user'].id
        r = redis.StrictRedis(host=os.environ.get('REDIS_HOST', 'localhost'))

        local = req.get_param('local') or False
        max_id = req.get_param('max_id') or None
        since_id = req.get_param('since_id') or None
        limit = req.get_param('limit') or 40
        statuses = []

        feed = 'feed:home:{}'.format(id)
        print(feed)
        for post in r.zrevrangebyscore(feed, 207, 0, score_cast_func = int):
            statuses.append(Status.get(id=post).to_json())
        print(statuses)
        resp.body=json.dumps(statuses, default=str)
        resp.status=falcon.HTTP_200