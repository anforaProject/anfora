import json

from models.user import UserProfile
from api.v1.base_handler import BaseHandler

class ExploreUsers(BaseHandler):

    async def get(self):

        query = await self.application.objects.execute(UserProfile.select().limit(5))
        
        data = [n.to_json() for n in query]

        self.write(json.dumps(data, default=str))
        self.set_status(200)