import datetime

from peewee import (ForeignKeyField, BooleanField, DateTimeField)

from models.base import BaseModel
from models.user import UserProfile

class FollowRequest(BaseModel):

    account = ForeignKeyField(UserProfile)
    target = ForeignKeyField(UserProfile)
    created_at = DateTimeField(default=datetime.datetime.now)


    def authorize(self):
        account.follow(target)
        #TODO: Add it to the notifications
        #MergeWorker(account, target)
        self.delete_instance()

    def reject(self):
        self.delete_instance()
    
    def notify(self):
        pass