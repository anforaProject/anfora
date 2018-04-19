import datetime
import uuid
import binascii
import os

from peewee import *
from playhouse.shortcuts import model_to_dict

from models.base import BaseModel
from activityPub.helpers import (uri, URI)

class User(BaseModel):

    name = CharField(null=True)
    username = CharField(unique=True)
    password = CharField()
    admin = BooleanField(default=False)
    created_at =  DateTimeField(default=datetime.datetime.now)
    disabled = BooleanField(default=False)
    moderator = BooleanField(default=False)
    confirmed = BooleanField(default=False)
    email = CharField(unique=True)
    confirmation_sent_at = DateTimeField()
    last_sign_in_at = IntegerField()
    remote = BooleanField(default=False)

    @property
    def uris(self):
        if self.remote:
            return URIs(id=self.id)

        return URIs(
            id=uri("person", self.username),
            following=uri("following", self.username),
            followers=uri("followers", self.username),
            outbox=uri("outbox", self.username),
            inbox=uri("inbox", self.username),
        )


    def to_activitystream(self):
        json = {
            "type": "Person",
            "id": self.uris.id,
            "name": self.name,
            "preferredUsername": self.username
        }

        if not self.remote:
            json.update({
                "following": self.uris.following,
                "followers": self.uris.followers,
                "outbox": self.uris.outbox,
                "inbox": self.uris.inbox,
            })
