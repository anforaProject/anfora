import datetime
import uuid
import binascii
import os
import json
import requests

from peewee import *
from playhouse.shortcuts import model_to_dict

from urls import (URIs, uri)
from models.base import BaseModel
from models.user import UserProfile
from models.album import Album


class Status(BaseModel):
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
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


    def to_activitystream(self):
        json = {
            "type": "Note",
            "id": self.id,
            "url": self.uris.media,
            "message": self.caption,
            #"hashtags": self.hashtags,
            "likes": self.likes_count(),
            "actor": self.user.uris.id,
            "is_sensitive": self.sensitive,
            "created_at": self.created_at.strftime('%Y-%m-%dT%H:%M:%S'),
            "attachment":[ media.to_activitystream() for media in self.media_object],
            "spoiler_text": self.spoiler_text,
            "reblogged": None,
            "favourited": None,
            "muted": None
        }

        return json

    def save(self,*args, **kwargs):
        if not self.ap_id:
            self.ap_id = self.uris.id

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
            "id": self.id,
            "description": self.caption,
            "preview": self.uris.preview,
            "message": self.caption,
            "hashtags": self.hashtags,
            "likes": self.likes_count(),
            "account": self.user.to_json(),
            "sensitive": self.sensitive,
            "created_at": self.created_at.strftime('%Y-%m-%dT%H:%M:%S'),
            "media_attachments":[]
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
