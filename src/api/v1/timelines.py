import os
import json 

import redis
import falcon
from models.user import UserProfile
from models.status import Status 
from models.like import Like

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
            status = Status.get(id=int(post))
            json_data = status.to_json()
            if Like.select().join(UserProfile).switch(Like).join(Status).switch(Like).where(Like.user.id == user.id, Like.status.id == status).count():
                json_data["favourited"] = True
            
            statuses.append(json_data)
        
        resp.body=json.dumps(statuses, default=str)
        resp.status=falcon.HTTP_200