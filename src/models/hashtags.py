import datetime

from peewee import (DateTimeField, CharField)

from models.base import BaseModel

class Hashtag(BaseModel):

    tag = CharField(max_length=100)
    created = DateTimeField(default=datetime.datetime.now)
