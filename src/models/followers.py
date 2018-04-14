from peewee import ForeignKeyField

from .base import BaseModel
from .photo import User

class FollowerRelation(BaseModel):

    user = ForeignKeyField(User)
    follows = ForeignKeyField(User)

    class Meta:
        indexes = (
        (('user', 'follows'), True),
        )
