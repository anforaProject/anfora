import datetime
from peewee import *
from models.base import BaseModel
from models.user import UserProfile
from models.status import Status
from models.follow_request import *
from models.followers import FollowerRelation

notification_types = {'follow': 'Follow', 'like': 'Like', 'follow_request': 'Follow Request', 'mention': 'Mention', 'reblog': 'Reblog'}

class Notification(BaseModel):

    target = ForeignKeyField(UserProfile)
    user = ForeignKeyField(UserProfile)
    status = ForeignKeyField(Status, null=True)
    follow = ForeignKeyField(FollowerRelation, null=True)
    follow_request = ForeignKeyField(FollowRequest, null=True)
    notification_type = CharField(max_length=64)
    created_at = DateTimeField(default=datetime.datetime.now)

    def to_json(self):
        
        data = {
            'id': self.id,
            'account': self.user.to_json(),
            'type': notification_types[self.notification_type],
            'created_at': self.created_at,
        }

        if self.status:
            data['status'] = self.status.to_json(),

        return data
