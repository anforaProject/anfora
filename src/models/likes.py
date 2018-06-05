import datetime

from peewee import (DateTimeField, ForeignKeyField)

from models.base import BaseModel
from models.photo import Photo
from models.user import User

class Like(BaseModel):

    user = ForeignKeyField(User, backref='liked_posts')
    photo = ForeignKeyField(Photo, backref='licked_by')
