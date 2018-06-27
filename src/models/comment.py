import datetime

from peewee import (ForeignKeyField, DateTimeField)

from models.photo import Photo
from models.base import BaseModel
from models.hashtags import Hashtag
from models.user import User

class Comment(BaseModel):

    photo = ForeignKeyField(Photo, backref="comments")
    user = ForeignKeyField(User, backref="comments")
    created_at = DateTimeField(default=datetime.datetime.now)
