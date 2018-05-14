import datetime

from peewee import (DatetimeField, CharField)

from models.base import BaseModel

class Hashtag(BaseModel):

    tag = CharField(max_length=100)
    created = DatetimeField(default=datetime.datetime.now)
