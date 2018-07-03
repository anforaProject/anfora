import datetime
import falcon

from peewee import (ForeignKeyField, BooleanField, DateTimeField)

from models.base import BaseModel
from models.user import User

class Block(BaseModel):

    account = ForeignKeyField(User)
    target = ForeignKeyField(User)
    created_at = DateTimeField(default=datetime.datetime.now)