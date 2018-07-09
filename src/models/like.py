import datetime

from peewee import (DateTimeField, ForeignKeyField)

from models.base import BaseModel
from models.status import Status
from models.user import User

class Like(BaseModel):

    user = ForeignKeyField(User, backref='liked_posts')
    photo = ForeignKeyField(Status, backref='licked_by')
    created_at = DateTimeField(default=datetime.datetime.now)
