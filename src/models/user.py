import datetime
import uuid
import binascii
import os

from peewee import *
from playhouse.shortcuts import model_to_dict

from models.base import BaseModel
from activityPub.helpers import (uri, URIs)

class User(BaseModel):
    ap_id = CharField(null=True)
    name = CharField(null=True)
    username = CharField(unique=True)
    password = CharField()
    admin = BooleanField(default=False)
    created_at =  DateTimeField(default=datetime.datetime.now)
    disabled = BooleanField(default=False)
    moderator = BooleanField(default=False)
    confirmed = BooleanField(default=False)
    email = CharField(unique=True, null=True)
    confirmation_sent_at = DateTimeField(null=True)
    last_sign_in_at = IntegerField(null=True)
    remote = BooleanField(default=False)

    @property
    def uris(self):
        if self.remote:
            return URIs(id=self.ap_id)

        return URIs(
            id=uri("user", {"username":self.username}),
            following=uri("following", {"username":self.username}),
            followers=uri("followers", {"username":self.username}),
            outbox=uri("outbox", {"username":self.username}),
            inbox=uri("inbox", {"username":self.username}),
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

        return json

    def save(self,*args, **kwargs):
        if not self.remote:
            self.ap_id = uri("user", {"username":self.username})
        return super(User, self).save(*args, **kwargs)
