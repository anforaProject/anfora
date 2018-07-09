import datetime
import uuid

from peewee import (DateTimeField, CharField, ForeignKeyField, IntegerField)

from models.base import BaseModel
from models.status import Status

class Media(BaseModel):

    status = ForeignKeyField(Status, backref='media_object')
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    media_name = CharField(unique=True) #uuid 
    height = IntegerField()
    width = IntegerField()    
    mimetype = CharField()
    description = CharField(max_length=250)
    remote_url = CharField(max_length=400)
    duration = IntegerField(null=True) #If this media is a video fill this