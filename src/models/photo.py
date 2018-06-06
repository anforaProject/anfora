import datetime
import uuid
import binascii
import os
import json
import requests

from peewee import *
from playhouse.shortcuts import model_to_dict

from activityPub.helpers import (URIs, uri)
from models.base import BaseModel
from models.user import User
from models.album import Album

from activityPub import activities



class Photo(BaseModel):
    media_name = CharField(unique=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    message = TextField()
    media_type = CharField(max_length=20)
    public = BooleanField(default=True)
    user = ForeignKeyField(User, backref='photos')
    text = CharField(null=True)
    sensitive = BooleanField(default=False)
    height = IntegerField()
    width = IntegerField()
    description = CharField(max_length=200)
    remote = BooleanField(default = False)
    ap_id = CharField(null=True)
    #Need to add tagged users

    def __str__(self):
        return "{} - {} - {} - {}".format(self.message, self.media_name, self.created_at, self.remote)

    @property
    def uris(self):
        if self.remote:
            ap_id = self.ap_id
        else:
            ap_id = uri("photo", {"username":self.user.username, "id":self.id})
        return URIs(id=ap_id,
                    media=uri("media", {"id":self.media_name}),
                    preview=uri("preview", {"id":self.media_name})
                    )

    def to_activitystream(self):
        json = {
            "type": "Note",
            "id": self.uris.id,
            "description": self.description,
            "url": self.uris.media,
            "message": self.message,
            "hashtags": self.hashtags,
            "likes": self.likes_count(),
            "actor": activities.Actor(self.user),
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
                valid = not Photo.select().where(self.media_name == ident).exists()

            self.media_name = ident

        return super(Photo, self).save(*args, **kwargs)

    def albums(self):
        from models.albumRelation import RelationAlbumPhoto

        query = (RelationAlbumPhoto
                .select()
                .where(RelationAlbumPhoto.photo==self)
        )


        return [model_to_dict(rel,exclude=self._BaseModel__exclude([RelationAlbumPhoto.photo, RelationAlbumPhoto.id, RelationAlbumPhoto.album.user])) for rel in query]

    def to_model(self):
        return model_to_dict(self, exclude=self._BaseModel__exclude())

    def to_json(self):
        data = {
            "type": "Note",
            "id": self.uris.id,
            "description": self.description,
            "preview": self.uris.preview,
            "message": self.message,
            "hashtags": self.hashtags,
            "likes": self.likes_count(),
            "actor": self.user.to_api(),
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
        from models.likes import Like
        return Like.select().where(Like.photo == self).count()
