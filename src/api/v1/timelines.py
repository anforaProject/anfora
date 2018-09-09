import os
import json 

import redis
import falcon
from models.user import UserProfile
from models.status import Status 

from managers.timeline_manager import TimelineManager

class homeTimeline(object):

    def on_get(self, req, resp):
        user = req.context['user']
        r = redis.StrictRedis(host=os.environ.get('REDIS_HOST', 'localhost'))

        local = req.get_param('local') or False
        max_id = req.get_param('max_id') or None
        since_id = req.get_param('since_id') or None
        limit = req.get_param('limit') or 20
        statuses = []
        errors = 0
        for post in TimelineManager(user).query(since_id=since_id, max_id=max_id, local=True, limit=limit):
            try:
                statuses.append(Status.get(id=int(post)).to_json())
            except:
                errors += 1
        
        resp.body=json.dumps(statuses, default=str)
        resp.status=falcon.HTTP_200