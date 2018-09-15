import datetime

from peewee import (DateTimeField, ForeignKeyField)

from models.base import BaseModel
from models.status import Status
from models.user import UserProfile

class Like(BaseModel):

    user = ForeignKeyField(UserProfile, backref='liked_posts', on_delete='CASCADE')
    status = ForeignKeyField(Status, backref='licked_by', on_delete='CASCADE')
    created_at = DateTimeField(default=datetime.datetime.now)
