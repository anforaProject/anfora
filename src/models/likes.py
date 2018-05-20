import datetime

from peewee import (DateTimeField, ForeignKeyField)

from models.base import BaseModel
from models.photo import Photo
from models.user import User

class Like(BaseModel):

    user = ForeignKeyField(User)
    photo = ForeignKeyField(Photo)
