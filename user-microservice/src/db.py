import datetime
import uuid
import binascii
import os
import io
import logging

import Crypto
from PIL import Image

from Crypto.PublicKey import RSA
from Crypto import Random

from tortoise.models import Model
from tortoise import fields

from urls import (uri, URIs)

#Generate pixeled avatars
from avatar_gen.pixel_avatar import PixelAvatar
from hashids import Hashids

from keys import import_keys

from utils import load_config

config = load_config()

BASE_URL = config['base_url']
MEDIA_FOLDER = config['media_folder']
salt_code = config['salt_code']

log = logging.getLogger(__name__)

class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(25,unique=True)
    password = fields.CharField(256,unique=True)
    created_at = fields.DatetimeField(auto_now_add = True)
    is_bot = fields.BooleanField(default=False) # True if the account is a bot
    is_admin = fields.BooleanField(default=False) # True if the user is admin
    email = fields.CharField(256, unique=True, null=False) # User's email
    confirmed = fields.BooleanField(default=False) # The user has confirmed the email
    confirmation_sent_at = fields.DatetimeField(auto_now_add = True) # Moment when the confirmation email was sent
    last_sign_in_at = fields.DatetimeField(auto_now_add = True) # Last time the user signed in epoch since
    is_private = fields.BooleanField(default=False) # The account has limited access

    def __repr__(self):
        return self.username

class UserProfile(Model):

    id = fields.IntField(pk=True)
    ap_id = fields.CharField(256,unique=True, null=True)
    name = fields.CharField(64, unique=False, null=True) # Display name
    disabled = fields.BooleanField(default=False) # True if the user is disabled in the server
    is_remote = fields.BooleanField(default=False) # The user is a remote user
    private_key = fields.TextField(null=True) # Private key used to sign AP actions
    public_key = fields.TextField(null=True) # Public key
    description = fields.CharField(512,unique=True, default="") # Description of the profile
    avatar_file = fields.CharField(512,unique=True, default="")
    following_count = fields.IntField(default=0)
    followers_count = fields.IntField(default=0)
    statuses_count = fields.IntField(default=0)
    user = fields.ForeignKeyField('models.User', on_delete='CASCADE')
    public_inbox = fields.CharField(256, null=True)

    followers = fields.ManyToManyField('models.UserProfile', related_name="following")

    @property
    async def username(self):
        await self.fetch_related('user')
        return self.user.username

    @property
    async def is_private(self):
        await self.fetch_related('user')
        return self.user.is_private

    @property
    async def uris(self):
        if self.is_remote:
            return URIs(
                id=self.ap_id,
                inbox=f'{self.ap_id}/inbox',
                outbox=f'{self.ap_id}/inbox',
                following=f'{self.ap_id}/following',
                followers=f'{self.ap_id}/followers',
            )

        return URIs(
            id=uri("user", {"username": await self.username}),
            following=uri("following", {"username": await self.username}),
            followers=uri("followers", {"username": await self.username}),
            outbox=uri("outbox", {"username": await self.username}),
            inbox=uri("inbox", {"username": await self.username}),
            atom=uri("atom", {"id": self.id}),
            featured=uri("featured", {"username": await self.username}),
            avatar=uri('profile_image', {"name": self.avatar_file}),
            client=uri('user_client',{'username': await self.username})
        )



    async def to_json(self):
        await self.fetch_related('user')
        json = {
            'id': self.id,
            'username': await self.username,
            'name': self.name,
            'display_name': self.name,
            'locked': await self.is_private,
            'created_at': str(self.user.created_at),
            'followers_count': self.followers_count,
            'following_count': self.following_count,
            'statuses_count': self.statuses_count,
            'note':self.description,
            'url': None,
            'avatar': self.avatar,
            'moved': None,
            'fields':[],
            'bot': self.user.is_bot,
        }

        if self.is_remote:
            json.update({
                'acct':self.ap_id
            })

        else:
            json.update({
                'acct': await self.username
            })

        return json


    async def to_activitystream(self):
        uris = await self.uris

        json_dict = {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
                "https://w3id.org/security/v1",
            ],
            "type": "Person",
            "id": uris.id,
            "name": self.name,
            "preferredUsername": await self.username,
        }

        if not self.is_remote:
            json_dict.update({
                "following": uris.following,
                "followers": uris.followers,
                "outbox": uris.outbox,
                "inbox": uris.inbox,
                "publicKey": {
                    'publicKeyPem': import_keys()["actorKeys"]["publicKey"],
                    'id': f'{BASE_URL}/users/{await self.username}#main-key',
                    'owner': f'{BASE_URL}/users/{await self.username}'
                },
                "summary": self.description,
                "manuallyApprovesFollowers": await self.is_private,
                "featured": uris.featured,
                "endpoints": {
                    "sharedInbox": uri('sharedInbox')
                }
            })

        return json_dict

    def _create_avatar_id(self):
        hashid = Hashids(salt=salt_code, min_length=6)

        possible_id = self.id + int((datetime.datetime.now() - datetime.datetime(1970,1,1)).total_seconds())
        return hashid.encode(possible_id)

    def _crate_avatar_file(self, image):
        """
        image - A byte array with the image
        """

        filename = self._create_avatar_id()
        image = io.BytesIO(image)
        im = Image.open(image)
        im = im.convert('RGB')
        im.thumbnail((400, 400), Image.ANTIALIAS)
        file_path = os.path.join(MEDIA_FOLDER, 'avatars', filename + '.jpeg')
        im.save(file_path, 'jpeg')

        return f'{filename}.jpeg'

    def update_avatar(self, image):
        return self._crate_avatar_file(image)

    @property
    def avatar(self):
        return uri("profile_image", {"name": self.avatar_file})


    async def is_following(self, user):
        return len(await self.followers.filter(pk=user.pk)) == 1

    async def follow(self, target):


        """
        The current user follows the target account.

        target: An instance of UserProfile
        """

        await self.followers.add(target)

        

    async def unfollow(self, target, valid=False):


        """
        The current user follows the target account.

        target: An instance of UserProfile
        """

        await self.followers.add(target)

