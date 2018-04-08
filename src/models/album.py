import datetime
from peewee import *
from playhouse.shortcuts import model_to_dict

from .user import User
from .base import BaseModel

class Album(BaseModel):
    name = CharField()
    creted_date = DateTimeField(default=datetime.datetime.now)
    public = BooleanField(default=False)
    user = ForeignKeyField(User, backref='albums')
    
    def json(self):
        return model_to_dict(self, exclude=self._BaseModel__exclude())
