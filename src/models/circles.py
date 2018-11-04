from peewee import DateTimeField, ForeignKeyField, CharField, TextField, BooleanField
from playhouse.shortcuts import model_to_dict

from .user import UserProfile
from .base import BaseModel

class Circle(BaseModel):
    name = CharField(max_length=120)
    public = BooleanField(default=False)
    user = ForeignKeyField(UserProfile, backref='circles')
    description = TextField()
    members = ForeignKeyField(UserProfile, null=True)
    
    def to_json(self):

        return {
            'name': self.name,
            'public': self.public,
            'user': self.user.to_json(),
            'description': self.description,
            'members': [x.to_json() for x in self.members]
        }


