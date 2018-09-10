import datetime
from peewee import *
from playhouse.shortcuts import model_to_dict

from .user import UserProfile
from .base import BaseModel

class Album(BaseModel):
    name = CharField()
    creted_date = DateTimeField(default=datetime.datetime.now)
    public = BooleanField(default=False)
    user = ForeignKeyField(UserProfile, backref='albums')
#   description = TextField()

    def to_model(self):
        return model_to_dict(self, exclude=self._BaseModel__exclude())
    
    def json(self):
        return json.dumps(self.to_model(), default=str)
