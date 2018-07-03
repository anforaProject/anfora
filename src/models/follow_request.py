import datetime
import falcon

from peewee import (ForeignKeyField, BooleanField, DateTimeField)

from models.base import BaseModel
from models.user import User

class FollowRequest(BaseModel):

    account = ForeignKeyField(User)
    target = ForeignKeyField(User)
    created_at = DateTimeField(default=datetime.datetime.now)


    def authorize(self):
        account.follow(target)
        #TODO: Add it to the notifications
        #MergeWorker(account, target)
        self.delete_instance()

    def reject(self):
        self.delete_instance()