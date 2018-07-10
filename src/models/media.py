import datetime
import uuid

from peewee import (DateTimeField, CharField, ForeignKeyField, 
                    IntegerField, FloatField, UUIDField)

from models.base import BaseModel
from models.status import Status

from urls import (URIs, uri)

class Media(BaseModel):

    status = ForeignKeyField(Status, backref='media_object', null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    media_name = UUIDField(unique=True)  
    height = IntegerField()
    width = IntegerField()
    focus_x = FloatField()
    focus_y = FloatField()   
    media_type = CharField()
    description = CharField(max_length=420)
    remote_url = CharField(max_length=400, null=True) #If this was a remote file. Specify origin url
    duration = IntegerField(null=True) #If this media is a video fill this

    @property
    def uris(self):
        return URIs(
            media=uri("media", {"id":self.media_name}),
            preview=uri("preview", {"id":self.media_name})
        )

    def to_json(self):
        return {
            'id': self.media_name,
            'type': self.type,
            'url': self.uris.media,
            'preview_url': self.uris.preview,
            'meta': {
                'focus': {
                    'x': self.focus_x,
                    'y': self.focus_y
                }
            },
            'description': self.description
        }