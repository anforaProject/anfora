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
    title = CharField()
    media_name = CharField(unique=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    media_type = IntegerField()
    public = BooleanField(default=True)
    user = ForeignKeyField(User, backref='photos')
    text = CharField(null=True)
    sensitive = BooleanField(default=False)

    def __str__(self):
        return "{} - {} - {}".format(self.title, self.media_name, self.created_at)

    @property
    def uris(self):
        if self.remote:
            ap_id = self.id
        else:
            ap_id = uri("photo", self.person.username, self.id)
        return URIs(id=ap_id)

    def to_activitystream(self):
        payload = self.payload.decode("utf-8")
        data = json.loads(payload)
        data.update({
            "id": self.uris.id
        })
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
