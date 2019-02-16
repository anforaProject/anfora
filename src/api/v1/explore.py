import json

from models.user import UserProfile
from api.v1.base_handler import BaseHandler
from models.status import Status
class ExploreUsers(BaseHandler):

    async def get(self):

        query = await self.application.objects.execute(UserProfile.select().limit(5))
        
        data = [n.to_json() for n in query]

        self.write(json.dumps(data, default=str))
        self.set_status(200)

class ExploreStatuses(BaseHandler):

    async def get(self):

        query = await self.application.objects.execute(Status.select().where(Status.in_reply_to==None).limit(33))
        
        data = [n.to_json() for n in query]

        self.write(json.dumps(data, default=str))
        self.set_status(200)

class ExploreServer(BaseHandler):

    async def get(self):

        users = await self.application.objects.execute(UserProfile.select().limit(5))
        posts = await self.application.objects.execute(Status.select().where(Status.in_reply_to==None).limit(15))

        data = {
            'users': [user.to_json() for user in users],
            'statuses': [status.to_json() for status in posts]
        }

        self.write(json.dumps(data, default=str))
        self.set_status(200)