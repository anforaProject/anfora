from peewee import (ForeignKeyField, BooleanField)

from models.base import BaseModel
from models.user import User

class FollowerRelation(BaseModel):

    user = ForeignKeyField(User)
    follows = ForeignKeyField(User)
    valid = BooleanField(default=False)

    class Meta:
        indexes = (
        (('user', 'follows'), True),
        )

    def __str__(self):
        return "{} follows {}".format(self.user.username, self.follows.username)
