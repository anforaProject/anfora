import datetime
import falcon

from peewee import (ForeignKeyField, BooleanField, DateTimeField)

from models.base import BaseModel
from models.user import UserProfile

class Block(BaseModel):

    account = ForeignKeyField(UserProfile, on_delete='CASCADE')
    target = ForeignKeyField(UserProfile, on_delete='CASCADE')
    created_at = DateTimeField(default=datetime.datetime.now)