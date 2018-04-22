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
    #Need to add tagged users

    def __str__(self):
        return "{} - {} - {}".format(self.title, self.media_name, self.created_at)

    @property
    def uris(self):
        if self.remote:
            ap_id = self.id
        else:
            ap_id = uri("photo", self.person.username, self.id)
        return URIs(id=ap_id,
                    media=uri("media", self.media_name),
                    preview=uri("preview", self.media_name)
                    )

    def to_activitystream(self):
        json = {
            "type": "image",
            "id": self.uris.id,
            "description": self.description,
            "url": self.uris.media,
            "preview": self.uris.preview,
            "content": self.message,
        }

        return data

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
        return model_to_dict(self, exclude=self._BaseModel__exclude(), extra_attrs=["albums"])

    def json(self):
        return json.dumps(self.to_model(), default=str)
