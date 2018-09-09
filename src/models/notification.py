import datetime
from peewee import *
from models.base import BaseModel
from models.user import UserProfile
from models.status import Status

notification_types = {'follow': 'Follow', 'like': 'Like', 'follow_request': 'Follow Request', 'mention': 'Mention', 'reblog': 'Reblog'}

class Notification(BaseModel):

    target = ForeignKeyField(UserProfile)
    user = ForeignKeyField(UserProfile)
    status = ForeignKeyField(Status, null=True)
    notification_type = CharField(max_length=64)
    created_at = DateTimeField(default=datetime.datetime.now)

    def json(self):
        
        return {
            'id': self.id,
            'account': self.user.to_json(),
            'status': self.status.to_json(),
            'type': self.notification_type,
            'created_at': self.created_at,
        }