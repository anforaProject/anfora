import datetime
import uuid
import binascii
import os
import io

import Crypto
from PIL import Image

from Crypto.PublicKey import RSA
from Crypto import Random

from peewee import *
from playhouse.shortcuts import model_to_dict

from models.base import BaseModel
from urls import (uri, URIs)

#Generate pixeled avatars
from avatar_gen.pixel_avatar import PixelAvatar
from hashids import Hashids
from settings import (MEDIA_FOLDER, salt_code, icon)



class UserProfile(BaseModel):
    ap_id = CharField(unique=True)
    name = CharField(null=True) # Display name
    username = CharField() # actual username
    password = CharField() 
    admin = BooleanField(default=False) # True if the user is admin
    created_at =  DateTimeField(default=datetime.datetime.now) 
    disabled = BooleanField(default=False) # True if the user is disabled in the server
    confirmed = BooleanField(default=False) # The user has confirmed the email
    email = CharField(unique=True, null=True) # User's email
    confirmation_sent_at = DateTimeField(null=True) # Moment when the confirmation email was sent
    last_sign_in_at = IntegerField(null=True) # Last time the user signed in epoch since
    remote = BooleanField(default=False) # The user is a remote user
    private = BooleanField(default=False) # The account has limited access
    private_key = TextField(null=True) # Private key used to sign AP actions
    public_key = TextField() # Public key
    description = TextField(default="") # Description of the profile
    is_bot = BooleanField(default=False) # True if the account is a bot
    avatar_file = CharField(null=True)
    following_count = IntegerField(default=0)
    followers_count = IntegerField(default=0)
    statuses_count = IntegerField(default=0)

    
    @property
    def uris(self):
        if self.remote:
            return URIs(
                id=self.ap_id,
                inbox=f'{self.ap_id}/inbox',
                outbox=f'{self.ap_id}/inbox',
                following=f'{self.ap_id}/following',
                followers=f'{self.ap_id}/followers'
            )

        return URIs(
            id=uri("user", {"username":self.username}),
            following=uri("following", {"username":self.username}),
            followers=uri("followers", {"username":self.username}),
            outbox=uri("outbox", {"username":self.username}),
            inbox=uri("inbox", {"username":self.username}),
            atom=uri("atom", {"id": self.id}),
            featured=uri("featured", {"username": self.username}),
            avatar=uri('profile_image', {"name": self.avatar_file})
        )



    def to_json(self):
        json = {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'display_name': self.name,
            'locked': self.private,
            'created_at':self.created_at,
            'followers_count': self.followers_count,
            'following_count': self.following_count,
            'statuses_count': self.statuses_count,
            'note':self.description,
            'url': None,
            'avatar': self.avatar,
            'moved': None,
            'fields':[],
            'bot': self.is_bot,
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
                "publicKey": {
                    'publicKeyPem': self.public_key,
                    'id': f'{self.ap_id}#main-key',
                    'owner': self.ap_id
                },
                "summary": self.description,
                "manuallyApprovesFollowers": self.private,
                "featured": self.uris.featured
            })

        return json

    def _create_avatar_id(self):
        hashid = Hashids(salt=salt_code, min_length=6)

        try:
            possible_id = UserProfile.select().order_by(UserProfile.id.desc()).get().id
        except:
            possible_id = 0

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
        file_path = os.path.join(MEDIA_FOLDER, icon, filename + '.jpeg')
        im.save(file_path, 'jpeg')

        return f'{filename}.jpeg'

    def save(self,*args, **kwargs):
        if not self.remote:
            self.ap_id = uri("user", {"username":self.username})

        if not self.private_key and not self.public_key:
            #Create a pair public/private key to sign messages
            random_generator = Random.new().read
            key = RSA.generate(2048, random_generator)
            self.public_key = key.publickey().exportKey().decode('utf-8')
            self.private_key = key.exportKey().decode('utf-8')

        if not self.avatar_file:
            pixel_avatar = PixelAvatar(rows=10, columns=10)
            image_byte_array = pixel_avatar.get_image(size=400, string=self.ap_id, filetype="jpeg")
            
            self.avatar_file = self._crate_avatar_file(image_byte_array)

        return super(UserProfile, self).save(*args, **kwargs)

    def update_avatar(self, image):
        return self._crate_avatar_file(image)
        

    @property
    def avatar(self):
        return uri("profile_image", {"name": self.avatar_file})

    def followers(self):
        from models.followers import FollowerRelation

        return (UserProfile
                .select()
                .join(FollowerRelation, on=FollowerRelation.user)
                .where(FollowerRelation.follows == self)
                .order_by(UserProfile.username))

    def timeline(self):
        from models.status import Status
        return self.statuses.order_by(Status.id.desc())

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

    def follow(self, target, valid=False):


        """
        The current user follows the target account. 
        
        target: An instance of User
        valid: Boolean to force a valid Follow. This means that the user
                doesn't have to accept the follow
        """

        from models.followers import FollowerRelation

        FollowerRelation.create(user = self, follows =target, valid=valid)
        followers_increment = UserProfile.update({UserProfile.followers_count: UserProfile.followers_count + 1}).where(UserProfile.id == target.id)
        following_increment = UserProfile.update({UserProfile.following_count: UserProfile.following_count + 1}).where(UserProfile.id == self.id)

        following_increment.execute()
        followers_increment.execute()
