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
from urls import (uri, URIs)


class User(BaseModel):
    ap_id = CharField(null=True)
    name = CharField(null=True) # Display name
    username = CharField(unique=True) # actual username
    password = CharField() 
    admin = BooleanField(default=False) # True if the user is admin
    created_at =  DateTimeField(default=datetime.datetime.now) 
    disabled = BooleanField(default=False) # True if the user is disabled in the server
    confirmed = BooleanField(default=False) # The user has confirmed the email
    email = CharField(unique=True, null=True) # User's email
    confirmation_sent_at = DateTimeField(null=True) # Moment when the confirmation email was sent
    last_sign_in_at = IntegerField(null=True) # Last time the user signed in
    remote = BooleanField(default=False) # The user is a remote user
    private = BooleanField(default=False) # The account has limited access
    private_key = TextField(null=True) # Private key used to sign AP actions
    public_key = TextField() # Public key
    description = TextField(default="") # Description of the profile
    is_bot = BooleanField(default=False) # True if the account is a bot
    avatar_file = CharField(default="default.jpg")
    
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
            atom=uri("atom", {"username": self.username}),
            avatar=self.avatar,
            featured=uri("featured", {"username": self.username}),
        )



    def to_json(self):
        json = {
            'id': self.id,
            'username': self.username,
            'display_name': self.name,
            'locked': self.private,
            'created_at':self.created_at,
            'followers_count': self.followers().count(),
            'following_count': self.following().count(),
            'statuses_count': self.statuses().count(),
            'note':self.description,
            'url': None,
            'avatar': self.avatar,
            'moved': None,
            'fields':[],
            'bot': self.is_bot,
            'publicKey':{
                'id': self.uris.id + '#main-key',
                'owner': self.uris.id,
                'publicKeyPem': self.public_key
            }
        }

        if self.remote:
            json.update({
                'acct':self.ap_id
            })

        else:
            json.update({
                'acct': self.username
            })

        return json

    def to_model(self):
        return self.to_json()

    def to_activitystream(self):
        json = {
            "type": "Person",
            "id": self.uris.id,
            "name": self.name,
            "preferredUsername": self.username,
        }

        if not self.remote:
            json.update({
                "following": self.uris.following,
                "followers": self.uris.followers,
                "outbox": self.uris.outbox,
                "inbox": self.uris.inbox,
                "publicKey": self.public_key,
                "summary": self.description,
                "manuallyApprovesFollowers": self.private,
                "featured": self.uris.featured
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

    @property
    def avatar(self):
        return uri("profile_image", {"name": self.avatar_file})

    def followers(self):
        from models.followers import FollowerRelation

        return (User
                .select()
                .join(FollowerRelation, on=FollowerRelation.user)
                .where(FollowerRelation.follows == self)
                .order_by(User.username))

    def statuses(self):
        from models.photo import Photo
        return self.photos.order_by(Photo.id.desc())

    def following(self):
        from models.followers import FollowerRelation

        return (User
                .select()
                .join(FollowerRelation, on=FollowerRelation.follows)
                .where(FollowerRelation.user == self)
                .order_by(FollowerRelation.created_at.desc()))

    def is_following(self, user):
        from models.followers import FollowerRelation

        return (FollowerRelation
                .select()
                .where(
                    (FollowerRelation.user == self) &
                    (FollowerRelation.follows == user))
                .exists())

    def liked(self):
        return self.liked_posts
