import datetime
from peewee import *
from playhouse.shortcuts import model_to_dict

from .user import UserProfile
from .base import BaseModel

class Album(BaseModel):
    name = CharField(max_length=200)
    created_date = DateTimeField(default=datetime.datetime.now)
    public = BooleanField(default=False)
    user = ForeignKeyField(UserProfile, backref='albums')
    description = TextField()

    def json(self):
        return {
            'name': self.name,
            'created_date': self.created_date,
            'public': self.public,
            'user': self.user,
            'description': self.description
        }
