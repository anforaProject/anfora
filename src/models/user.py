import datetime
import uuid
import binascii
import os

import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random

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
    private_key = TextField()
    public_key = TextField()

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

        if not self.private_key:
            #Create a pair public/private key to sign messages
            random_generator = Random.new().read
            key = RSA.generate(2048, random_generator)
            self.public_key = key.publickey().exportKey().decode('utf-8')
            self.private_key = key.exportKey().decode('utf-8')

        return super(User, self).save(*args, **kwargs)

    def followers(self):
        from models.followers import FollowerRelation

        return (User
                .select()
                .join(FollowerRelation, on=FollowerRelation.user)
                .where(FollowerRelation.follows == self)
                .order_by(User.username))

    def following(self):
        from models.followers import FollowerRelation

        return (User
                .select()
                .join(FollowerRelation, on=FollowerRelation.follows)
                .where(FollowerRelation.user == self)
                .order_by(User.username))

    def is_following(self, user):
        from models.followers import FollowerRelation

        return (FollowerRelation
                .select()
                .where(
                    (FollowerRelation.user == self) &
                    (FollowerRelation.follows == user))
                .exists())
