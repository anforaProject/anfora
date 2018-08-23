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
    media_name = CharField(unique=True)  
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

    def __str__(self):
        return f'{self.id} - {self.media_name}'

    def to_json(self):
        return {
            'id': self.media_name,
            'url': self.uris.media,
            'preview_url': self.uris.preview,
            'meta': {
                'original':{
                    'width': self.width,
                    'height': self.height,
                    'size': f'{self.width}x{self.height}',
                    'aspect': self.width/self.height
                },
                'focus': {
                    'x': self.focus_x,
                    'y': self.focus_y
                }
            },
            'description': self.description
        }

    def to_activitystrem(self):
        json = {
            "type": "Document"      
        }

        return json
