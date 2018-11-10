import json 
from models.user import User, UserProfile
from api.v1.base_handler import BaseHandler

class getActor(BaseHandler):

    def get(self, username):
        person = User.get_or_none(username=username)
        if person:
            person = person.profile.get()
            self.write(json.dumps(person.to_activitystream(), default=str))
            self.set_status(200)
        else:
            self.set_status(200)