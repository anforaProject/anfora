import os
import json 

import redis
import aioredis

from tornado.web import HTTPError, RequestHandler
import tornado.ioloop

from api.v1.base_handler import BaseHandler, CustomError
from auth.token_auth import bearerAuth

from models.user import UserProfile
from models.status import Status 
from models.like import Like

from managers.timeline_manager import TimelineManager

class HomeTimeline(BaseHandler):

    @bearerAuth
    async def get(self, user):
        
        #r = await aioredis.create_connection(
        #    f"redis://{os.environ.get('REDIS_HOST', 'localhost')}", 
        #    loop=IOLoop.current().asyncio_loop,
        #    encoding='utf-8'
        #)

        local = self.get_argument('media_ids', False)
        max_id = self.get_argument('max_id', None) 
        since_id = self.get_argument('since_id', None)
        limit = self.get_argument('limit', 20)
        
        statuses = []
        errors = 0
        """
        for post in TimelineManager(user).query(since_id=since_id, max_id=max_id, local=True, limit=limit):
            try:
                status = self.application.objects.get(Status,id=int(post))
                json_data = status.to_json()
                count = await self.application.objects.count(Like.select().join(UserProfile).switch(Like).join(Status).switch(Like).where(Like.user.id == user.id, Like.status.id == status))
                if count:
                    json_data["favourited"] = True
                
                statuses.append(json_data)
            except:
                pass
        
        """
        ids = TimelineManager(user).query(since_id=since_id, max_id=max_id, local=True, limit=limit)
        statuses = await self.application.objects.execute(Status.select().where(Status.id << ids).order_by(Status.created_at))

        hydratated = []

        for status in statuses:
            json_data = status.to_json()
            count = await self.application.objects.count(Like.select().join(UserProfile).switch(Like).join(Status).switch(Like).where(Like.user.id == user.id, Like.status.id == status))
            if count:
                json_data["favourited"] = True
            
            hydratated.append(json_data)     

        self.write(json.dumps(hydratated[::-1], default=str))