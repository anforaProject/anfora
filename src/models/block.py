import datetime
import falcon

from peewee import (ForeignKeyField, BooleanField, DateTimeField)

from models.base import BaseModel
from models.user import UserProfile

class Block(BaseModel):

    account = ForeignKeyField(UserProfile)
    target = ForeignKeyField(UserProfile)
    created_at = DateTimeField(default=datetime.datetime.now)