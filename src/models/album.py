import datetime
from peewee import *
from hashids import Hashids

from playhouse.shortcuts import model_to_dict

from .user import UserProfile
from .base import BaseModel

from settings import (MEDIA_FOLDER, salt_code)


class Album(BaseModel):
    name = CharField(max_length=200)
    identifier = CharField(max_length=30, default="1")
    created_date = DateTimeField(default=datetime.datetime.now)
    public = BooleanField(default=False)
    user = ForeignKeyField(UserProfile, backref='albums')
    description = TextField()

    def generate_id(self):
        hashids = Hashids(salt=salt_code, min_length=9)
        return hashids.encode(self.id)

    def save(self,*args, **kwargs):
        if not self.identifier:
            self.identifier = self.generate_id()

    def to_json(self):
        return {
            'name': self.name,
            'created_date': self.created_date,
            'public': self.public,
            'user': self.user,
            'description': self.description
        }
