from datetime import datetime

from peewee import *

from models.base import BaseModel
from models.user import User
from helpers import URI

class Activity(BaseModel):
    id = TextField()
    payload = TextField()
    created_at = DateTimeField(default=datetime.now)
    type = CharField()
    remote = BooleanField(default=False)
    person = ForeignKeyField(User)
