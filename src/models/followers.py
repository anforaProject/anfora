import datetime

from peewee import (ForeignKeyField, BooleanField, DateTimeField)

from models.base import BaseModel
from models.user import UserProfile

class FollowerRelation(BaseModel):

    user = ForeignKeyField(UserProfile, on_delete='CASCADE')
    follows = ForeignKeyField(UserProfile, on_delete='CASCADE')
    valid = BooleanField(default=False) #Whether the follow request has been authored
    muting = BooleanField(default=False)
    muting_notifications = BooleanField(default=False)
    domain_blocking = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        indexes = (
        (('user', 'follows'), True),
        )

    def __str__(self):
        return "{} follows {}".format(self.user.username, self.follows.username)
