import datetime

from peewee import (DateTimeField, ForeignKeyField)

from models.base import BaseModel
from models.status import Status
from models.user import UserProfile

class Like(BaseModel):

    user = ForeignKeyField(UserProfile, backref='liked_posts')
    status = ForeignKeyField(Status, backref='licked_by')
    created_at = DateTimeField(default=datetime.datetime.now)
