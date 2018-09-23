import datetime
import uuid

from peewee import (DateTimeField, CharField, ForeignKeyField, 
                    IntegerField, FloatField, UUIDField)

from models.base import BaseModel
from models.status import Status

from urls import (URIs, uri)

class Media(BaseModel):

    status = ForeignKeyField(Status, backref='media_object', null=True, on_delete='CASCADE')
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
    def extension(self):
        if self.media_type == "image/jpeg":
            media_type = "jpg"
        elif self.media_type == 'video/mp4':
            media_type = 'mp4'
        else:
            media_type = 'jpg'

        return media_type


    @property
    def uris(self):
        return URIs(
            media=uri("media", {"id":self.media_name, "extension": self.extension}),
            preview=uri("preview", {"id":self.media_name})
        )

    def __str__(self):
        return f'{self.id} - {self.media_name}'

    def to_json(self):


        if self.media_type == "image/jpeg":
            media_type = "image"
        elif self.media_type == 'video/mp4':
            media_type = 'video'
        else:
            media_type = 'image'

        return {
            'id': self.media_name,
            'url': self.uris.media,
            'preview_url': self.uris.preview,
            'type': media_type,
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

    def to_activitystream(self):
        json = {
            "type": "Document",
            "name": self.media_name,
            "url": self.uris.media,
            "mediaType": self.media_type      
        }

        return json
