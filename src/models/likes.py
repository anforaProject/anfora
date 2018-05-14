import datetime

from peewee import (DateTimeField, ForeignKeyField)

from models.base import BaseMode
from models.photo import Photo
from models.user import User

class Like(BaseModel):

    user = ForeignKeyField(User)
    photo = ForeignKeyField(Photo)