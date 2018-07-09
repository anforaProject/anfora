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
from models.user import User
from models.album import Album


class Status(BaseModel):
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    caption = TextField()
    public = BooleanField(default=True)
    user = ForeignKeyField(User, backref='photos')
    sensitive = BooleanField(default=False)
    remote = BooleanField(default = False)
    ap_id = CharField(null=True)
    in_reply_to = ForeignKeyField('self', backref='replies', null=True)
    story = BooleanField(default=False)
    #Need to add tagged users

    def __str__(self):
        return "{} - {} - {} - {}".format(self.caption, self.media_name, self.created_at, self.remote)

    @property
    def uris(self):
        if self.remote:
            ap_id = self.ap_id
        else:
            ap_id = uri("status", {"username":self.user.username, "id":self.id})
        return URIs(id=ap_id,
                    media=uri("media", {"id":self.media_name}),
                    preview=uri("preview", {"id":self.media_name})
                    )

    @property
    def media(self):
        from models.media import Media 

        return self.media_object.order_by(Media.id.desc())


    def to_activitystream(self):
        json = {
            "type": "Note",
            "id": self.uris.id,
            "url": self.uris.media,
            "message": self.caption,
            "hashtags": self.hashtags,
            "likes": self.likes_count(),
            "actor": self.user.uris.id,
            "sensitive": self.sensitive,
            "created_at": self.created_at.strftime('%Y-%m-%dT%H:%M:%S'),
            "media_url":self.uris.media,
            "preview_url":self.uris.preview
        }

        return json

    def save(self,*args, **kwargs):
        if not self.media_name:
            valid = False
            ident = ""
            while not valid:
                ident = str(uuid.uuid4())
                valid = not Status.select().where(self.media_name == ident).exists()

            self.media_name = ident

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
            "type": "Note",
            "id": self.uris.id,
            "description": self.caption,
            "preview": self.uris.preview,
            "message": self.caption,
            "hashtags": self.hashtags,
            "likes": self.likes_count(),
            "actor": self.user.to_json(),
            "sensitive": self.sensitive,
            "created_at": self.created_at.strftime('%Y-%m-%dT%H:%M:%S'),
            "media_url":self.uris.media,
            "preview_url":self.uris.preview
        }
        return data

    def hashtags(self):
        from models.hashtags import Hashtag
        tags = [x.tag for x in Hashtag.select().where(Hashtag.photo == self)]
        return list(map(lambda x: '#'+x, tags))

    def likes_count(self):
        from models.like import Like
        return Like.select().where(Like.photo == self).count()
