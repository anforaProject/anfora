import datetime
import uuid
import binascii
import os
import json
import requests
from hashids import Hashids

from peewee import *
from playhouse.shortcuts import model_to_dict

from urls import (URIs, uri)
from models.base import BaseModel
from models.user import UserProfile
from models.album import Album

from settings import (MEDIA_FOLDER, salt_code)

def random():
    return os.urandom(5).hex()

class Status(BaseModel):
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)
    caption = TextField()
    spoiler_text = CharField(max_length=255, null=True)
    is_public = BooleanField(default=True)
    user = ForeignKeyField(UserProfile, backref='statuses', on_delete='CASCADE')
    sensitive = BooleanField(default=False)
    remote = BooleanField(default = False)
    ap_id = CharField(null=True)
    in_reply_to = ForeignKeyField('self', backref='replies', null=True)
    is_story = BooleanField(default=False)
    favourites_count = IntegerField(default=0)
    reblogs_count = IntegerField(default=0)
    replies_count = IntegerField(default=0)
    identifier = CharField(max_length=20, null=False, default="1")
    #Need to add tagged users
    
    def __str__(self):
        return "{} - {} - {} - {}".format(self.caption, self.ap_id, self.created_at, self.remote)

    @property
    def uris(self):
        from models.media import Media
        if self.remote:
            ap_id = self.ap_id
        else:
            ap_id = uri("status", {"username":self.user.username, "id":self.id})
            
        return URIs(id=ap_id,
                    url = uri("status_client_url", {"username": self.user.username, "id": self.id }), 
                    media=[uri.uris.media for uri in self.media_object],
                    preview=[uri.uris.preview for uri in self.media_object]
                    )

    @property
    def media(self):
        from models.media import Media 

        return self.media_object.order_by(Media.id.desc())
        
    @property
    def media_data(self):
        return {"hola": 3}

    def generate_id(self):
        hashids = Hashids(salt=salt_code, min_length=9)
        return hashids.encode(self.id)

    def to_activitystream(self):
        json = {
            "id": uri("status", {"username":self.user.username, "id":self.id}),
            "type": "Note",
            "summary": None,
            
            "published": self.created_at.replace(microsecond=0).isoformat() + "Z",
            "url": self.uris.url,
            "attributedTo": self.user.ap_id,
            #"hashtags": self.hashtags,
            "sensitive": self.sensitive,
            "attachment":[ media.to_activitystream() for media in self.media_object],
            "spoiler_text": self.spoiler_text,
            "content": self.caption,
        }

        if self.is_public:
            json['to'] = ["https://www.w3.org/ns/activitystreams#Public"]
        else:
            json['to'] = []
        
        json['cc'] = [self.user.uris.followers] 

        return json

    def save(self,*args, **kwargs):
        if not self.ap_id:
            self.ap_id = uri("status", {"username":self.user.username, "id":self.id})

        if not self.identifier:
            self.identifier = self.generate_id()

        return super(Status, self).save(*args, **kwargs)

    def albums(self):
        from models.albumRelation import RelationAlbumStatus

        query = (RelationAlbumStatus
                .select()
                .where(RelationAlbumStatus.photo==self)
        )


        return [model_to_dict(rel,exclude=self._BaseModel__exclude([RelationAlbumStatus.photo, RelationAlbumStatus.id, RelationAlbumStatus.album.user])) for rel in query]

    def to_model(self):
        return model_to_dict(self, exclude=self._BaseModel__exclude())

    def to_json(self):
        data = {
            "id": self.identifier,
            "description": self.caption,
            "message": self.caption,
            "hashtags": self.hashtags,
            "likes": self.likes_count(),
            "account": self.user.to_json(),
            "sensitive": self.sensitive,
            "created_at": self.created_at.strftime('%Y-%m-%dT%H:%M:%S'),
            "media_attachments":[],
            "comments": [x.to_json() for x in self.replies]

        }

        for media in self.media_object:
            data['media_attachments'].append(media.to_json())

        return data

    def hashtags(self):
        from models.hashtags import Hashtag
        tags = [x.tag for x in Hashtag.select().where(Hashtag.photo == self)]
        return list(map(lambda x: '#'+x, tags))

    def likes_count(self):
        from models.like import Like
        return Like.select().where(Like.status == self).count()
